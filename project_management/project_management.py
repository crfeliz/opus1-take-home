import os
from uuid import uuid4, UUID
import sqlite3
from typing import Any

from bidict import bidict
from eventsourcing.application import Application
from eventsourcing.domain import Aggregate, event
from eventsourcing.persistence import Transcoding, Transcoder
from typing_extensions import override


def find_item_by_id(collection, item_id):
    return next((item for item in collection if item.id == item_id), None)


def edit_item_by_id(collection, item_id, f):
    f(find_item_by_id(collection, item_id))


def remove_item_by_id(collection, item_id):
    item_to_remove = find_item_by_id(collection, item_id)
    if item_to_remove is None:
        raise ValueError(f"Item with ID {item_id} not found in collection {collection}")
    collection.remove(item_to_remove)


def debug_print_ids(collection):
    print("----------")
    print(list(map(lambda v: v.id, collection)))
    print("----------")

def with_item_moved_by_id(collection, item_id, new_index):
    item_index = next((i for i, item in enumerate(collection) if item.id == item_id), None)
    if item_index is None:
        raise ValueError(f"Item {item_id} not found in {collection}")

    item = collection[item_index]
    collection[item_index] = None
    collection.insert(new_index, item)
    return list(filter(None, collection))


class Card:

    def __init__(self, card_id):
        self.id = card_id
        self.title = ""
        self.content = ""

class CardTranscoding(Transcoding):
    type = Card
    name = "card_dict"
    def encode(self, obj: Any) -> Any:
        return {
            "id": obj.id,
            "title": obj.title,
            "content": obj.content
        }

    def decode(self, data: Any) -> Any:
        # Create a Card from a dict.
        card = Card(data["id"])
        card.title = data.get("title", "")
        card.content = data.get("content", "")
        return card

class Column:

    def __init__(self, column_id):
        self.id = column_id
        self.title = ""
        self.cards = []

class ColumnTranscoding(Transcoding):
    type = Column
    name = "column_dict"
    def encode(self, obj: Any) -> Any:
        return {
            "id": obj.id,
            "title": obj.title,
            "cards": obj.cards
        }

    def decode(self, data: Any) -> Any:
        column = Column(data["id"])
        column.title = data.get("title", "")
        column.cards = data.get("cards", [])
        return column

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
        print("active_version_before", self.get_version_cursor())
        print("undo_commits", self._undo_commits)
        self._version_cursor = max(self._min_version, self.get_version_cursor() - 1)
        reference_version = self._undo_commits.get(self.get_version_cursor())
        if reference_version is not None and reference_version < self.get_version_cursor():
            self._version_cursor = reference_version
        print("active_version_after", self.get_version_cursor())

    def redo(self, maximum_version):
        print("active_version_before", self.get_version_cursor())
        print("undo_commits", self._undo_commits)
        commit_version = self._undo_commits.get(self.get_version_cursor())
        if commit_version is not None and commit_version > self.get_version_cursor():
            self._version_cursor = commit_version
        self._version_cursor = min(maximum_version, self.get_version_cursor() + 1)
        print("active_version_after", self.get_version_cursor())

    def commit(self, commit_version, reference_version):
        reference_version = min(self._undo_commits.get(reference_version, reference_version), reference_version)
        commit_version = max(self._undo_commits.get(commit_version, commit_version), commit_version)
        self._undo_commits.forceput(commit_version, reference_version)
        self._undo_commits.forceput(reference_version, commit_version)
        self.clean_undo_commits()
        self._version_cursor = commit_version
        print("undo_commits", self._undo_commits)

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

class BoardUndoTracker(Aggregate):

    @event("UNDO_TRACKER_CREATED")
    def __init__(self, board_id):
        self.board_id = board_id
        self.strategy = UndoRedoStrategy(min_version=2)

    @event("INCR_VERSION_CURSOR")
    def increment_version_cursor(self):
        self.strategy.increment_version_cursor()

    @event("UNDO")
    def undo(self):
        self.strategy.undo()

    @event("REDO")
    def redo(self, maximum_version):
        self.strategy.redo(maximum_version)

    @event("COMMIT")
    def commit(self, commit_version, reference_version):
        self.strategy.commit(commit_version, reference_version)

    def get_active_version(self):
        return self.strategy.get_version_cursor()


