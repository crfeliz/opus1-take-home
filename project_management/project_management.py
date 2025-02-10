import os
import uuid
from functools import wraps
from eventsourcing.application import Application, Repository
from eventsourcing.domain import Aggregate, event


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
    debug_print_ids(collection)
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


class Column:
    def __init__(self, column_id):
        self.id = column_id
        self.title = ""
        self.cards = []


class Board(Aggregate):
    @event("BOARD_CREATED")
    def __init__(self):
        self.title = ""
        self.columns = []

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


class ProjectManagementApp(Application):

    def create_board(self) -> str:
        board = Board()
        self.save(board)
        return str(board.id)

    def edit_board_title(self, board_id: str, title: str):
        board_uuid = uuid.UUID(board_id)
        board = self.repository.get(board_uuid)
        board.edit_board_title(title)
        self.save(board)

    def edit_column_title(self, board_id: str, column_id: str, title: str):
        board_uuid = uuid.UUID(board_id)
        column_uuid = uuid.UUID(column_id)
        board = self.repository.get(board_uuid)
        board.edit_column_title(column_uuid, title)
        self.save(board)

    def edit_card_title(self, board_id, column_id: str, card_id: str, title: str):
        board_uuid = uuid.UUID(board_id)
        column_uuid = uuid.UUID(column_id)
        card_uuid = uuid.UUID(card_id)
        board = self.repository.get(board_uuid)
        board.edit_card_title(column_uuid, card_uuid, title)
        self.save(board)

    def edit_card_content(self, board_id, column_id: str, card_id: str, content: str):
        board_uuid = uuid.UUID(board_id)
        column_uuid = uuid.UUID(column_id)
        card_uuid = uuid.UUID(card_id)
        board = self.repository.get(board_uuid)
        board.edit_card_content(column_uuid, card_uuid, content)
        self.save(board)

    def add_column(self, board_id: str) -> str:
        board_uuid = uuid.UUID(board_id)
        board = self.repository.get(board_uuid)
        column_uuid = uuid.uuid4()
        board.add_column(column_uuid)
        self.save(board)
        return str(column_uuid)

    def remove_column(self, board_id: str, column_id: str):
        board_uuid = uuid.UUID(board_id)
        column_uuid = uuid.UUID(column_id)
        board = self.repository.get(board_uuid)
        board.remove_column(column_uuid)
        self.save(board)

    def move_column(self, board_id: str, column_id: str, new_index: int):
        board_uuid = uuid.UUID(board_id)
        column_uuid = uuid.UUID(column_id)
        board = self.repository.get(board_uuid)
        board.move_column(column_uuid, new_index)
        self.save(board)

    def add_card(self, board_id, column_id: str) -> str:
        board_uuid = uuid.UUID(board_id)
        column_uuid = uuid.UUID(column_id)
        board = self.repository.get(board_uuid)
        card_uuid = uuid.uuid4()
        board.add_card(column_uuid, card_uuid)
        self.save(board)
        return str(card_uuid)

    def remove_card(self, board_id: str, column_id: str, card_id: str):
        board_uuid = uuid.UUID(board_id)
        column_uuid = uuid.UUID(column_id)
        card_uuid = uuid.UUID(card_id)
        board = self.repository.get(board_uuid)
        board.remove_card(column_uuid, card_uuid)
        self.save(board)

    def move_card(self, board_id: str, from_column_id: str, to_column_id: str, card_id: str, new_index: int):
        board_uuid = uuid.UUID(board_id)
        from_column_uuid = uuid.UUID(from_column_id)
        to_column_uuid = uuid.UUID(to_column_id)
        card_uuid = uuid.UUID(card_id)
        board = self.repository.get(board_uuid)

        if from_column_uuid != to_column_uuid:
            card = board.get_card(from_column_uuid, card_uuid)
            board.remove_card(from_column_uuid, card_uuid)
            board.add_card(to_column_uuid, card.id, card.title, card.content)
        board.move_card(to_column_uuid, card_uuid, new_index)
        self.save(board)

    def board_as_dict(self, board_id: str, version: str = None) -> dict:
        board_uuid = uuid.UUID(board_id)
        board = self.repository.get(board_uuid, version=version)

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
