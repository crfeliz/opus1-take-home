from uuid import UUID

from flask import Flask, request, jsonify
from flask_cors import CORS

from project_management.project_management_app import ProjectManagementApp

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"])
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app_instance = ProjectManagementApp()


@app.errorhandler(Exception)
def handle_exception(e):
    response = jsonify(message=str(e))
    print(e)
    response.status_code = 500
    return response


# ---------------------- BOARD ----------------------
@app.route('/create_board', methods=['POST'])
def create_board():
    board_id = app_instance.create_board()
    return jsonify({"board_id": board_id}), 201


@app.route('/edit_board_title', methods=['PUT'])
def edit_board_title():
    data = request.get_json()
    board_id = UUID(data.get('board_id'))
    title = data.get('title')
    app_instance.edit_board_title(board_id, title)
    return jsonify({"message": "Board title updated"})


@app.route('/board_as_dict', methods=['GET'])
def board_as_dict():
    print("RENDER START")
    board_id = UUID(request.args.get('board_id'))
    try:
        board = app_instance.board_as_dict(board_id)
        print("RENDER END")
        return jsonify(board)
    except Exception as e:
        print(e)
        return jsonify({"message": "Board not found"})


# ---------------------- COLUMN ----------------------
@app.route('/add_column_to_board', methods=['POST'])
def add_column_to_board():
    data = request.get_json()
    board_id = UUID(data.get('board_id'))
    try:
        print(app_instance)
        print(app_instance.add_column)
        column_id = str(app_instance.add_column(board_id))
    except Exception as e:
        print(e)
    print(4)
    return jsonify({"column_id": column_id}), 201


@app.route('/remove_column_from_board', methods=['DELETE'])
def remove_column_from_board():
    data = request.get_json()
    board_id = UUID(data.get('board_id'))
    column_id = UUID(data.get('column_id'))
    app_instance.remove_column(board_id, column_id)
    return jsonify({"message": "Column removed from board"})


@app.route('/move_column_within_board', methods=['PUT'])
def move_column_within_board():
    data = request.get_json()
    board_id = UUID(data.get('board_id'))
    column_id = UUID(data.get('column_id'))
    new_index = int(data.get('new_index'))
    app_instance.move_column(board_id, column_id, new_index)
    return jsonify({"message": "Column moved within board"})


@app.route('/edit_column_title', methods=['PUT'])
def edit_column_title():
    data = request.get_json()
    board_id = UUID(data.get('board_id'))
    column_id = UUID(data.get('column_id'))
    title = data.get('title')
    app_instance.edit_column_title(board_id, column_id, title)
    return jsonify({"message": "Column title updated"})


# ---------------------- CARD ----------------------
@app.route('/add_card_to_column', methods=['POST'])
def add_card_to_column():
    data = request.get_json()
    board_id = UUID(data.get('board_id'))
    column_id = UUID(data.get('column_id'))
    card_id = str(app_instance.add_card(board_id, column_id))
    return jsonify({"card_id": card_id}), 201


@app.route('/remove_card_from_column', methods=['DELETE'])
def remove_card_from_column():
    data = request.get_json()
    board_id = UUID(data.get('board_id'))
    column_id = UUID(data.get('column_id'))
    card_id = UUID(data.get('card_id'))
    app_instance.remove_card(board_id, column_id, card_id)
    return jsonify({"message": "Card removed from column"})


@app.route('/move_card', methods=['PUT'])
def move_card():
    data = request.get_json()
    board_id = UUID(data.get('board_id'))
    from_column_id = UUID(data.get('from_column_id'))
    to_column_id = UUID(data.get('to_column_id'))
    card_id = UUID(data.get('card_id'))
    new_index = int(data.get('new_index'))
    app_instance.move_card(board_id, from_column_id, to_column_id, card_id, new_index)
    return jsonify({"message": "Card moved"})


@app.route('/edit_card_title', methods=['PUT'])
def edit_card_title():
    data = request.get_json()
    board_id = UUID(data.get('board_id'))
    column_id = UUID(data.get('column_id'))
    card_id = UUID(data.get('card_id'))
    title = data.get('title')
    app_instance.edit_card_title(board_id, column_id, card_id, title)
    return jsonify({"message": "Card title updated"})


@app.route('/edit_card_content', methods=['PUT'])
def edit_card_content():
    data = request.get_json()
    board_id = UUID(data.get('board_id'))
    column_id = UUID(data.get('column_id'))
    card_id = UUID(data.get('card_id'))
    content = data.get('content')
    app_instance.edit_card_content(board_id, column_id, card_id, content)
    return jsonify({"message": "Card content updated"})


@app.route('/undo', methods=['POST'])
def undo():
    print("UNDO_START")
    data = request.get_json()
    board_id = UUID(data.get('board_id'))
    app_instance.undo(board_id)
    print("UNDO_END")
    return jsonify({"message": "Board undo"})


@app.route('/redo', methods=['POST'])
def redo():
    data = request.get_json()
    board_id = UUID(data.get('board_id'))
    print("1")
    try:
        print("2")
        app_instance.redo(board_id)
        return jsonify({"message": "Board redo"})
    except Exception as e:
        print("3")
        print(e)
        return jsonify({"message": f"{e}"})
