import os
from uuid import uuid4, UUID

from eventsourcing.application import Application
from eventsourcing.persistence import Transcoder
from typing_extensions import override

from project_management.domain_model import Board
from project_management.transcoders import CardTranscoding, ColumnTranscoding
from project_management.undo_redo.undo_redo_state_manager import UndoRedoStateManager


class ProjectManagementApp(Application):
    is_snapshotting_enabled = True

    def __init__(self):
        super().__init__()
        self.undo_redo_state_manager = UndoRedoStateManager(self)

    @override
    def register_transcodings(self, transcoder: Transcoder):
        super().register_transcodings(transcoder)
        transcoder.register(CardTranscoding())
        transcoder.register(ColumnTranscoding())

    def create_board(self) -> UUID:
        board = Board()
        undo_redo_tracker_id = self.undo_redo_state_manager.create_undo_redo_tracker(board.id)
        board.set_undo_redo_tracker(undo_redo_tracker_id)
        self.save(board)
        return board.id

    def edit_board_title(self, board_id: UUID, title: str):
        board = self.repository.get(board_id)
        self.undo_redo_state_manager.commit_undo_state(board)
        board.edit_board_title(title)
        self.save(board)
        self.undo_redo_state_manager.increment_version_cursor(board_id)

    def edit_column_title(self, board_id: UUID, column_id: UUID, title: str):
        board = self.repository.get(board_id)
        self.undo_redo_state_manager.commit_undo_state(board)
        board.edit_column_title(column_id, title)
        self.save(board)
        self.undo_redo_state_manager.increment_version_cursor(board_id)

    def edit_card_title(self, board_id: UUID, column_id: UUID, card_id: UUID, title: str):
        board = self.repository.get(board_id)
        self.undo_redo_state_manager.commit_undo_state(board)
        board.edit_card_title(column_id, card_id, title)
        self.save(board)
        self.undo_redo_state_manager.increment_version_cursor(board_id)

    def edit_card_content(self, board_id: UUID, column_id: UUID, card_id: UUID, content: str):
        board = self.repository.get(board_id)
        self.undo_redo_state_manager.commit_undo_state(board)
        board.edit_card_content(column_id, card_id, content)
        self.save(board)
        self.undo_redo_state_manager.increment_version_cursor(board_id)

    def add_column(self, board_id: UUID) -> UUID:
        board = self.repository.get(board_id)
        self.undo_redo_state_manager.commit_undo_state(board)
        column_id = uuid4()
        board.add_column(column_id)
        self.save(board)
        self.undo_redo_state_manager.increment_version_cursor(board_id)
        return column_id

    def remove_column(self, board_id: UUID, column_id: UUID):
        board = self.repository.get(board_id)
        self.undo_redo_state_manager.commit_undo_state(board)
        board.remove_column(column_id)
        self.save(board)
        self.undo_redo_state_manager.increment_version_cursor(board_id)

    def move_column(self, board_id: UUID, column_id: UUID, new_index: int):
        board = self.repository.get(board_id)
        self.undo_redo_state_manager.commit_undo_state(board)
        board.move_column(column_id, new_index)
        self.save(board)
        self.undo_redo_state_manager.increment_version_cursor(board_id)

    def add_card(self, board_id: UUID, column_id: UUID) -> UUID:
        board = self.repository.get(board_id)
        self.undo_redo_state_manager.commit_undo_state(board)
        card_id = uuid4()
        board.add_card(column_id, card_id)
        self.save(board)
        self.undo_redo_state_manager.increment_version_cursor(board_id)
        return card_id

    def remove_card(self, board_id: UUID, column_id: UUID, card_id: UUID):
        board = self.repository.get(board_id)
        self.undo_redo_state_manager.commit_undo_state(board)
        board.remove_card(column_id, card_id)
        self.save(board)
        self.undo_redo_state_manager.increment_version_cursor(board_id)

    def move_card(self, board_id: UUID, from_column_id: UUID, to_column_id: UUID, card_id: UUID, new_index: int):
        board = self.repository.get(board_id)
        self.undo_redo_state_manager.commit_undo_state(board)

        if from_column_id != to_column_id:
            card = board.get_card(from_column_id, card_id)
            board.remove_card(from_column_id, card_id)
            self.undo_redo_state_manager.increment_version_cursor(board_id)

            board.add_card(to_column_id, card.id, card.title, card.content)
            self.undo_redo_state_manager.increment_version_cursor(board_id)

            self.save(board)

        board.move_card(to_column_id, card_id, new_index)
        self.undo_redo_state_manager.increment_version_cursor(board_id)
        self.save(board)

    def undo(self, board_id: UUID):
        self.undo_redo_state_manager.undo(board_id)

    def redo(self, board_id: UUID):
        self.undo_redo_state_manager.redo(board_id)

    def board_as_dict(self, board_id: UUID) -> dict:
        active_version = self.undo_redo_state_manager.get_version_cursor(board_id)
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
