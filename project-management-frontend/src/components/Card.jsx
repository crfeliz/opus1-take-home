import React, {useState} from 'react'
import {EditText, EditTextarea} from 'react-edit-text'
import 'react-edit-text/dist/index.css'
import {cardService} from "../services/services.js";

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
    const [currentDragTargetId, setCurrentDragTargetId] = useState(null)
    const [isEditing, setIsEditing] = useState(false);


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
        await cardService.remove(boardId, colId, card.id)
        await fetchBoard(boardId)
    }

    // Update card title
    const updateCardTitle = async (newVal) => {
        if (!boardId || !colId || !card.id || !newVal.trim()) return
        await cardService.updateTitle(boardId, colId, card.id, newVal.trim())
        await fetchBoard(boardId)
    }

    // Update card content
    const updateCardContent = async (newVal) => {
        if (!boardId || !colId || !card.id) return
        await cardService.updateContent(boardId, colId, card.id, newVal)
        await fetchBoard(boardId)
    }

    // DRAG & DROP
    const handleDragStart = (e) => {
        e.stopPropagation()
        if (isEditing) {
            e.preventDefault()
            return
        }

        setDragType('card')
        e.dataTransfer.setData('payload', JSON.stringify({
            type: 'card',
            fromColumnId: colId,
            cardId: card.id,
        }))

        // timeout to give the browser time to generate the drag ghost
        setTimeout(() => {
            setCurrentDragTargetId(card.id)
        }, 0)

    }

    const handleDragEnd = (e) => {
        setDragType(null)
        setCurrentDragTargetId(null)
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

        await cardService.move(boardId, data.fromColumnId, colId, data.cardId, newIndex)
        await fetchBoard(boardId)

        setDropPosition(null)
        setDragType(null)
    }

    let isBeingDragged = card.id === currentDragTargetId;

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
                margin: '-1px', // negative margin causes slight overlap to prevent jitter when dropping precisely between.
                height: '140px',
                visibility: isBeingDragged ? 'hidden' : 'visible'
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
                <button
                    className="close-btn btn d-flex align-items-center justify-content-center"
                    onClick={removeCard}
                    style={{
                        width: '22px',
                        height: '22px',
                        paddingBottom: '8px',
                        visibility: isHovered && !isBeingDragged ? 'visible' : 'hidden',
                        backgroundColor: 'transparent',
                        border: 'none',
                        color: 'rgb(187,187,187)',
                        transition: 'background-color 0.2s ease-in-out',
                        float: 'right'
                    }}
                >
                    &times;
                </button>
                <div className="d-flex justify-content-between align-items-center">
                    <EditText
                        defaultValue={card.title || 'Untitled'}
                        onSave={(data) => updateCardTitle(data.value)}
                        onEditMode={() => setIsEditing(true)}
                        onBlur={() => setIsEditing(false)}
                        className="edit-text text-info h5"
                        inputClassName="editing-text"
                        style={{ maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}

                    />
                </div>

                <div className="mt-1">
                    <EditTextarea
                        defaultValue={card.content || 'No content'}
                        onSave={(data) => updateCardContent(data.value)}
                        onEditMode={() => setIsEditing(true)}
                        onBlur={() => setIsEditing(false)}
                        className="edit-text edit-content"
                        inputClassName="editing-text"
                        rows={2}
                    />
                </div>
            </div>
        </div>
    )
}
