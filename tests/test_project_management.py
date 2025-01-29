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

    def test_add_column_to_board(self):
        # Create a new board
        board_id = self.app.create_board()

        # Add a column to the board
        column_id = self.app.add_column_to_board(board_id)

        # Fetch the board and check if column was added
        board_dict = self.app.board_as_dict(board_id)
        self.assertEqual(len(board_dict["board"]["columns"]), 1)
        self.assertEqual(board_dict["board"]["columns"][0]["id"], str(column_id))
        self.assertEqual(board_dict["board"]["columns"][0]["title"], "")
        self.assertEqual(board_dict["board"]["columns"][0]["cards"], [])

    def test_edit_column_title(self):
        # Create a new board and add a column
        board_id = self.app.create_board()
        column_id = self.app.add_column_to_board(board_id)

        # Edit the column title
        new_title = "To Do"
        self.app.edit_column_title(column_id, new_title)

        # Fetch the board and check column title
        board_dict = self.app.board_as_dict(board_id)
        self.assertEqual(board_dict["board"]["columns"][0]["title"], new_title)

    def test_add_card_to_column(self):
        # Create a new board and add a column
        board_id = self.app.create_board()
        column_id = self.app.add_column_to_board(board_id)

        # Add a card to the column
        card_id = self.app.add_card_to_column(column_id)

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
        column_id = self.app.add_column_to_board(board_id)

        # Add cards to the column
        card_id1 = self.app.add_card_to_column(column_id)
        card_id2 = self.app.add_card_to_column(column_id)

        # Move the first card to the second position
        self.app.move_card(column_id, card_id1, 1)

        # Fetch the board and check card order
        board_dict = self.app.board_as_dict(board_id)
        card_ids = [card["id"] for card in board_dict["board"]["columns"][0]["cards"]]
        self.assertEqual(card_ids, [str(card_id2), str(card_id1)])

    def test_remove_card_from_column(self):
        # Create a new board and add a column
        board_id = self.app.create_board()
        column_id = self.app.add_column_to_board(board_id)

        # Add a card to the column
        card_id = self.app.add_card_to_column(column_id)

        # Remove the card from the column
        self.app.remove_card_from_column(column_id, card_id)

        # Fetch the board and check if the card was removed
        board_dict = self.app.board_as_dict(board_id)
        self.assertEqual(len(board_dict["board"]["columns"][0]["cards"]), 0)

    def test_remove_column_from_board(self):
        # Create a new board
        board_id = self.app.create_board()

        # Add a column to the board
        column_id = self.app.add_column_to_board(board_id)

        # Remove the column from the board
        self.app.remove_column_from_board(board_id, column_id)

        # Fetch the board and check if the column was removed
        board_dict = self.app.board_as_dict(board_id)
        self.assertEqual(len(board_dict["board"]["columns"]), 0)

    def test_move_column_within_board(self):
        # Create a new board
        board_id = self.app.create_board()

        # Add columns to the board
        column_id1 = self.app.add_column_to_board(board_id)
        column_id2 = self.app.add_column_to_board(board_id)

        # Move the first column to the second position
        self.app.move_column_within_board(board_id, column_id1, 1)

        # Fetch the board and check column order
        board_dict = self.app.board_as_dict(board_id)
        column_ids = [column["id"] for column in board_dict["board"]["columns"]]
        self.assertEqual(column_ids, [str(column_id2), str(column_id1)])

    def test_multiple_boards_and_cards(self):
        # Scaffold 1: Create a project with multiple boards
        board_1_id = self.app.create_board()
        board_2_id = self.app.create_board()

        # Scaffold 2: Add columns to both boards
        column_1_1_id = self.app.add_column_to_board(board_1_id)
        column_1_2_id = self.app.add_column_to_board(board_1_id)
        column_2_1_id = self.app.add_column_to_board(board_2_id)

        # Scaffold 3: Add cards to columns
        card_1_1_1_id = self.app.add_card_to_column(column_1_1_id)
        card_1_2_1_id = self.app.add_card_to_column(column_1_2_id)
        card_2_1_1_id = self.app.add_card_to_column(column_2_1_id)

        # Scaffold 4: Edit board titles
        self.app.edit_board_title(board_1_id, "Board 1 - To Do")
        self.app.edit_board_title(board_2_id, "Board 2 - In Progress")

        # Scaffold 5: Edit column and card titles
        self.app.edit_column_title(column_1_1_id, "Backlog")
        self.app.edit_column_title(column_1_2_id, "In Development")
        self.app.edit_column_title(column_2_1_id, "Review")
        self.app.edit_card_title(card_1_1_1_id, "Card 1 for Backlog")
        self.app.edit_card_title(card_1_2_1_id, "Card 2 for In Development")
        self.app.edit_card_title(card_2_1_1_id, "Card for Review")

        # Final Check: Fetch boards and compare with scaffolded data
        board_1_dict = self.app.board_as_dict(board_1_id)
        board_2_dict = self.app.board_as_dict(board_2_id)

        # Check Board 1
        self.assertEqual(board_1_dict["board"]["title"], "Board 1 - To Do")
        self.assertEqual(len(board_1_dict["board"]["columns"]), 2)
        self.assertEqual(board_1_dict["board"]["columns"][0]["title"], "Backlog")
        self.assertEqual(board_1_dict["board"]["columns"][1]["title"], "In Development")
        self.assertEqual(len(board_1_dict["board"]["columns"][0]["cards"]), 1)
        self.assertEqual(board_1_dict["board"]["columns"][0]["cards"][0]["title"], "Card 1 for Backlog")

        # Check Board 2
        self.assertEqual(board_2_dict["board"]["title"], "Board 2 - In Progress")
        self.assertEqual(len(board_2_dict["board"]["columns"]), 1)
        self.assertEqual(board_2_dict["board"]["columns"][0]["title"], "Review")
        self.assertEqual(len(board_2_dict["board"]["columns"][0]["cards"]), 1)
        self.assertEqual(board_2_dict["board"]["columns"][0]["cards"][0]["title"], "Card for Review")

    def test_move_cards_and_edit_column_titles(self):
        # Scaffold 1: Create a project with a board
        board_id = self.app.create_board()

        # Scaffold 2: Add columns to the board
        column_1_id = self.app.add_column_to_board(board_id)
        column_2_id = self.app.add_column_to_board(board_id)

        # Scaffold 3: Add cards to the columns
        card_1_id = self.app.add_card_to_column(column_1_id)
        card_2_id = self.app.add_card_to_column(column_1_id)
        card_3_id = self.app.add_card_to_column(column_2_id)
        card_4_id = self.app.add_card_to_column(column_2_id)

        # Scaffold 4: Edit card titles
        self.app.edit_card_title(card_1_id, "Card 1 for Backlog")
        self.app.edit_card_title(card_2_id, "Card 2 for Backlog")
        self.app.edit_card_title(card_3_id, "Card for Review")
        self.app.edit_card_title(card_4_id, "Card 4 for In Progress")

        # Scaffold 5: Move a card within columns (after having multiple cards in each)
        self.app.move_card(column_1_id, card_2_id, 0)  # Moving card 2 to the front

        # Scaffold 6: Edit column titles
        self.app.edit_column_title(column_1_id, "To Do")
        self.app.edit_column_title(column_2_id, "In Progress")

        # Final Check: Verify card movement and column title changes
        board_dict = self.app.board_as_dict(board_id)

        # Board should have two columns
        self.assertEqual(len(board_dict["board"]["columns"]), 2)

        # Verify the new column titles
        self.assertEqual(board_dict["board"]["columns"][0]["title"], "To Do")
        self.assertEqual(board_dict["board"]["columns"][1]["title"], "In Progress")

        # Verify the cards are correctly moved within the columns
        self.assertEqual(len(board_dict["board"]["columns"][0]["cards"]), 2)
        self.assertEqual(board_dict["board"]["columns"][0]["cards"][0]["title"], "Card 2 for Backlog")
        self.assertEqual(board_dict["board"]["columns"][0]["cards"][1]["title"], "Card 1 for Backlog")
        self.assertEqual(len(board_dict["board"]["columns"][1]["cards"]), 2)
        self.assertEqual(board_dict["board"]["columns"][1]["cards"][0]["title"], "Card for Review")
        self.assertEqual(board_dict["board"]["columns"][1]["cards"][1]["title"], "Card 4 for In Progress")

    def test_remove_cards_and_columns(self):
        # Scaffold 1: Create a project with a board
        board_id = self.app.create_board()

        # Scaffold 2: Add columns to the board
        column_1_id = self.app.add_column_to_board(board_id)
        column_2_id = self.app.add_column_to_board(board_id)

        # Scaffold 3: Add cards to the columns
        card_1_id = self.app.add_card_to_column(column_1_id)
        card_2_id = self.app.add_card_to_column(column_2_id)

        # Scaffold 4: Remove a card from a column
        self.app.remove_card_from_column(column_1_id, card_1_id)

        # Scaffold 5: Remove a column from the board
        self.app.remove_column_from_board(board_id, column_2_id)

        # Final Check: Verify the board state after removals
        board_dict = self.app.board_as_dict(board_id)
        self.assertEqual(len(board_dict["board"]["columns"]), 1)
        self.assertEqual(board_dict["board"]["columns"][0]["title"], "")
        self.assertEqual(len(board_dict["board"]["columns"][0]["cards"]), 0)

        # Check that the card was properly removed
        self.assertEqual(len(board_dict["board"]["columns"][0]["cards"]), 0)


if __name__ == "__main__":
    unittest.main()
