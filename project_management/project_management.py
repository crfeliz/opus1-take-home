import os
import uuid
from eventsourcing.application import Application
from eventsourcing.domain import Aggregate, event
from eventsourcing.system import NotificationLogReader


def try_remove(collection, item):
    if item in collection:
        collection.remove(item)
    else:
        raise ValueError(f"Item {item} not found in collection {collection}")

def move_item(collection, item_id, new_index):
    print(collection)
    item_index = next((i for i, item in enumerate(collection) if item == item_id), None)
    if item_index is None:
        raise ValueError(f"Item {item_id} not found in {collection}")

    item = collection.pop(item_index)
    collection.insert(new_index, item)

class Card(Aggregate):
    @event("CARD_CREATED")
    def __init__(self, board_id):
        self.board_id = board_id
        self.title = ""
        self.content = ""

    @event("TITLE_EDITED")
    def edit_title(self, title):
        self.title = title

    @event("CONTENT_EDITED")
    def edit_content(self, content):
        self.content = content


class Column(Aggregate):
    @event("COLUMN_CREATED")
    def __init__(self, board_id):
        self.board_id = board_id
        self.title = ""
        self.card_ids = []

    @event("TITLE_EDITED")
    def edit_title(self, title):
        self.title = title

    @event("CARD_ADDED")
    def add_card(self, card_id):
        self.card_ids.append(card_id)

    @event("CARD_REMOVED")
    def remove_card(self, card_id):
        try_remove(self.card_ids, card_id)

    @event("CARD_MOVED")
    def move_card(self, card_id, new_index):
        move_item(self.card_ids, card_id, new_index)


class Board(Aggregate):
    @event("BOARD_CREATED")
    def __init__(self):
        self.title = ""
        self.columns = []

    @event("TITLE_EDITED")
    def edit_title(self, title):
        self.title = title

    @event("COLUMN_ADDED")
    def add_column(self, column_id):
        self.column_ids.append(column_id)

    @event("REMOVE_COLUMN")
    def remove_column(self, column_id):
        try_remove(self.column_ids, column_id)

    @event("COLUMN_MOVED")
    def move_column(self, column_id, new_index):
        move_item(self.column_ids, column_id, new_index)


class ProjectManagementApp(Application):

    def create_board(self) -> str:
        board = Board()
        self.save(board)
        return str(board.id)

    def edit_board_title(self, board_id: str, title: str):
        board_uuid = uuid.UUID(board_id)
        board = self.repository.get(board_uuid)
        board.edit_title(title)
        self.save(board)

    def add_column_to_board(self, board_id: str) -> str:
        board_uuid = uuid.UUID(board_id)
        board = self.repository.get(board_uuid)
        column = Column(board_uuid)
        board.add_column(column.id)
        self.save(column)
        self.save(board)
        return str(column.id)

    def remove_column_from_board(self, board_id: str, column_id: str):
        board_uuid = uuid.UUID(board_id)
        column_uuid = uuid.UUID(column_id)
        board = self.repository.get(board_uuid)
        board.remove_column(column_uuid)
        self.save(board)

    def move_column_within_board(self, board_id: str, column_id: str, new_index: int):
        board_uuid = uuid.UUID(board_id)
        column_uuid = uuid.UUID(column_id)
        board = self.repository.get(board_uuid)
        board.move_column(column_uuid, new_index)
        self.save(board)

    def edit_column_title(self, column_id: str, title: str):
        column_uuid = uuid.UUID(column_id)
        column = self.repository.get(column_uuid)
        column.edit_title(title)
        self.save(column)

    def add_card_to_column(self, column_id: str) -> str:
        column_uuid = uuid.UUID(column_id)
        column = self.repository.get(column_uuid)
        card = Card(column.board_id)
        column.add_card(card.id)
        self.save(card)
        self.save(column)
        return str(card.id)

    def remove_card_from_column(self, column_id: str, card_id: str):
        column_uuid = uuid.UUID(column_id)
        card_uuid = uuid.UUID(card_id)
        column = self.repository.get(column_uuid)
        column.remove_card(card_uuid)
        self.save(column)

    def move_card(self, from_column_id: str, to_column_id: str, card_id: str, new_index: int):
        from_column_uuid = uuid.UUID(from_column_id)
        to_column_uuid = uuid.UUID(to_column_id)
        card_uuid = uuid.UUID(card_id)
        from_column = self.repository.get(from_column_uuid)
        to_column = self.repository.get(to_column_uuid)
        if from_column != to_column:
            from_column.remove_card(card_uuid)
            to_column.add_card(card_uuid)
        to_column.move_card(card_uuid, new_index)
        self.save(from_column)
        self.save(to_column)

    def edit_card_title(self, card_id: str, title: str):
        card_uuid = uuid.UUID(card_id)
        card = self.repository.get(card_uuid)
        card.edit_title(title)
        self.save(card)

    def edit_card_content(self, card_id: str, content: str):
        card_uuid = uuid.UUID(card_id)
        card = self.repository.get(card_uuid)
        card.edit_content(content)
        self.save(card)

    def recompile_to_n_minus_1(self):
        notification_log = self.notification_log
        reader = NotificationLogReader(notification_log)

        notifications = list(reader.read(start=0, limit=None))
        if len(notifications) <= 1:
            raise ValueError("Cannot undo. Not enough events to roll back.")

        events_to_process = notifications[:-1]
        recompiled_app = ProjectManagementApp(env=self.env)

        for notification in events_to_process:
            domain_event = notification.event
            recompiled_app.process_event(domain_event)
        return recompiled_app

    def board_as_dict(self, board_id: str) -> dict:
        board_uuid = uuid.UUID(board_id)
        board = self.repository.get(board_uuid)

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
                            for card_id in column.card_ids if (card := self.repository.get(card_id))
                        ],
                    }
                    for column_id in board.column_ids if (column := self.repository.get(column_id))
                ],
            }
        }

    def undo_last_action_on_board(self, board_id: str):
        # 1) Read the notification log
        reader = NotificationLogReader(self.notification_log)
        notifications = list(reader.read(start=0, limit=None))

        # 2) Filter for events belonging to this board only
        filtered_events = []
        for n in notifications:
            domain_event = n.event
            # We assume sub-aggregates (Column, Card) store board_id in an attribute or metadata
            # e.g., domain_event.__dict__.get('board_id'), or domain_event.metadata['board_id']
            # For illustration, let's assume domain_event.__dict__ has 'board_id'
            event_board_id = domain_event.__dict__.get('board_id')
            if event_board_id == board_id:
                filtered_events.append(n)

        if len(filtered_events) < 1:
            raise ValueError(f"No events found for board {board_id} to undo.")
        if len(filtered_events) == 1:
            raise ValueError(f"Cannot undo: only 1 event for board {board_id}.")

        # 3) Remove the latest event from this board
        events_to_process = filtered_events[:-1]

        # 4) Create a new application instance
        recompiled_app = ProjectManagementApp(env=self.env)

        # 5) Replay all but the last event
        for notification in events_to_process:
            domain_event = notification.event
            recompiled_app.process_event(domain_event)

        return recompiled_app

os.environ['PERSISTENCE_MODULE'] = 'eventsourcing.sqlite'
os.environ['SQLITE_DBNAME'] = 'events.db'