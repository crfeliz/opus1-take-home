import React, {useState, useEffect} from 'react'
import Column from './Column.jsx'
import {EditText} from 'react-edit-text'
import 'react-edit-text/dist/index.css'
import {boardService, columnService} from "../services/services.js";


export default function Board() {
    const [boardId, setBoardId] = useState(null)
    const [boardData, setBoardData] = useState(null)
    const [loadBoardId, setLoadBoardId] = useState('')
    const [dragStartInfo, setDragStartInfo] = useState({}) // 'card' | 'column' | null

    // CREATE / LOAD
    const createBoard = async () => {
        const data = await boardService.create()
        setBoardId(data.board_id)
    }

    const loadExistingBoard = () => {
        if (!loadBoardId.trim()) return
        setBoardId(loadBoardId.trim())
    }

    const fetchBoard = async (id = null) => {
        if (!id) return
        const data = await boardService.get(id)
        setBoardData(data.board)
    }

    useEffect(() => {
        if (boardId) {
            fetchBoard(boardId).catch((err) => console.log("Load board failed", err))
        }
    }, [boardId])

    // Edit board title
    const updateBoardTitle = async (newVal) => {
        if (!boardId || !newVal.trim()) return
        await boardService.updateTitle(boardId, newVal.trim())
        await fetchBoard(boardId)
    }

    // Add / Remove columns
    const addColumn = async () => {
        if (!boardId) return
        await columnService.add(boardId)
        await fetchBoard(boardId)
    }

    const removeColumn = async (colId) => {
        if (!boardId || !colId) return
        await columnService.remove(boardId, colId)
        await fetchBoard(boardId)
    }

    // Move columns left/right
    const moveColumn = async (columnId, newIndex) => {
        if (!boardId || !columnId) return
        await columnService.move(boardId, columnId, newIndex)
        await fetchBoard(boardId)
    }

    const undo = async () => {
        if (!boardData) return
        await boardService.undo(boardId)
        await fetchBoard(boardId)
    }

    const redo = async () => {
        if (!boardData) return
        await boardService.redo(boardId)
        await fetchBoard(boardId)
    }

    // Copy board ID
    const copyBoardIdToClipboard = () => {
        if (!boardId) return
        navigator.clipboard.writeText(boardId)
            .then(() => {
                alert('Board ID copied to clipboard!')
            })
            .catch(err => console.error('Failed to copy ID:', err))
    }

    return (
        <div className="vh-100 vw-100 d-flex flex-column"
             style={{background: '#111', color: '#fff'}}
             onDragOver={(e) => e.preventDefault()}> {/* Trick to prevent ghosting bug when dropping items outside of column/card*/}
            {/* Top Bar */}
            <div className="p-3">
                <button className="btn btn-primary me-3" onClick={createBoard}>Create New Board</button>
                <input
                    className="form-control w-auto d-inline-block me-2"
                    placeholder="Existing Board UUID"
                    value={loadBoardId}
                    onChange={(e) => setLoadBoardId(e.target.value)}
                />
                <button className="btn btn-secondary me-2" onClick={loadExistingBoard}>Load Board</button>
                <div className="history-controls w-auto d-inline-block me-2">
                    <button className="btn btn-secondary w-auto d-inline-block me-2" onClick={undo}>&lt;</button>
                    <button className="btn btn-secondary w-auto d-inline-block me-2" onClick={redo}>&gt;</button>
                </div>

                {boardId && (
                    <div className="mt-2">
                        <strong>Current Board ID: </strong>
                        <span
                            style={{textDecoration: 'underline', cursor: 'pointer'}}
                            onClick={copyBoardIdToClipboard}>
                          {boardId}
                        </span>
                    </div>
                )}

                {boardData && (
                    <div className="mt-3">
                        <h2 className="text-info">
                            <EditText
                                defaultValue={boardData.title || 'Untitled Board'}
                                onSave={(data) => updateBoardTitle(data.value)}
                                className="edit-text"
                                inputClassName="editing-text"
                            />
                        </h2>
                    </div>
                )}
            </div>

            {/* Board Content: horizontally scrollable columns */}
            {boardData && boardData.columns && (
                <div
                    style={{
                        flex: 1,
                        overflowX: 'auto',
                        overflowY: 'auto',
                        whiteSpace: 'nowrap', // no wrap
                    }}
                >
                    <div
                        style={{
                            display: 'inline-flex',
                            flexWrap: 'nowrap',
                            padding: '1rem',
                        }}
                    >
                        {boardData.columns.map((col, colIndex) => (
                            <Column
                                key={col.id}
                                col={col}
                                colIndex={colIndex}
                                boardId={boardId}
                                removeColumn={removeColumn}
                                moveColumn={moveColumn}
                                fetchBoard={fetchBoard}
                                dragStartInfo={dragStartInfo}
                                setDragStartInfo={setDragStartInfo}
                                isLastColumn={boardData.columns.length - 1 === colIndex}
                            />
                        ))}

                        {/* Add Column placeholder */}
                        <div
                            style={{
                                display: 'inline-block',
                                verticalAlign: 'top',
                                // bounding box touches adjacent columns
                                // the visual margin will be inside the box
                                width: '50px',
                                minHeight: '200px',
                                background: '#333',
                                cursor: 'pointer',
                                margin: '0', // no margin so no dead space
                            }}
                            onClick={addColumn}
                        >
                            <div
                                style={{
                                    // visual spacing inside
                                    margin: '0 10px',
                                    marginTop: '10px',
                                    borderRadius: '4px',
                                    height: 'calc(100% - 20px)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    color: '#bbb',
                                    fontSize: '1.2rem'
                                }}
                            >
                                +
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
