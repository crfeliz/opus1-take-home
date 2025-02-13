import unittest

from project_management.project_management_app import (
    ProjectManagementApp,
)


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
        board_id = self.app.create_board()
        new_title = "Project Board"
        self.app.edit_board_title(board_id, new_title)
        board_dict = self.app.board_as_dict(board_id)
        self.assertEqual(board_dict["board"]["title"], new_title)

    def test_add_column(self):
        board_id = self.app.create_board()
        column_id = self.app.add_column(board_id)
        board_dict = self.app.board_as_dict(board_id)
        self.assertEqual(len(board_dict["board"]["columns"]), 1)
        self.assertEqual(board_dict["board"]["columns"][0]["id"], str(column_id))
        self.assertEqual(board_dict["board"]["columns"][0]["title"], "")
        self.assertEqual(board_dict["board"]["columns"][0]["cards"], [])

    def test_edit_column_title(self):
        board_id = self.app.create_board()
        column_id = self.app.add_column(board_id)
        new_title = "To Do"
        self.app.edit_column_title(board_id, column_id, new_title)
        board_dict = self.app.board_as_dict(board_id)
        self.assertEqual(board_dict["board"]["columns"][0]["title"], new_title)

    def test_add_card(self):
        board_id = self.app.create_board()
        column_id = self.app.add_column(board_id)
        card_id = self.app.add_card(board_id, column_id)
        board_dict = self.app.board_as_dict(board_id)
        self.assertEqual(len(board_dict["board"]["columns"][0]["cards"]), 1)
        card_dict = board_dict["board"]["columns"][0]["cards"][0]
        self.assertEqual(card_dict["id"], str(card_id))
        self.assertEqual(card_dict["title"], "")
        self.assertEqual(card_dict["content"], "")

    def test_move_card_within_column(self):
        board_id = self.app.create_board()
        column_id = self.app.add_column(board_id)
        card_id1 = self.app.add_card(board_id, column_id)
        card_id2 = self.app.add_card(board_id, column_id)
        self.app.move_card(board_id, column_id, column_id, card_id1, 2)
        board_dict = self.app.board_as_dict(board_id)
        card_ids = [card["id"] for card in board_dict["board"]["columns"][0]["cards"]]
        self.assertEqual(card_ids, [str(card_id2), str(card_id1)])

    def test_remove_card(self):
        board_id = self.app.create_board()
        column_id = self.app.add_column(board_id)
        card_id = self.app.add_card(board_id, column_id)
        self.app.remove_card(board_id, column_id, card_id)
        board_dict = self.app.board_as_dict(board_id)
        self.assertEqual(len(board_dict["board"]["columns"][0]["cards"]), 0)

    def test_remove_column(self):
        board_id = self.app.create_board()
        column_id = self.app.add_column(board_id)
        self.app.remove_column(board_id, column_id)
        board_dict = self.app.board_as_dict(board_id)
        self.assertEqual(len(board_dict["board"]["columns"]), 0)

    def test_move_column(self):
        board_id = self.app.create_board()
        column_id1 = self.app.add_column(board_id)
        column_id2 = self.app.add_column(board_id)
        self.app.move_column(board_id, column_id1, 2)
        board_dict = self.app.board_as_dict(board_id)
        column_ids = [col["id"] for col in board_dict["board"]["columns"]]
        self.assertEqual(column_ids, [str(column_id2), str(column_id1)])

    def test_multiple_boards_and_cards(self):
        board_1_id = self.app.create_board()
        board_2_id = self.app.create_board()
        col_1_1 = self.app.add_column(board_1_id)
        col_1_2 = self.app.add_column(board_1_id)
        col_2_1 = self.app.add_column(board_2_id)
        card_1_1_1 = self.app.add_card(board_1_id, col_1_1)
        card_1_2_1 = self.app.add_card(board_1_id, col_1_2)
        card_2_1_1 = self.app.add_card(board_2_id, col_2_1)
        self.app.edit_board_title(board_1_id, "Board 1 - To Do")
        self.app.edit_board_title(board_2_id, "Board 2 - In Progress")
        self.app.edit_column_title(board_1_id, col_1_1, "Backlog")
        self.app.edit_column_title(board_1_id, col_1_2, "In Development")
        self.app.edit_column_title(board_2_id, col_2_1, "Review")
        self.app.edit_card_title(board_1_id, col_1_1, card_1_1_1, "Card 1 for Backlog")
        self.app.edit_card_title(board_1_id, col_1_2, card_1_2_1, "Card 2 for In Development")
        self.app.edit_card_title(board_2_id, col_2_1, card_2_1_1, "Card for Review")
        board_1_dict = self.app.board_as_dict(board_1_id)
        self.assertEqual(board_1_dict["board"]["title"], "Board 1 - To Do")
        self.assertEqual(len(board_1_dict["board"]["columns"]), 2)
        self.assertEqual(board_1_dict["board"]["columns"][0]["title"], "Backlog")
        board_2_dict = self.app.board_as_dict(board_2_id)
        self.assertEqual(board_2_dict["board"]["title"], "Board 2 - In Progress")
        self.assertEqual(len(board_2_dict["board"]["columns"]), 1)

    def test_move_cards_and_edit_column_titles(self):
        board_id = self.app.create_board()
        col_1 = self.app.add_column(board_id)
        col_2 = self.app.add_column(board_id)
        c1 = self.app.add_card(board_id, col_1)
        c2 = self.app.add_card(board_id, col_1)
        c3 = self.app.add_card(board_id, col_2)
        c4 = self.app.add_card(board_id, col_2)
        self.app.edit_card_title(board_id, col_1, c1, "Card 1 for Backlog")
        self.app.edit_card_title(board_id, col_1, c2, "Card 2 for Backlog")
        self.app.edit_card_title(board_id, col_2, c3, "Card for Review")
        self.app.edit_card_title(board_id, col_2, c4, "Card 4 for In Progress")
        self.app.move_card(board_id, col_1, col_1, c2, 0)
        self.app.edit_column_title(board_id, col_1, "To Do")
        self.app.edit_column_title(board_id, col_2, "In Progress")
        board_dict = self.app.board_as_dict(board_id)
        self.assertEqual(len(board_dict["board"]["columns"]), 2)
        self.assertEqual(board_dict["board"]["columns"][0]["title"], "To Do")
        col1_cards = board_dict["board"]["columns"][0]["cards"]
        self.assertEqual(len(col1_cards), 2)
        self.assertEqual(col1_cards[0]["title"], "Card 2 for Backlog")
        col2_cards = board_dict["board"]["columns"][1]["cards"]
        self.assertEqual(len(col2_cards), 2)
        self.assertEqual(col2_cards[0]["title"], "Card for Review")

    def test_remove_cards_and_columns(self):
        board_id = self.app.create_board()
        col1 = self.app.add_column(board_id)
        col2 = self.app.add_column(board_id)
        c1 = self.app.add_card(board_id, col1)
        self.app.add_card(board_id, col2)
        self.app.remove_card(board_id, col1, c1)
        self.app.remove_column(board_id, col2)
        board_dict = self.app.board_as_dict(board_id)
        self.assertEqual(len(board_dict["board"]["columns"]), 1)
        self.assertEqual(len(board_dict["board"]["columns"][0]["cards"]), 0)

    def test_initial_undo_redo_tracker_cursor(self):
        board_id = self.app.create_board()
        board = self.app.repository.get(board_id)
        tracker = self.app.repository.get(board.undo_redo_tracker_id)
        self.assertEqual(tracker.get_version_cursor(), board.version)

    def test_edit_board_title_increments_tracker(self):
        board_id = self.app.create_board()
        board_before = self.app.repository.get(board_id)
        initial_version = board_before.version
        self.app.edit_board_title(board_id, "New Title")
        board_after = self.app.repository.get(board_id)
        self.assertEqual(board_after.title, "New Title")
        version_cursor = self.app.undo_redo_state_manager.get_version_cursor(board_id)
        self.assertGreater(version_cursor, initial_version, "Cursor should increment after an edit.")

    def test_undo_decrements_cursor(self):
        board_id = self.app.create_board()
        self.app.edit_board_title(board_id, "Title 1")
        self.app.edit_board_title(board_id, "Title 2")
        self.app.edit_board_title(board_id, "Title 3")
        current_cursor = self.app.undo_redo_state_manager.get_version_cursor(board_id)
        self.app.undo(board_id)
        new_cursor = self.app.undo_redo_state_manager.get_version_cursor(board_id)
        self.assertLess(new_cursor, current_cursor, "Undo should lower the cursor.")

    def test_redo_increments_cursor(self):
        board_id = self.app.create_board()
        self.app.edit_board_title(board_id, "Title 1")
        self.app.edit_board_title(board_id, "Title 2")
        current_cursor = self.app.undo_redo_state_manager.get_version_cursor(board_id)
        self.app.undo(board_id)
        cursor_after_undo = self.app.undo_redo_state_manager.get_version_cursor(board_id)
        self.assertLess(cursor_after_undo, current_cursor, "Cursor should decrease after undo.")
        self.app.redo(board_id)
        cursor_after_redo = self.app.undo_redo_state_manager.get_version_cursor(board_id)
        self.assertGreater(cursor_after_redo, cursor_after_undo, "Redo should raise the cursor.")

    def test_commit_updates_cursor(self):
        board_id = self.app.create_board()
        self.app.add_column(board_id)
        self.app.add_column(board_id)
        self.app.undo(board_id)
        self.app.undo(board_id)

        board_before = self.app.repository.get(board_id)
        tracker_before = self.app.repository.get(board_before.undo_redo_tracker_id)

        self.assertLess(tracker_before.get_version_cursor(), board_before.version,
                        "Undo before commit should leave the cursor behind the board version")

        self.app.edit_board_title(board_id, "Title")  # triggers commit

        board_after = self.app.repository.get(board_id)
        tracker_after = self.app.repository.get(board_after.undo_redo_tracker_id)
        self.assertEqual(tracker_after.get_version_cursor(), board_after.version,
                         "After commit, the tracker cursor should equal the board version.")

    def test_complex_undo_redo_sequence(self):
        board_id = self.app.create_board()
        # Perform a series of title edits.
        for t in ["Title1", "Title2", "Title3", "Title4", "Title5"]:
            self.app.edit_board_title(board_id, t)
        final_board = self.app.repository.get(board_id)
        final_version = final_board.version
        # Undo three times.
        for _ in range(3):
            self.app.undo(board_id)
        active_version_after_undo = self.app.undo_redo_state_manager.get_version_cursor(board_id)
        self.assertLess(active_version_after_undo, final_version,
                        "After undoing multiple, active version should be less than final version")

        board_dict = self.app.board_as_dict(board_id)
        self.assertEqual(board_dict["board"]["title"], "Title2",
                         "Rendered board title should be Title2")

        # Redo until we reach final version.
        while self.app.undo_redo_state_manager.get_version_cursor(board_id) < final_version:
            self.app.redo(board_id)
        active_version_after_redo = self.app.undo_redo_state_manager.get_version_cursor(board_id)
        self.assertEqual(active_version_after_redo, final_version,
                         "After redoing multiple, active version should equal final version")
        # Assert rendered output reflects final title.
        board_dict = self.app.board_as_dict(board_id)
        self.assertEqual(board_dict["board"]["title"], "Title5",
                         "Rendered board title should be Title5")
        self.assertEqual(board_dict["board"]["version"], final_board.version,
                         "Rendered board version should match final version")

    def test_new_operation_breaks_redo_chain(self):
        board_id = self.app.create_board()
        # Create a few columns.
        for _ in range(3):
            self.app.add_column(board_id)
        # Undo twice.
        self.app.undo(board_id)
        self.app.undo(board_id)
        # At this point, the tracker cursor should be less than the board's tip.
        cursor_before_new_op = self.app.undo_redo_state_manager.get_version_cursor(board_id)
        board_before_new_op = self.app.repository.get(board_id)
        self.assertLess(cursor_before_new_op,
                        board_before_new_op.version, "After undo cursor should be less than the board's tip")

        # Now perform a new operation: add a column and then edit its title.
        column_id = self.app.add_column(board_id)
        self.app.edit_column_title(board_id, column_id, "LastOne")
        cursor_after_new_op = self.app.undo_redo_state_manager.get_version_cursor(board_id)
        # Attempt to redo.
        self.app.redo(board_id)
        cursor_after_redo = self.app.undo_redo_state_manager.get_version_cursor(board_id)
        # Since the redo chain is broken, the cursor should remain unchanged.
        self.assertEqual(cursor_after_new_op, cursor_after_redo,
                         "New operation should break the redo chain")
        # Also assert that the rendered board reflects the new column title.
        board_dict = self.app.board_as_dict(board_id)
        # Look for the column with the expected title.
        column_titles = [col["title"] for col in board_dict["board"]["columns"]]
        self.assertIn("LastOne", column_titles,
                      "Rendered board should include a column titled 'LastOne'")

    def test_multiple_undo_beyond_minimum(self):
        board_id = self.app.create_board()
        # Perform two title edits.
        for t in ["Title1", "Title2"]:
            self.app.edit_board_title(board_id, t)
        # Attempt many undos.
        for _ in range(10):
            self.app.undo(board_id)
        active_version = self.app.undo_redo_state_manager.get_version_cursor(board_id)
        # The cursor should not fall below the minimal value (which is 2)
        self.assertGreaterEqual(active_version, 2,
                                "Cursor should not fall below the minimum allowed value")
        # Assert that rendered board shows the earliest title ("Title1") if undo goes past the second edit.
        board_dict = self.app.board_as_dict(board_id)
        self.assertEqual(board_dict["board"]["title"], "",
                         "Rendered board title should be empty after excessive undos")

    def test_stress_undo_redo_commit(self):
        board_id = self.app.create_board()

        # version should end at 22
        for i in range(20):
            self.app.edit_board_title(board_id, f"Title {i}")

        # cursor should be 12
        for _ in range(10):
            self.app.undo(board_id)

        # cursor should be 17
        for _ in range(5):
            self.app.redo(board_id)

        self.assertEqual(self.app.undo_redo_state_manager.get_version_cursor(board_id),
                         17,
                         "cursor should be 17 after the given undo redo sequence")

        # Perform a final edit to trigger a commit.
        self.app.edit_board_title(board_id, "Final Title")
        board_after = self.app.repository.get(board_id)
        active_version = self.app.undo_redo_state_manager.get_version_cursor(board_id)
        self.assertEqual(active_version, board_after.version,
                         "After final commit, the tracker cursor should match the board version")
        self.assertEqual(self.app.undo_redo_state_manager.get_version_cursor(board_id),
                         24, "after the given sequence the version should be 24")
        # Assert that rendered board reflects the final title.
        board_dict = self.app.board_as_dict(board_id)
        self.assertEqual(board_dict["board"]["title"], "Final Title",
                         "Rendered board title should be 'Final Title' after stress test")
        self.assertEqual(board_dict["board"]["version"], board_after.version,
                         "Rendered board version should match the board's final version")

        self.app.undo(board_id)  # should jump cursor back to 17
        active_version = self.app.undo_redo_state_manager.get_version_cursor(board_id)
        self.assertEqual(active_version, 17, "undo should cause cursor to jump from commit to reference")

        self.app.undo(board_id)  # cursor is 16
        self.app.redo(board_id)  # cursor is 17
        active_version = self.app.undo_redo_state_manager.get_version_cursor(board_id)
        self.assertEqual(active_version, 17, "redo should allow cursor to land on reference")
        self.app.redo(board_id)  # cursor is 24
        active_version = self.app.undo_redo_state_manager.get_version_cursor(board_id)
        self.assertEqual(active_version,
                         24,
                         "attempt to redo past the reference should jump to the commit + 1")


if __name__ == "__main__":
    unittest.main()
