import React, { useState, useEffect } from 'react';
import { EditText } from 'react-edit-text';
import 'react-edit-text/dist/index.css';
import './index.css';


const API_BASE_URL = 'http://127.0.0.1:5000';

function App() {
  const [boardId, setBoardId] = useState(null);
  const [boardData, setBoardData] = useState(null);
  const [loadBoardId, setLoadBoardId] = useState('');

  // Create / Load board
  const createBoard = async () => {
    const res = await fetch(`${API_BASE_URL}/create_board`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    const data = await res.json();
    setBoardId(data.board_id);
  };

  const loadExistingBoard = () => {
    if (!loadBoardId.trim()) return;
    setBoardId(loadBoardId.trim());
  };

  const fetchBoard = async (id) => {
    const res = await fetch(`${API_BASE_URL}/board_as_dict?board_id=${id}`);
    const data = await res.json();
    setBoardData(data.board);
  };

  useEffect(() => {
    if (boardId) {
      fetchBoard(boardId);
    }
  }, [boardId]);

  // Title editing
  const updateBoardTitle = async (newVal) => {
    if (!boardId || !newVal.trim()) return;
    await fetch(`${API_BASE_URL}/edit_board_title`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ board_id: boardId, title: newVal })
    });
    fetchBoard(boardId);
  };

  const updateColumnTitle = async (colId, newVal) => {
    if (!boardId || !colId || !newVal.trim()) return;
    await fetch(`${API_BASE_URL}/edit_column_title`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ board_id: boardId, column_id: colId, title: newVal })
    });
    fetchBoard(boardId);
  };

  // Adding / Removing
  const addColumn = async () => {
    if (!boardId) return;
    await fetch(`${API_BASE_URL}/add_column_to_board`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ board_id: boardId })
    });
    fetchBoard(boardId);
  };

  const addCard = async (colId) => {
    if (!boardId || !colId) return;
    await fetch(`${API_BASE_URL}/add_card_to_column`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ board_id: boardId, column_id: colId })
    });
    fetchBoard(boardId);
  };

  // Card-level editing
  const updateCardTitle = async (colId, cardId, newVal) => {
    if (!boardId || !colId || !cardId || !newVal.trim()) return;
    await fetch(`${API_BASE_URL}/edit_card_title`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        board_id: boardId,
        column_id: colId,
        card_id: cardId,
        title: newVal
      })
    });
    fetchBoard(boardId);
  };

  const updateCardContent = async (colId, cardId, newVal) => {
    if (!boardId || !colId || !cardId) return;
    await fetch(`${API_BASE_URL}/edit_card_content`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        board_id: boardId,
        column_id: colId,
        card_id: cardId,
        content: newVal
      })
    });
    fetchBoard(boardId);
  };

  const onDragStartColumn = (e, columnId) => {
    const payload = { type: 'column', columnId }; // need to type to differentiate between card and column `drag and drop`
    e.dataTransfer.setData('payload', JSON.stringify(payload));
  };

  const onDragOver = (e) => {
    e.preventDefault();
  };

  const onDropColumn = async (e, dropIndex) => {
    const payloadStr = e.dataTransfer.getData('payload');
    if (!payloadStr) return;
    const payload = JSON.parse(payloadStr);
    if (payload.type !== 'column') return; // ignore if dropping a card

    await fetch(`${API_BASE_URL}/move_column_within_board`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        board_id: boardId,
        column_id: payload.columnId,
        new_index: dropIndex
      })
    });
    fetchBoard(boardId);
  };


  // Card Drag & Drop
  const onDragStartCard = (e, fromColumnId, cardId) => {
    e.stopPropagation(); // prevent the event from reaching the column
    const payload = { type: 'card', fromColumnId, cardId }; // need to type to differentiate between card and column `drag and drop`
    e.dataTransfer.setData('payload', JSON.stringify(payload));
  };

  const onDropCard = async (e, toColumnId, toCardIndex) => {
    e.stopPropagation(); // stop drop from reaching column level
    const payloadStr = e.dataTransfer.getData('payload');
    if (!payloadStr) return;
    const payload = JSON.parse(payloadStr);
    if (payload.type !== 'card') return; // ignore column drops

    await fetch(`${API_BASE_URL}/move_card`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        board_id: boardId,
        from_column_id: payload.fromColumnId,
        to_column_id: toColumnId,
        card_id: payload.cardId,
        new_index: toCardIndex
      })
    });
    fetchBoard(boardId);
  };

  return (
    <div
      className="vh-100 vw-100 d-flex flex-column"
      style={{ background: '#111', color: '#fff' }}
    >
      <div className="p-3">
        <button className="btn btn-primary me-3" onClick={createBoard}>
          Create Board
        </button>
        <input
          className="form-control w-auto d-inline-block me-2"
          placeholder="Existing Board UUID"
          value={loadBoardId}
          onChange={(e) => setLoadBoardId(e.target.value)}
        />
        <button className="btn btn-secondary" onClick={loadExistingBoard}>
          Load Board
        </button>

        {boardId && (
          <div className="mt-3">
            <strong>Board ID:</strong> {boardId}
          </div>
        )}
      </div>

      {boardData && (
        <div className="p-3">
          <h2 style={{ color: '#0bf' }}>
            <EditText
              defaultValue={boardData.title || 'Untitled Board'}
              onSave={(data) => updateBoardTitle(data.value)}
              style={{ background: '#fff', color: '#000', padding: '2px' }}
            />
          </h2>

          <button className="btn btn-light mb-2" onClick={addColumn}>
            + Add Column
          </button>

          <div className="d-flex flex-row flex-wrap">
            {boardData.columns &&
              boardData.columns.map((col, colIndex) => (
                <div
                  key={col.id}
                  className="bg-secondary text-white p-3 me-3 rounded"
                  style={{ width: '220px', position: 'relative' }}
                  draggable
                  onDragStart={(e) => onDragStartColumn(e, col.id)}
                  onDragOver={onDragOver}
                  onDrop={(e) => onDropColumn(e, colIndex)}
                >
                  <div style={{ marginBottom: '6px' }}>
                    <EditText
                      defaultValue={col.title || 'Untitled Column'}
                      onSave={(data) => updateColumnTitle(col.id, data.value)}
                      style={{ background: '#fff', color: '#000' }}
                    />
                  </div>

                  <button
                    className="btn btn-sm btn-light mb-2"
                    onClick={() => addCard(col.id)}
                  >
                    + Add Card
                  </button>

                  {col.cards &&
                    col.cards.map((card, cardIndex) => (
                      <div
                        key={card.id}
                        className="card mb-2"
                        draggable
                        onDragStart={(e) => onDragStartCard(e, col.id, card.id)}
                        onDragOver={onDragOver}
                        onDrop={(e) => onDropCard(e, col.id, cardIndex)}
                        style={{ cursor: 'move' }}
                      >
                        <div className="card-body p-2">
                          <small>
                            <strong>Title: </strong>
                            <EditText
                              defaultValue={card.title || 'Untitled Card'}
                              onSave={(data) =>
                                updateCardTitle(col.id, card.id, data.value)
                              }
                              style={{ background: '#fff', color: '#000' }}
                            />
                          </small>
                          <br />
                          <small>
                            <strong>Content: </strong>
                            <EditText
                              defaultValue={card.content || 'No content'}
                              onSave={(data) =>
                                updateCardContent(col.id, card.id, data.value)
                              }
                              style={{ background: '#f7f7f7', color: '#000' }}
                              multiline
                            />
                          </small>
                        </div>
                      </div>
                    ))}

                  {/* Card drop zone */}
                  <div
                    style={{ height: '20px', background: '#444' }}
                    onDragOver={onDragOver}
                    onDrop={(e) =>
                      onDropCard(e, col.id, col.cards ? col.cards.length : 0)
                    }
                  />
                </div>
              ))}
            {/* Column drop zone */}
            <div
              style={{ width: '40px', background: '#222' }}
              onDragOver={onDragOver}
              onDrop={(e) =>
                onDropColumn(e, boardData.columns.length)
              }
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