class Board(Aggregate):
    @event("BOARD_CREATED")
    def __init__(self):
        self.title = ""
        self.columns = []
        self.undo_jump_offset = 0
        self.undo_tracker_id = None

    @event("UNDO_TRACKER_LINKED")
    def set_undo_tracker(self, undo_tracker_id):
        self.undo_tracker_id = undo_tracker_id

    @event("BOARD_TITLE_EDITED")
    def edit_board_title(self, title):
        self.title = title

    @event("COLUMN_ADDED")
    def add_column(self, column_id):
        column = Column(column_id)
        self.columns.append(column)

    @event("COLUMN_REMOVED")
    def remove_column(self, column_id):
        remove_item_by_id(self.columns, column_id)

    @event("COLUMN_MOVED")
    def move_column(self, column_id, new_index):
        # this operation creates a new array
        self.columns = with_item_moved_by_id(self.columns, column_id, new_index)

    @event("COLUMN_TITLE_EDITED")
    def edit_column_title(self, column_id, title):
        edit_item_by_id(self.columns, column_id, lambda column: setattr(column, 'title', title))

    @event("CARD_TITLE_EDITED")
    def edit_card_title(self, column_id, card_id, title):
        column = find_item_by_id(self.columns, column_id)
        edit_item_by_id(column.cards, card_id, lambda card: setattr(card, 'title', title))

    @event("CARD_CONTENT_EDITED")
    def edit_card_content(self, column_id, card_id, content):
        column = find_item_by_id(self.columns, column_id)
        edit_item_by_id(column.cards, card_id, lambda card: setattr(card, 'content', content))

    @event("CARD_ADDED")
    def add_card(self, column_id, card_id, title=None, content=None):
        card = Card(card_id)
        if title is not None:
            card.title = title
        if content is not None:
            card.content = content

        column = find_item_by_id(self.columns, column_id)
        column.cards.append(card)

    @event("CARD_REMOVED")
    def remove_card(self, column_id, card_id):
        column = find_item_by_id(self.columns, column_id)
        remove_item_by_id(column.cards, card_id)

    @event("CARD_MOVED")
    def move_card(self, column_id, card_id, new_index):
        column = find_item_by_id(self.columns, column_id)
        column.cards = with_item_moved_by_id(column.cards, card_id, new_index)

    def get_card(self, column_id, card_id):
        column = find_item_by_id(self.columns, column_id)
        card = find_item_by_id(column.cards, card_id)
        if card is None:
            raise ValueError(f"Card {card_id} not found in column {column_id}")
        return card

    @event("COMMIT_UNDO_STATE")
    def commit_undo_state(self, title, columns):
        self.title = title
        self.columns = columns


class UndoStateHandler:
    def __init__(self, app):
        self.app: Application = app
        self.board_id_to_undo_tracker_id = {}

    def commit_undo_state(self, board: Board):
        undo_tracker = self._get_undo_tracker(board.id)
        active_version = undo_tracker.get_active_version()
        if active_version != board.version:
            undone_board: Board = self.app.repository.get(board.id, version=active_version)
            board.commit_undo_state(undone_board.title, undone_board.columns)
            self.app.save(board)
            undo_tracker.commit(board.version, undone_board.version)
            self.app.save(undo_tracker)


    def increment_version_cursor(self, board_id: UUID):
        undo_tracker = self._get_undo_tracker(board_id)
        undo_tracker.increment_version_cursor()
        self.app.save(undo_tracker)


    def undo(self, board_id: UUID):
        undo_tracker = self._get_undo_tracker(board_id)
        undo_tracker.undo()
        self.app.save(undo_tracker)

    def redo(self, board_id: UUID):
        latest_version = self._get_latest_board_version(board_id)
        undo_tracker = self._get_undo_tracker(board_id)
        undo_tracker.redo(maximum_version=latest_version)
        self.app.save(undo_tracker)

    def get_active_version(self, board_id: UUID):
        undo_tracker: BoardUndoTracker = self._get_undo_tracker(board_id)
        return undo_tracker.get_active_version()

    def _get_undo_tracker(self, board_id) -> BoardUndoTracker:
        if board_id not in self.board_id_to_undo_tracker_id:
            board = self.app.repository.get(board_id)
            self.board_id_to_undo_tracker_id[board_id] = board.undo_tracker_id
        undo_tracker_uuid = self.board_id_to_undo_tracker_id[board_id]
        return self.app.repository.get(undo_tracker_uuid)

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


