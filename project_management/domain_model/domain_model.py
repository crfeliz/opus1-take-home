from eventsourcing.domain import Aggregate, event
from project_management.utils.collection_utils import (
    remove_item_by_id,
    with_item_moved_by_id,
    edit_item_by_id,
    find_item_by_id
)
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


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
        logger.debug("BOARD_CREATED")
        self.title = ""
        self.columns = []
        self.undo_jump_offset = 0
        self.undo_redo_tracker_id = None

    @event("UNDO_REDO_TRACKER_LINKED")
    def set_undo_redo_tracker(self, undo_redo_tracker_id):
        logger.debug("UNDO_REDO_TRACKER_LINKED")
        self.undo_redo_tracker_id = undo_redo_tracker_id

    @event("BOARD_TITLE_EDITED")
    def edit_board_title(self, title):
        logger.debug("BOARD_TITLE_EDITED")
        self.title = title

    @event("COLUMN_ADDED")
    def add_column(self, column_id):
        logger.debug("COLUMN_ADDED")
        column = Column(column_id)
        self.columns.append(column)

    @event("COLUMN_REMOVED")
    def remove_column(self, column_id):
        logger.debug("COLUMN_REMOVED")
        remove_item_by_id(self.columns, column_id)

    @event("COLUMN_MOVED")
    def move_column(self, column_id, new_index):
        logger.debug("COLUMN_MOVED")
        # this operation creates a new array
        self.columns = with_item_moved_by_id(self.columns, column_id, new_index)

    @event("COLUMN_TITLE_EDITED")
    def edit_column_title(self, column_id, title):
        logger.debug("COLUMN_TITLE_EDITED")
        edit_item_by_id(self.columns, column_id, lambda column: setattr(column, 'title', title))

    @event("CARD_TITLE_EDITED")
    def edit_card_title(self, column_id, card_id, title):
        logger.debug("CARD_TITLE_EDITED")
        column = find_item_by_id(self.columns, column_id)
        edit_item_by_id(column.cards, card_id, lambda card: setattr(card, 'title', title))

    @event("CARD_CONTENT_EDITED")
    def edit_card_content(self, column_id, card_id, content):
        logger.debug("CARD_CONTENT_EDITED")
        column = find_item_by_id(self.columns, column_id)
        edit_item_by_id(column.cards, card_id, lambda card: setattr(card, 'content', content))

    @event("CARD_ADDED")
    def add_card(self, column_id, card_id, title=None, content=None):
        logger.debug("CARD_ADDED")
        card = Card(card_id)
        if title is not None:
            card.title = title
        if content is not None:
            card.content = content

        column = find_item_by_id(self.columns, column_id)
        column.cards.append(card)

    @event("CARD_REMOVED")
    def remove_card(self, column_id, card_id):
        logger.debug("CARD_REMOVED")
        column = find_item_by_id(self.columns, column_id)
        remove_item_by_id(column.cards, card_id)

    @event("CARD_MOVED")
    def move_card(self, column_id, card_id, new_index):
        logger.debug("CARD_MOVED")
        column = find_item_by_id(self.columns, column_id)
        column.cards = with_item_moved_by_id(column.cards, card_id, new_index)

    def get_card(self, column_id, card_id):
        logger.debug("CARD_MOVED")
        column = find_item_by_id(self.columns, column_id)
        card = find_item_by_id(column.cards, card_id)
        if card is None:
            raise ValueError(f"Card {card_id} not found in column {column_id}")
        return card

    @event("COMMIT_UNDO_STATE")
    def commit_undo_state(self):
        logger.debug("COMMIT_UNDO_STATE")
        pass
