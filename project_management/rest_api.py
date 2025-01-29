from flask import Flask, request, jsonify, render_template
from project_management.project_management import ProjectManagementApp

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Create an instance of ProjectManagementApp
app_instance = ProjectManagementApp()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/create_board', methods=['POST'])
def create_board():
    board_id = app_instance.create_board()
    return jsonify({"board_id": board_id}), 201


@app.route('/edit_board_title', methods=['PUT'])
def edit_board_title():
    data = request.get_json()
    board_id = data.get('board_id')
    title = data.get('title')
    app_instance.edit_board_title(board_id, title)
    return jsonify({"message": "Board title updated"})


@app.route('/add_column_to_board', methods=['POST'])
def add_column_to_board():
    data = request.get_json()
    board_id = data.get('board_id')
    column_id = app_instance.add_column_to_board(board_id)
    return jsonify({"column_id": column_id}), 201


@app.route('/remove_column_from_board', methods=['DELETE'])
def remove_column_from_board():
    data = request.get_json()
    board_id = data.get('board_id')
    column_id = data.get('column_id')
    app_instance.remove_column_from_board(board_id, column_id)
    return jsonify({"message": "Column removed from board"})


@app.route('/move_column_within_board', methods=['PUT'])
def move_column_within_board():
    data = request.get_json()
    board_id = data.get('board_id')
    column_id = data.get('column_id')
    new_index = int(data.get('new_index'))
    app_instance.move_column_within_board(board_id, column_id, new_index)
    return jsonify({"message": "Column moved within board"})


@app.route('/edit_column_title', methods=['PUT'])
def edit_column_title():
    data = request.get_json()
    column_id = data.get('column_id')
    title = data.get('title')
    app_instance.edit_column_title(column_id, title)
    return jsonify({"message": "Column title updated"})


@app.route('/add_card_to_column', methods=['POST'])
def add_card_to_column():
    data = request.get_json()
    column_id = data.get('column_id')
    card_id = app_instance.add_card_to_column(column_id)
    return jsonify({"card_id": card_id}), 201


@app.route('/remove_card_from_column', methods=['DELETE'])
def remove_card_from_column():
    data = request.get_json()
    column_id = data.get('column_id')
    card_id = data.get('card_id')
    app_instance.remove_card_from_column(column_id, card_id)
    return jsonify({"message": "Card removed from column"})


@app.route('/move_card', methods=['PUT'])
def move_card():
    data = request.get_json()
    from_column_id = data.get('from_column_id')
    to_column_id = data.get('to_column_id')
    card_id = data.get('card_id')
    new_index = int(data.get('new_index'))
    app_instance.move_card(from_column_id, to_column_id, card_id, new_index)
    return jsonify({"message": "Card moved within column"})


@app.route('/edit_card_title', methods=['PUT'])
def edit_card_title():
    data = request.get_json()
    card_id = data.get('card_id')
    title = data.get('title')
    app_instance.edit_card_title(card_id, title)
    return jsonify({"message": "Card title updated"})


@app.route('/edit_card_content', methods=['PUT'])
def edit_card_content():
    data = request.get_json()
    card_id = data.get('card_id')
    content = data.get('content')
    app_instance.edit_card_content(card_id, content)
    return jsonify({"message": "Card content updated"})


@app.route('/board_as_dict', methods=['GET'])
def board_as_dict():
    board_id = request.args.get('board_id')
    board = app_instance.board_as_dict(board_id)
    return jsonify(board)
