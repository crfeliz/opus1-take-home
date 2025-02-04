import React, { useState, useEffect } from 'react';
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

  // Add Column / Card
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

  // --------------------
  // DRAG & DROP - Columns
  // --------------------

  // store payload in dataTransfer
  const onDragStartColumn = (e, columnId) => {
     const payload = { columnId };
    e.dataTransfer.setData('payload', JSON.stringify(payload));
  };

  // must prevent default for onDragOver or drop won't fire
  const onDragOver = (e) => {
    e.preventDefault();
  };

  // reorder serverside then fetch and rerender
  const onDropColumn = async (e, dropIndex) => {
    const payloadStr = e.dataTransfer.getData('payload');
    if (!payloadStr) return;
    const payload = JSON.parse(payloadStr);

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
          <h2>{boardData.title || 'Untitled Board'}</h2>
          <button className="btn btn-light mb-2" onClick={addColumn}>
            + Add Column
          </button>

          <div className="d-flex flex-row flex-wrap">
            {boardData.columns &&
              boardData.columns.map((col, colIndex) => (
                <div
                  key={col.id}
                  className="bg-secondary text-white p-3 me-3 rounded"
                  style={{ width: '200px' }}
                  draggable // Make column draggable
                  onDragStart={(e) => onDragStartColumn(e, col.id)} // capture info of what we're dragging
                  onDragOver={onDragOver} // Must have to allow drop
                  onDrop={(e) => onDropColumn(e, colIndex)} // when we are the drop target our index is the target index
                >
                  <strong>{col.title || 'Untitled Column'}</strong>
                  <div className="mt-2">
                    <button
                      className="btn btn-sm btn-light"
                      onClick={() => addCard(col.id)}
                    >
                      + Add Card
                    </button>
                    {col.cards &&
                      col.cards.map((card) => (
                        <div key={card.id} className="card mt-2">
                          <div className="card-body p-2">
                            {card.title || 'Untitled Card'}
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              ))}

            {/* drop zone at the end for reordering columns to last */}
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
