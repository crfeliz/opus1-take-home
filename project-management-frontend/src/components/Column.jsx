import React, {useState} from 'react'
import Card from './Card.jsx'
import {EditText} from 'react-edit-text'
import 'react-edit-text/dist/index.css'
import {cardService, columnService} from "../services/services.js";

export default function Column({
    col,
    colIndex,
    boardId,
    removeColumn,
    moveColumn,
    fetchBoard,
    dragStartInfo,
    setDragStartInfo,
    isLastColumn
}) {
    // For remove-button
    const [isColumnHovered, setIsColumnHovered] = useState(false)
    const [isAnyCardHovered, setIsAnyCardHovered] = useState(false)

    // 'before' or 'after' or null
    const [dropPosition, setDropPosition] = useState(null)
    const [isEditing, setIsEditing] = useState(false);

    const handleColumnMouseEnter = () => {
        setIsColumnHovered(true)
    }
    const handleColumnMouseLeave = () => {
        setIsColumnHovered(false)
        setDropPosition(null)
    }

    const handleCardHoverChange = (hovered) => setIsAnyCardHovered(hovered)

    // Edit column title
    const updateColumnTitle = async (newVal) => {
        if (!boardId || !col.id || !newVal.trim()) return
        await columnService.updateTitle(boardId, col.id, newVal.trim())
        await fetchBoard(boardId)
    }

    // Add card
    const addCard = async () => {
        if (!boardId || !col.id) return
        await cardService.add(boardId, col.id)
        await fetchBoard(boardId)
    }

    // DRAG & DROP for columns
    const handleColumnDragStart = (e) => {
        if (isEditing) {
            e.preventDefault()
            return
        }

        // timeout to give the browser time to generate the drag ghost
        setTimeout(() => {
            setDragStartInfo({type: 'column', id: col.id, index: colIndex})
        }, 0)

    }

    const handleColumnDragEnd = () => {
        setDragStartInfo({})
    }

    const handleColumnDragOver = (e) => {
        e.preventDefault()
        if (dragStartInfo.type !== 'column') return

        const rect = e.currentTarget.getBoundingClientRect()
        const x = e.clientX - rect.left
        const isBefore = x < rect.width / 2;

        // Prevent shift animation when the column being dragged wouldn't change positions
        const noMovementIndex = isBefore ? colIndex - 1 : colIndex + 1;
        if (dragStartInfo.index === noMovementIndex) return;

        setDropPosition(isBefore ? 'before' : 'after');
    }

    const handleColumnDragLeave = () => {
        setDropPosition(null)
    }

    const handleColumnDrop = (e) => {
        e.preventDefault()
        if (dragStartInfo.type !== 'column') return

        const newIndex = dropPosition === 'before' ? colIndex : colIndex + 1
        moveColumn(dragStartInfo.id, newIndex)
        setDropPosition(null)
        setDragStartInfo({})
    }

    // If column is empty => special drop zone for cards
    const handleEmptyColumnDragOver = (e) => e.preventDefault()

    const handleEmptyColumnDrop = async (e) => {
        e.preventDefault()
        if (dragStartInfo.type !== 'card') return

        await cardService.move(boardId, dragStartInfo.fromColumnId, col.id, dragStartInfo.id, 0)
        await fetchBoard(boardId)
        setDragStartInfo({})
    }

    let isBeingDragged = col.id === dragStartInfo.id;

    // SHIFT the "visual" column, not the bounding container
    let translateOffset = '0px'
    if (dropPosition === 'before') {
        translateOffset = '10px' // visually shift right
    } else if (dropPosition === 'after') {
        translateOffset = '-10px' // visually shift left
    }

    if (isAnyCardHovered && col.cards.length === 0) {
        setIsAnyCardHovered(false) // fix edge case when dragging last card from column.
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
                paddingRight: isLastColumn ? '5px' : "0",
                position: 'relative',
                backgroundColor: "transparent",
                visibility: isBeingDragged ? 'hidden' : 'visible',
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
                }}
            >
                {/* Remove */}
                <button
                    className="close-btn btn d-flex align-items-center justify-content-center"
                    onClick={() => removeColumn(col.id)}
                    style={{
                        width: '22px',
                        height: '22px',
                        paddingBottom: '8px',
                        visibility: (isColumnHovered && !isAnyCardHovered && !isBeingDragged) ? 'visible' : 'hidden',
                        backgroundColor: 'transparent',
                        border: 'none',
                        color: 'rgb(187,187,187)',
                        transition: 'background-color 0.2s ease-in-out',
                        float: 'right'
                    }}
                >
                    &times;
                </button>
                {/* Column Title */}
                <div className="d-flex align-items-center justify-content-between mb-2">
                    <EditText
                        defaultValue={col.title || 'Untitled'}
                        onSave={(data) => updateColumnTitle(data.value)}
                        onEditMode={() => setIsEditing(true)}
                        onBlur={() => setIsEditing(false)}
                        className="edit-text text-info h3"
                        inputClassName="editing-text"
                        style={{ maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}
                    />
                </div>


                {(!col.cards || col.cards.length === 0) && dragStartInfo.type === 'card' && (
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
                        onHoverChange={handleCardHoverChange}
                        dragStartInfo={dragStartInfo}
                        setDragStartInfo={setDragStartInfo}
                        parentColumnIsBeingDragged={isBeingDragged}
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
                        marginTop: '0'
                    }}
                    onClick={addCard}
                >
                    <span style={{color: '#bbb', fontSize: '1.2rem'}}>+</span>
                </div>
            </div>
        </div>
    )
}
