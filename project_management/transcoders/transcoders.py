from typing import Any

from eventsourcing.persistence import Transcoding

from project_management.domain_model import Card, Column


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
