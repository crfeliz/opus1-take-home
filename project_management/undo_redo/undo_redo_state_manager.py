import sqlite3
from uuid import UUID

from bidict import bidict
from eventsourcing.application import Application
from eventsourcing.domain import Aggregate, event

from project_management.domain_model import Board

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class UndoRedoStrategy:

    def __init__(self, min_version):
        self._min_version = min_version
        self._version_cursor = min_version
        self._undo_commits = bidict()

    def get_version_cursor(self):
        return self._version_cursor

    def increment_version_cursor(self):
        self._version_cursor += 1

    def undo(self):
        self._version_cursor = max(self._min_version, self.get_version_cursor() - 1)
        reference_version = self._undo_commits.get(self.get_version_cursor())
        if reference_version is not None and reference_version < self.get_version_cursor():
            self._version_cursor = reference_version

    def redo(self, maximum_version):
        commit_version = self._undo_commits.get(self.get_version_cursor())
        if commit_version is not None and commit_version > self.get_version_cursor():
            self._version_cursor = commit_version
        self._version_cursor = min(maximum_version, self.get_version_cursor() + 1)

    def commit(self, commit_version, reference_version):
        reference_version = min(self._undo_commits.get(reference_version, reference_version), reference_version)
        commit_version = max(self._undo_commits.get(commit_version, commit_version), commit_version)
        self._undo_commits.forceput(commit_version, reference_version)
        self._undo_commits.forceput(reference_version, commit_version)
        self.clean_undo_commits()
        self._version_cursor = commit_version
        logging.debug("undo_commits", self._undo_commits)

    def clean_undo_commits(self):
        pairs = {(min(k, v), max(k, v)) for k, v in self._undo_commits.items()}

        # 2. Sort pairs by left endpoint ascending; if equal, by right endpoint descending.
        sorted_pairs = sorted(pairs, key=lambda sp: (sp[0], -sp[1]))

        # 3. Keep only pairs that are not completely contained within a previously kept (larger) range.
        kept = []
        for p in sorted_pairs:
            if any(q[0] <= p[0] and p[1] <= q[1] for q in kept):
                continue
            kept.append(p)

        # 4. Create a new bidict of the same type as bid and add the kept pairs in both directions.
        nb = {}
        for l, r in kept:
            nb[l] = r
            nb[r] = l
        self._undo_commits = bidict(nb)


class UndoRedoTracker(Aggregate):

    @event("TRACKER_CREATED")
    def __init__(self, board_id):
        logger.debug("TRACKER_CREATED")
        self.board_id = board_id
        self.strategy = UndoRedoStrategy(min_version=2)

    @event("INCR_VERSION_CURSOR")
    def increment_version_cursor(self):
        logger.debug("INCR_VERSION_CURSOR")
        self.strategy.increment_version_cursor()

    @event("UNDO")
    def undo(self):
        logger.debug("UNDO")
        self.strategy.undo()

    @event("REDO")
    def redo(self, maximum_version):
        logger.debug("REDO")
        self.strategy.redo(maximum_version)

    @event("COMMIT")
    def commit(self, commit_version, reference_version):
        logger.debug("COMMIT")
        self.strategy.commit(commit_version, reference_version)

    def get_version_cursor(self):
        return self.strategy.get_version_cursor()


class UndoRedoStateManager:
    def __init__(self, app):
        self.app: Application = app
        self.board_id_to_undo_redo_tracker_id = {}

    def create_undo_redo_tracker(self, board_id):
        undo_redo_tracker = UndoRedoTracker(board_id)
        self.app.save(undo_redo_tracker)
        return undo_redo_tracker.id

    def commit_undo_state(self, board: Board):
        undo_redo_tracker = self._get_undo_redo_tracker(board.id)
        version_cursor = undo_redo_tracker.get_version_cursor()
        if version_cursor != board.version:
            board.commit_undo_state()
            self.app.save(board)
            self._take_undo_commit_snapshot(board.id, version_cursor)
            undo_redo_tracker.commit(board.version, version_cursor)
            self.app.save(undo_redo_tracker)

    def increment_version_cursor(self, board_id: UUID):
        undo_redo_tracker = self._get_undo_redo_tracker(board_id)
        undo_redo_tracker.increment_version_cursor()
        self.app.save(undo_redo_tracker)

    def undo(self, board_id: UUID):
        undo_redo_tracker = self._get_undo_redo_tracker(board_id)
        undo_redo_tracker.undo()
        self.app.save(undo_redo_tracker)

    def redo(self, board_id: UUID):
        latest_version = self._get_latest_board_version(board_id)
        undo_redo_tracker = self._get_undo_redo_tracker(board_id)
        undo_redo_tracker.redo(maximum_version=latest_version)
        self.app.save(undo_redo_tracker)

    def get_version_cursor(self, board_id: UUID):
        undo_redo_tracker: UndoRedoTracker = self._get_undo_redo_tracker(board_id)
        return undo_redo_tracker.get_version_cursor()

    def _get_undo_redo_tracker(self, board_id) -> UndoRedoTracker:
        if board_id not in self.board_id_to_undo_redo_tracker_id:
            board = self.app.repository.get(board_id)
            self.board_id_to_undo_redo_tracker_id[board_id] = board.undo_redo_tracker_id
        undo_redo_tracker_uuid = self.board_id_to_undo_redo_tracker_id[board_id]
        return self.app.repository.get(undo_redo_tracker_uuid)

    def _take_undo_commit_snapshot(self, board_id: UUID, version: int) -> None:
        reference_board = self.app.repository.get(board_id, version=version)
        latest_board = self.app.repository.get(board_id)
        snapshot_class = getattr(type(reference_board), "Snapshot", self.app.snapshot_class)

        latest_board.title = reference_board.title
        latest_board.columns = reference_board.columns
        undo_commit_snapshot = snapshot_class.take(latest_board)
        self.app.snapshots.put([undo_commit_snapshot])

    @staticmethod
    def _get_latest_board_version(board_id: UUID):
        board_uuid = board_id.hex
        connection = sqlite3.connect("events.db")
        try:
            cursor = connection.cursor()
            query = """
                SELECT MAX(originator_version)
                FROM stored_events
                WHERE originator_id = ?
            """
            cursor.execute(query, (board_uuid,))
            row = cursor.fetchone()
        finally:
            connection.close()

        return row[0] if row[0] is not None else 0
