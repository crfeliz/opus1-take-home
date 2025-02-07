import React, {useState} from 'react'
import {EditText} from 'react-edit-text'
import 'react-edit-text/dist/index.css'

export default function Card({
                                 card,
                                 cardIndex,
                                 boardId,
                                 colId,
                                 fetchBoard,
                                 API_BASE_URL,
                                 onHoverChange,
                                 dragType,
                                 setDragType
                             }) {
    const [isHovered, setIsHovered] = useState(false)
    const [dropPosition, setDropPosition] = useState(null) // 'above' or 'below'

    const handleMouseEnter = () => {
        setIsHovered(true)
        onHoverChange(true)
    }
    const handleMouseLeave = () => {
        setIsHovered(false)
        onHoverChange(false)
        setDropPosition(null)
    }

    // Remove card
    const removeCard = async () => {
        if (!boardId || !colId || !card.id) return
        await fetch(`${API_BASE_URL}/remove_card_from_column`, {
            method: 'DELETE',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({board_id: boardId, column_id: colId, card_id: card.id}),
        })
        fetchBoard(boardId)
    }

    // Update card title
    const updateCardTitle = async (newVal) => {
        if (!boardId || !colId || !card.id || !newVal.trim()) return
        await fetch(`${API_BASE_URL}/edit_card_title`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                board_id: boardId,
                column_id: colId,
                card_id: card.id,
                title: newVal,
            }),
        })
        fetchBoard(boardId)
    }

    // Update card content
    const updateCardContent = async (newVal) => {
        if (!boardId || !colId || !card.id) return
        await fetch(`${API_BASE_URL}/edit_card_content`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                board_id: boardId,
                column_id: colId,
                card_id: card.id,
                content: newVal,
            }),
        })
        fetchBoard(boardId)
    }

    // DRAG & DROP
    const handleDragStart = (e) => {
        e.stopPropagation()
        setDragType('card')
        e.dataTransfer.setData('payload', JSON.stringify({
            type: 'card',
            fromColumnId: colId,
            cardId: card.id,
        }))
    }

    const handleDragEnd = () => {
        setDragType(null)
    }

    const handleDragOver = (e) => {
        e.preventDefault()
        if (dragType !== 'card') return

        const rect = e.currentTarget.getBoundingClientRect()
        const y = e.clientY - rect.top
        if (y < rect.height / 2) {
            setDropPosition('above')
        } else {
            setDropPosition('below')
        }
    }

    const handleDragLeave = () => {
        setDropPosition(null)
    }

    const handleDrop = async (e) => {
        e.preventDefault()
        if (dragType !== 'card') return

        const dataStr = e.dataTransfer.getData('payload')
        if (!dataStr || !boardId) return
        const data = JSON.parse(dataStr)
        if (data.type !== 'card') return

        // If "above", newIndex = cardIndex
        // If "below", newIndex = cardIndex + 1
        const newIndex = (dropPosition === 'above') ? cardIndex : (cardIndex + 1)

        await fetch(`${API_BASE_URL}/move_card`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                board_id: boardId,
                from_column_id: data.fromColumnId,
                to_column_id: colId,
                card_id: data.cardId,
                new_index: newIndex,
            }),
        })
        fetchBoard(boardId)

        setDropPosition(null)
        setDragType(null)
    }

    // SHIFT only the visual portion
    let translateOffset = '0px'
    if (dropPosition === 'above') {
        translateOffset = '10px'
    } else if (dropPosition === 'below') {
        translateOffset = '-10px'
    }

    return (
        // bounding container => droppable area. 0 margin so bounding boxes meet
        <div
            style={{
                position: 'relative',
                margin: '-1', // negative margin causes slight overlap to prevent jitter when dropping precisely between.
                minHeight: '116px'
            }}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
        >
            <div
                className="card-visual"
                style={{
                    position: 'relative',
                    background: '#222',
                    borderRadius: '4px',
                    padding: '8px',
                    transition: 'transform 0.2s ease',
                    transform: `translateY(${translateOffset})`,
                }}
                draggable
                onDragStart={handleDragStart}
                onDragEnd={handleDragEnd}
            >
                {/* highlight bar if "above" */}
                {dropPosition === 'above' && (
                    <div
                        style={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: '100%',
                            height: '5px',
                            background: 'yellow',
                            borderRadius: '2px'
                        }}
                    />
                )}

                <style>
                    {`
            .close-btn:hover {
              background-color: #ff7074 !important;
            }
          `}
                </style>

                <h5 className="text-info">
                    <div className="d-flex justify-content-between align-items-center">
                        <EditText
                            defaultValue={card.title || 'Untitled Card'}
                            onSave={(data) => updateCardTitle(data.value)}
                            className="edit-text"
                            inputClassName="editing-text"
                            multiline
                        />
                        <button
                            className="close-btn btn btn-sm rounded-circle"
                            onClick={removeCard}
                            style={{
                                width: '2rem',
                                height: '2rem',
                                visibility: isHovered ? 'visible' : 'hidden',
                                backgroundColor: 'transparent',
                                border: 'none',
                                color: 'inherit',
                                transition: 'background-color 0.2s ease-in-out'
                            }}
                        >
                            ✖️
                        </button>
                    </div>
                </h5>
                <div className="mt-1">
                    <EditText
                        defaultValue={card.content || 'No content'}
                        onSave={(data) => updateCardContent(data.value)}
                        className="edit-text"
                        inputClassName="editing-text"
                        multiline
                    />
                </div>

                {/* highlight bar if "below" */}
                {dropPosition === 'below' && (
                    <div
                        style={{
                            position: 'absolute',
                            bottom: 0,
                            left: 0,
                            width: '100%',
                            height: '5px',
                            background: 'yellow',
                            borderRadius: '2px'
                        }}
                    />
                )}
            </div>
        </div>
    )
}
