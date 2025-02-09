const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000';

const handleResponse = async (response) => {
  if (!response.ok) throw new Error('Network response was not ok');
  return response.json();
};

export const boardService = {
  create: () => fetch(`${API_BASE_URL}/create_board`, {
    method: 'POST'
  }).then(handleResponse),

  get: (id) => fetch(`${API_BASE_URL}/board_as_dict?board_id=${id}`)
    .then(handleResponse),

  updateTitle: (id, title) => fetch(`${API_BASE_URL}/edit_board_title`, {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ board_id: id, title }),
  }).then(handleResponse),
};

export const columnService = {
  add: (boardId) => fetch(`${API_BASE_URL}/add_column_to_board`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ board_id: boardId }),
  }).then(handleResponse),

  remove: (boardId, columnId) => fetch(`${API_BASE_URL}/remove_column_from_board`, {
    method: 'DELETE',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ board_id: boardId, column_id: columnId }),
  }).then(handleResponse),

  move: (boardId, columnId, newIndex) => fetch(`${API_BASE_URL}/move_column_within_board`, {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      board_id: boardId,
      column_id: columnId,
      new_index: newIndex
    }),
  }).then(handleResponse),

  updateTitle: (boardId, columnId, title) => fetch(`${API_BASE_URL}/edit_column_title`, {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      board_id: boardId,
      column_id: columnId,
      title
    }),
  }).then(handleResponse),
};

export const cardService = {
  add: (boardId, columnId) => fetch(`${API_BASE_URL}/add_card_to_column`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ board_id: boardId, column_id: columnId }),
  }).then(handleResponse),

  remove: (boardId, columnId, cardId) => fetch(`${API_BASE_URL}/remove_card_from_column`, {
    method: 'DELETE',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      board_id: boardId,
      column_id: columnId,
      card_id: cardId
    }),
  }).then(handleResponse),

  move: (boardId, fromColumnId, toColumnId, cardId, newIndex) =>
    fetch(`${API_BASE_URL}/move_card`, {
      method: 'PUT',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        board_id: boardId,
        from_column_id: fromColumnId,
        to_column_id: toColumnId,
        card_id: cardId,
        new_index: newIndex
      }),
    }).then(handleResponse),

  updateTitle: (boardId, columnId, cardId, title) =>
    fetch(`${API_BASE_URL}/edit_card_title`, {
      method: 'PUT',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        board_id: boardId,
        column_id: columnId,
        card_id: cardId,
        title
      }),
    }).then(handleResponse),

  updateContent: (boardId, columnId, cardId, content) =>
    fetch(`${API_BASE_URL}/edit_card_content`, {
      method: 'PUT',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        board_id: boardId,
        column_id: columnId,
        card_id: cardId,
        content
      }),
    }).then(handleResponse),
};