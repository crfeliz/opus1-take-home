import argparse
from project_management.project_management import ProjectManagementApp


def main():
    parser = argparse.ArgumentParser(description="Project Management CLI")

    # Add subcommands for each action (e.g., create board, edit title, etc.)
    subparsers = parser.add_subparsers(dest="command")

    # Create Board command
    create_board_parser = subparsers.add_parser("create_board", help="Create a new board")

    # Edit Board Title command
    edit_board_title_parser = subparsers.add_parser("edit_board_title", help="Edit board title")
    edit_board_title_parser.add_argument("--board-id", required=True, help="ID of the board to edit")
    edit_board_title_parser.add_argument("--title", required=True, help="New title for the board")

    # Add Column command
    add_column_parser = subparsers.add_parser("add_column", help="Add a column to a board")
    add_column_parser.add_argument("--board-id", required=True, help="ID of the board to add a column")

    # Remove Column command
    remove_column_parser = subparsers.add_parser("remove_column", help="Remove a column from a board")
    remove_column_parser.add_argument("--board-id", required=True, help="ID of the board")
    remove_column_parser.add_argument("--column-id", required=True, help="ID of the column to remove")

    # Add Card command
    add_card_parser = subparsers.add_parser("add_card", help="Add a card to a column")
    add_card_parser.add_argument("--column-id", required=True, help="ID of the column to add a card")

    # Edit Column Title command
    edit_column_title_parser = subparsers.add_parser("edit_column_title", help="Edit the title of a column")
    edit_column_title_parser.add_argument("--column-id", required=True, help="ID of the column")
    edit_column_title_parser.add_argument("--title", required=True, help="New title for the column")

    # Edit Card Title command
    edit_card_title_parser = subparsers.add_parser("edit_card_title", help="Edit the title of a card")
    edit_card_title_parser.add_argument("--card-id", required=True, help="ID of the card")
    edit_card_title_parser.add_argument("--title", required=True, help="New title for the card")

    # Edit Card Content command
    edit_card_content_parser = subparsers.add_parser("edit_card_content", help="Edit the content of a card")
    edit_card_content_parser.add_argument("--card-id", required=True, help="ID of the card")
    edit_card_content_parser.add_argument("--content", required=True, help="New content for the card")

    get_state_parser = subparsers.add_parser("get_state", help="Get the state of a board")
    get_state_parser.add_argument("--board-id", required=True, help="ID of the board")

    # Parse the arguments
    args = parser.parse_args()

    # Instantiate the ProjectManagementApp
    app = ProjectManagementApp()

    if args.command == "create_board":
        board_id = app.create_board()
        print(f"Board created with ID: {board_id}")

    elif args.command == "edit_board_title":
        app.edit_board_title(args.board_id, args.title)
        print(f"Board {args.board_id} title updated to {args.title}")

    elif args.command == "add_column":
        column_id = app.add_column(args.board_id)
        print(f"Column added to board {args.board_id} with ID: {column_id}")

    elif args.command == "remove_column":
        app.remove_column(args.board_id, args.column_id)
        print(f"Column {args.column_id} removed from board {args.board_id}")

    elif args.command == "add_card":
        card_id = app.add_card_to_column(args.column_id)
        print(f"Card added to column {args.column_id} with ID: {card_id}")

    elif args.command == "edit_column_title":
        app.edit_column_title(args.column_id, args.title)
        print(f"Column {args.column_id} title updated to {args.title}")

    elif args.command == "edit_card_title":
        app.edit_card_title(args.card_id, args.title)
        print(f"Card {args.card_id} title updated to {args.title}")

    elif args.command == "edit_card_content":
        app.edit_card_content(args.card_id, args.content)
        print(f"Card {args.card_id} content updated to {args.content}")

    elif args.command == "get_state":
        board = app.board_as_dict(args.board_id)
        print(board)


if __name__ == "__main__":
    main()
