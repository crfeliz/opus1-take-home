import React, {useState} from 'react'
import Card from './Card.jsx'
import {EditText} from 'react-edit-text'
import 'react-edit-text/dist/index.css'

export default function Column({
    col,
    colIndex,
    boardId,
    removeColumn,
    moveColumn,
    fetchBoard,
    API_BASE_URL,
    dragType,
    setDragType
}) {
    // For remove-button
    const [isColumnHovered, setIsColumnHovered] = useState(false)
    const [isAnyCardHovered, setIsAnyCardHovered] = useState(false)

    // 'left' or 'right' or null
    const [dropPosition, setDropPosition] = useState(null)

    const handleColumnMouseEnter = () => setIsColumnHovered(true)
    const handleColumnMouseLeave = () => {
        setIsColumnHovered(false)
        setDropPosition(null)
    }

    const handleCardHoverChange = (hovered) => setIsAnyCardHovered(hovered)

    // Edit column title
    const updateColumnTitle = async (newVal) => {
        if (!boardId || !col.id || !newVal.trim()) return
        await fetch(`${API_BASE_URL}/edit_column_title`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({board_id: boardId, column_id: col.id, title: newVal}),
        })
        fetchBoard(boardId)
    }

    // Add card
    const addCard = async () => {
        if (!boardId || !col.id) return
        await fetch(`${API_BASE_URL}/add_card_to_column`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({board_id: boardId, column_id: col.id}),
        })
        fetchBoard(boardId)
    }

    // DRAG & DROP for columns
    const handleColumnDragStart = (e) => {
        setDragType('column')
        e.dataTransfer.setData('payload', JSON.stringify({
            type: 'column',
            columnId: col.id
        }))
    }

    const handleColumnDragEnd = () => {
        setDragType(null)
    }

    const handleColumnDragOver = (e) => {
        e.preventDefault()
        if (dragType !== 'column') return

        const rect = e.currentTarget.getBoundingClientRect()
        const x = e.clientX - rect.left
        if (x < rect.width / 2) {
            setDropPosition('left')
        } else {
            setDropPosition('right')
        }
    }

    const handleColumnDragLeave = () => {
        setDropPosition(null)
    }

    const handleColumnDrop = (e) => {
        e.preventDefault()
        if (dragType !== 'column') return

        const dataStr = e.dataTransfer.getData('payload')
        if (!dataStr) return
        const data = JSON.parse(dataStr)
        if (data.type !== 'column') return

        const newIndex = dropPosition === 'left' ? colIndex : colIndex + 1
        moveColumn(data.columnId, newIndex)
        setDropPosition(null)
        setDragType(null)
    }

    // If column is empty => special drop zone for cards
    const handleEmptyColumnDragOver = (e) => e.preventDefault()

    const handleEmptyColumnDrop = async (e) => {
        e.preventDefault()
        if (dragType !== 'card') return

        const dataStr = e.dataTransfer.getData('payload')
        if (!dataStr) return
        const data = JSON.parse(dataStr)
        if (data.type !== 'card') return

        // Insert at index=0
        await fetch(`${API_BASE_URL}/move_card`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                board_id: boardId,
                from_column_id: data.fromColumnId,
                to_column_id: col.id,
                card_id: data.cardId,
                new_index: 0,
            }),
        })
        fetchBoard(boardId)
        setDragType(null)
    }

    // SHIFT the "visual" column, not the bounding container
    let translateOffset = '0px'
    if (dropPosition === 'left') {
        translateOffset = '10px' // visually shift right
    } else if (dropPosition === 'right') {
        translateOffset = '-10px' // visually shift left
    }

    return (
        // bounding box = droppable area (no margin so it touches neighbors)
        <div
            style={{
                display: 'inline-block',
                verticalAlign: 'top',
                width: '270px',    // bounding width (slightly bigger to allow visual margin inside)
                minHeight: '200px',
                margin: 0,         // no margin, so bounding boxes are flush
                padding: 0,
                position: 'relative',
                backgroundColor: "transparent",
                zIndex: 1 // this prevents the dragged item  from rendering a background color
            }}
            draggable
            onDragStart={handleColumnDragStart}
            onDragEnd={handleColumnDragEnd}
            onDragOver={handleColumnDragOver}
            onDragLeave={handleColumnDragLeave}
            onDrop={handleColumnDrop}
            onMouseEnter={handleColumnMouseEnter}
            onMouseLeave={handleColumnMouseLeave}
        >
            <div
                className="column-visual"
                style={{
                    background: '#333',
                    borderRadius: '4px',
                    margin: '0 5px',      // <== VISUAL SPACE
                    padding: '1rem',
                    transition: 'transform 0.2s ease',
                    transform: `translateX(${translateOffset})`,
                    borderLeft: dropPosition === 'left' ? '4px solid yellow' : 'none',
                    borderRight: dropPosition === 'right' ? '4px solid yellow' : 'none',
                }}
            >

                {/* Column Title & Remove */}


                    <div className="d-flex align-items-center justify-content-between mb-2">
                        <EditText
                            defaultValue={col.title || 'Untitled Column'}
                            onSave={(data) => updateColumnTitle(data.value)}
                            className="edit-text text-info h3"
                            inputClassName="editing-text"
                        />
                        <button
                            className="close-btn btn d-flex align-items-center justify-content-center"
                            onClick={() => removeColumn(col.id)}
                            style={{
                                width: '22px',
                                height: '22px',
                                paddingBottom: '8px',
                                visibility: (isColumnHovered && !isAnyCardHovered) ? 'visible' : 'hidden',
                                backgroundColor: 'transparent',
                                border: 'none',
                                color: 'rgb(187,187,187)',
                                transition: 'background-color 0.2s ease-in-out'
                            }}
                        >
                            &times;
                        </button>

                    </div>



            {(!col.cards || col.cards.length === 0) && dragType === 'card' && (
                    <div
                        style={{
                            minHeight: '50px',
                            border: '2px dashed #bbb',
                            borderRadius: '5px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: '#bbb',
                            marginBottom: '1rem'
                        }}
                        onDragOver={handleEmptyColumnDragOver}
                        onDrop={handleEmptyColumnDrop}
                    >
                        Drop card here
                    </div>
                )}

                {/* Cards */}
                {col.cards && col.cards.map((card, cardIndex) => (
                    <Card
                        key={card.id}
                        card={card}
                        cardIndex={cardIndex}
                        boardId={boardId}
                        colId={col.id}
                        fetchBoard={fetchBoard}
                        API_BASE_URL={API_BASE_URL}
                        onHoverChange={handleCardHoverChange}
                        dragType={dragType}
                        setDragType={setDragType}
                    />
                ))}

                {/* Add Card button */}
                <div
                    style={{
                        height: '50px',
                        background: '#444',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        marginTop: '1rem'
                    }}
                    onClick={addCard}
                >
                    <span style={{color: '#bbb', fontSize: '1.2rem'}}>+</span>
                </div>
            </div>
        </div>
    )
}
