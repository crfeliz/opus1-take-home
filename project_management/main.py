import json
from project_management.project_management import ProjectManagementApp


def main():
    # Example: Initialize the application and perform some operations
    app = ProjectManagementApp()

    # Create a board
    board_id = app.create_board()
    app.edit_board_title(board_id, "Project Board")

    # Add a column
    column_id = app.add_column(board_id)
    app.edit_board_title(column_id, "To Do")

    # Add a card to the column
    card_id = app.add_card_to_column(column_id)
    app.edit_board_title(card_id, "Write main function")
    app.edit_board_title(card_id, "Demonstrate the application usage")

    print(json.dumps(app.board_as_dict(board_id), indent=4))


if __name__ == "__main__":
    main()
