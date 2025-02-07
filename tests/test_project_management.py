import unittest
from project_management.project_management import ProjectManagementApp, Board, Column, Card


class TestProjectManagementApp(unittest.TestCase):

    def setUp(self):
        self.app = ProjectManagementApp()

    def test_create_board(self):
        # Create a new board
        board_id = self.app.create_board()
        board_dict = self.app.board_as_dict(board_id)

        # Check that the board was created with correct initial values
        self.assertEqual(board_dict["board"]["id"], str(board_id))
        self.assertEqual(board_dict["board"]["title"], "")
        self.assertEqual(board_dict["board"]["columns"], [])

    def test_edit_board_title(self):
        # Create a new board
        board_id = self.app.create_board()

        # Edit board title
        new_title = "Project Board"
        self.app.edit_board_title(board_id, new_title)

        # Fetch the board as a dictionary and check title
        board_dict = self.app.board_as_dict(board_id)
        self.assertEqual(board_dict["board"]["title"], new_title)

    def test_add_column(self):
        # Create a new board
        board_id = self.app.create_board()

        # Add a column to the board
        column_id = self.app.add_column(board_id)

        # Fetch the board and check if column was added
        board_dict = self.app.board_as_dict(board_id)
        self.assertEqual(len(board_dict["board"]["columns"]), 1)
        self.assertEqual(board_dict["board"]["columns"][0]["id"], str(column_id))
        self.assertEqual(board_dict["board"]["columns"][0]["title"], "")
        self.assertEqual(board_dict["board"]["columns"][0]["cards"], [])

    def test_edit_column_title(self):
        # Create a new board and add a column
        board_id = self.app.create_board()
        column_id = self.app.add_column(board_id)

        # Edit the column title
        new_title = "To Do"
        self.app.edit_column_title(board_id, column_id, new_title)

        # Fetch the board and check column title
        board_dict = self.app.board_as_dict(board_id)
        self.assertEqual(board_dict["board"]["columns"][0]["title"], new_title)

    def test_add_card(self):
        # Create a new board and add a column
        board_id = self.app.create_board()
        column_id = self.app.add_column(board_id)

        # Add a card to the column
        card_id = self.app.add_card(board_id, column_id)

        # Fetch the board and check if the card was added
        board_dict = self.app.board_as_dict(board_id)
        self.assertEqual(len(board_dict["board"]["columns"][0]["cards"]), 1)
        card_dict = board_dict["board"]["columns"][0]["cards"][0]
        self.assertEqual(card_dict["id"], str(card_id))
        self.assertEqual(card_dict["title"], "")
        self.assertEqual(card_dict["content"], "")

    def test_move_card_within_column(self):
        # Create a new board and add a column
        board_id = self.app.create_board()
        column_id = self.app.add_column(board_id)

        # Add cards to the column
        card_id1 = self.app.add_card(board_id, column_id)
        card_id2 = self.app.add_card(board_id, column_id)

        # Move card1 to the second position in the same column
        self.app.move_card(board_id, column_id, column_id, card_id1, 2)

        # Fetch the board and check card order
        board_dict = self.app.board_as_dict(board_id)
        card_ids = [card["id"] for card in board_dict["board"]["columns"][0]["cards"]]
        self.assertEqual(card_ids, [str(card_id2), str(card_id1)])

    def test_remove_card(self):
        # Create a new board and add a column
        board_id = self.app.create_board()
        column_id = self.app.add_column(board_id)

        # Add a card to the column
        card_id = self.app.add_card(board_id, column_id)

        # Remove the card
        self.app.remove_card(board_id, column_id, card_id)

        # Fetch the board and check if the card was removed
        board_dict = self.app.board_as_dict(board_id)
        self.assertEqual(len(board_dict["board"]["columns"][0]["cards"]), 0)

    def test_remove_column(self):
        # Create a new board
        board_id = self.app.create_board()

        # Add a column
        column_id = self.app.add_column(board_id)

        # Remove the column
        self.app.remove_column(board_id, column_id)

        # Fetch the board and check if the column was removed
        board_dict = self.app.board_as_dict(board_id)
        self.assertEqual(len(board_dict["board"]["columns"]), 0)

    def test_move_column(self):
        # Create a new board
        board_id = self.app.create_board()

        # Add columns
        column_id1 = self.app.add_column(board_id)
        column_id2 = self.app.add_column(board_id)

        # Move column1 to second position
        self.app.move_column(board_id, column_id1, 2)

        # Fetch the board and check column order
        board_dict = self.app.board_as_dict(board_id)
        column_ids = [col["id"] for col in board_dict["board"]["columns"]]
        self.assertEqual(column_ids, [str(column_id2), str(column_id1)])

    def test_multiple_boards_and_cards(self):
        # Create multiple boards
        board_1_id = self.app.create_board()
        board_2_id = self.app.create_board()

        # Add columns to both boards
        col_1_1 = self.app.add_column(board_1_id)
        col_1_2 = self.app.add_column(board_1_id)
        col_2_1 = self.app.add_column(board_2_id)

        # Add cards to columns
        card_1_1_1 = self.app.add_card(board_1_id, col_1_1)
        card_1_2_1 = self.app.add_card(board_1_id, col_1_2)
        card_2_1_1 = self.app.add_card(board_2_id, col_2_1)

        # Edit board titles
        self.app.edit_board_title(board_1_id, "Board 1 - To Do")
        self.app.edit_board_title(board_2_id, "Board 2 - In Progress")

        # Edit column titles
        self.app.edit_column_title(board_1_id, col_1_1, "Backlog")
        self.app.edit_column_title(board_1_id, col_1_2, "In Development")
        self.app.edit_column_title(board_2_id, col_2_1, "Review")

        # Edit card titles
        self.app.edit_card_title(board_1_id, col_1_1, card_1_1_1, "Card 1 for Backlog")
        self.app.edit_card_title(board_1_id, col_1_2, card_1_2_1, "Card 2 for In Development")
        self.app.edit_card_title(board_2_id, col_2_1, card_2_1_1, "Card for Review")

        # Check board 1
        board_1_dict = self.app.board_as_dict(board_1_id)
        self.assertEqual(board_1_dict["board"]["title"], "Board 1 - To Do")
        self.assertEqual(len(board_1_dict["board"]["columns"]), 2)
        self.assertEqual(board_1_dict["board"]["columns"][0]["title"], "Backlog")
        self.assertEqual(board_1_dict["board"]["columns"][1]["title"], "In Development")
        self.assertEqual(len(board_1_dict["board"]["columns"][0]["cards"]), 1)
        self.assertEqual(board_1_dict["board"]["columns"][0]["cards"][0]["title"], "Card 1 for Backlog")

        # Check board 2
        board_2_dict = self.app.board_as_dict(board_2_id)
        self.assertEqual(board_2_dict["board"]["title"], "Board 2 - In Progress")
        self.assertEqual(len(board_2_dict["board"]["columns"]), 1)
        self.assertEqual(board_2_dict["board"]["columns"][0]["title"], "Review")
        self.assertEqual(len(board_2_dict["board"]["columns"][0]["cards"]), 1)
        self.assertEqual(board_2_dict["board"]["columns"][0]["cards"][0]["title"], "Card for Review")

    def test_move_cards_and_edit_column_titles(self):
        # Create a board
        board_id = self.app.create_board()

        # Add columns
        col_1 = self.app.add_column(board_id)
        col_2 = self.app.add_column(board_id)

        # Add cards
        c1 = self.app.add_card(board_id, col_1)
        c2 = self.app.add_card(board_id, col_1)
        c3 = self.app.add_card(board_id, col_2)
        c4 = self.app.add_card(board_id, col_2)

        # Edit card titles
        self.app.edit_card_title(board_id, col_1, c1, "Card 1 for Backlog")
        self.app.edit_card_title(board_id, col_1, c2, "Card 2 for Backlog")
        self.app.edit_card_title(board_id, col_2, c3, "Card for Review")
        self.app.edit_card_title(board_id, col_2, c4, "Card 4 for In Progress")

        # Move card c2 to the front of col_1
        self.app.move_card(board_id, col_1, col_1, c2, 0)

        # Edit column titles
        self.app.edit_column_title(board_id, col_1, "To Do")
        self.app.edit_column_title(board_id, col_2, "In Progress")

        # Check final board state
        board_dict = self.app.board_as_dict(board_id)

        # Board should have two columns
        self.assertEqual(len(board_dict["board"]["columns"]), 2)

        # Verify column titles
        self.assertEqual(board_dict["board"]["columns"][0]["title"], "To Do")
        self.assertEqual(board_dict["board"]["columns"][1]["title"], "In Progress")

        # The first column should have c2 at the front now
        col1_cards = board_dict["board"]["columns"][0]["cards"]
        self.assertEqual(len(col1_cards), 2)
        self.assertEqual(col1_cards[0]["title"], "Card 2 for Backlog")
        self.assertEqual(col1_cards[1]["title"], "Card 1 for Backlog")

        # The second column should still have c3, c4
        col2_cards = board_dict["board"]["columns"][1]["cards"]
        self.assertEqual(len(col2_cards), 2)
        self.assertEqual(col2_cards[0]["title"], "Card for Review")
        self.assertEqual(col2_cards[1]["title"], "Card 4 for In Progress")

    def test_remove_cards_and_columns(self):
        # Create a board
        board_id = self.app.create_board()

        # Add columns
        col1 = self.app.add_column(board_id)
        col2 = self.app.add_column(board_id)

        # Add cards
        c1 = self.app.add_card(board_id, col1)
        c2 = self.app.add_card(board_id, col2)

        # Remove a card from col1
        self.app.remove_card(board_id, col1, c1)

        # Remove col2 from board
        self.app.remove_column(board_id, col2)

        # Check final board state
        board_dict = self.app.board_as_dict(board_id)
        self.assertEqual(len(board_dict["board"]["columns"]), 1)
        self.assertEqual(board_dict["board"]["columns"][0]["title"], "")
        self.assertEqual(len(board_dict["board"]["columns"][0]["cards"]), 0)

        # Confirm c1 was removed
        self.assertEqual(len(board_dict["board"]["columns"][0]["cards"]), 0)


if __name__ == "__main__":
    unittest.main()