class ProjectManagementApp(Application):

    def __init__(self):
        super().__init__()
        self.undo_state_handler = UndoStateHandler(self)

    @override
    def register_transcodings(self, transcoder: Transcoder):
        super().register_transcodings(transcoder)
        transcoder.register(CardTranscoding())
        transcoder.register(ColumnTranscoding())


    def create_board(self) -> UUID:
        board = Board()
        undo_tracker = BoardUndoTracker(board.id)
        board.set_undo_tracker(undo_tracker.id)
        self.save(board)
        self.save(undo_tracker)
        return board.id

    def edit_board_title(self, board_id: UUID, title: str):
        board = self.repository.get(board_id)
        self.undo_state_handler.commit_undo_state(board)
        board.edit_board_title(title)
        self.save(board)
        self.undo_state_handler.increment_version_cursor(board_id)

    def edit_column_title(self, board_id: UUID, column_id: UUID, title: str):
        board = self.repository.get(board_id)
        self.undo_state_handler.commit_undo_state(board)
        board.edit_column_title(column_id, title)
        self.save(board)
        self.undo_state_handler.increment_version_cursor(board_id)

    def edit_card_title(self, board_id: UUID, column_id: UUID, card_id: UUID, title: str):
        board = self.repository.get(board_id)
        self.undo_state_handler.commit_undo_state(board)
        board.edit_card_title(column_id, card_id, title)
        self.save(board)
        self.undo_state_handler.increment_version_cursor(board_id)

    def edit_card_content(self, board_id: UUID, column_id: UUID, card_id: UUID, content: str):
        board = self.repository.get(board_id)
        self.undo_state_handler.commit_undo_state(board)
        board.edit_card_content(column_id, card_id, content)
        self.save(board)
        self.undo_state_handler.increment_version_cursor(board_id)

    def add_column(self, board_id: UUID) -> UUID:
        board = self.repository.get(board_id)
        self.undo_state_handler.commit_undo_state(board)
        column_id = uuid4()
        board.add_column(column_id)
        self.save(board)
        self.undo_state_handler.increment_version_cursor(board_id)
        return column_id

    def remove_column(self, board_id: UUID, column_id: UUID):
        board = self.repository.get(board_id)
        self.undo_state_handler.commit_undo_state(board)
        board.remove_column(column_id)
        self.save(board)
        self.undo_state_handler.increment_version_cursor(board_id)


    def move_column(self, board_id: UUID, column_id: UUID, new_index: int):
        board = self.repository.get(board_id)
        self.undo_state_handler.commit_undo_state(board)
        board.move_column(column_id, new_index)
        self.save(board)
        self.undo_state_handler.increment_version_cursor(board_id)

    def add_card(self, board_id: UUID, column_id: UUID) -> UUID:
        board = self.repository.get(board_id)
        self.undo_state_handler.commit_undo_state(board)
        card_id = uuid4()
        board.add_card(column_id, card_id)
        self.save(board)
        self.undo_state_handler.increment_version_cursor(board_id)
        return card_id

    def remove_card(self, board_id: UUID, column_id: UUID, card_id: UUID):
        board = self.repository.get(board_id)
        self.undo_state_handler.commit_undo_state(board)
        board.remove_card(column_id, card_id)
        self.save(board)
        self.undo_state_handler.increment_version_cursor(board_id)

    def move_card(self, board_id: UUID, from_column_id: UUID, to_column_id: UUID, card_id: UUID, new_index: int):

        board = self.repository.get(board_id)
        self.undo_state_handler.commit_undo_state(board)

        if from_column_id != to_column_id:
            card = board.get_card(from_column_id, card_id)
            board.remove_card(from_column_id, card_id)
            board.add_card(to_column_id, card.id, card.title, card.content)
            self.save(board)
            self.undo_state_handler.increment_version_cursor(board_id)
            self.undo_state_handler.increment_version_cursor(board_id)

        board.move_card(to_column_id, card_id, new_index)
        self.save(board)
        self.undo_state_handler.increment_version_cursor(board_id)

    def undo(self, board_id: UUID):
        self.undo_state_handler.undo(board_id)

    def redo(self, board_id: UUID):
        self.undo_state_handler.redo(board_id)

    def board_as_dict(self, board_id: UUID) -> dict:
        active_version = self.undo_state_handler.get_active_version(board_id)
        print("rendering version: ", active_version)
        board = self.repository.get(board_id, version=active_version)

        return {
            "board": {
                "id": str(board_id),
                "title": board.title,
                "columns": [
                    {
                        "id": str(column.id),
                        "title": column.title,
                        "cards": [
                            {
                                "id": str(card.id),
                                "title": card.title,
                                "content": card.content
                            }
                            for card in column.cards
                        ],
                    }
                    for column in board.columns
                ],
                "version": board.version
            }
        }


os.environ['PERSISTENCE_MODULE'] = 'eventsourcing.sqlite'
os.environ['SQLITE_DBNAME'] = 'events.db'