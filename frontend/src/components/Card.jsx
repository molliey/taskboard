import React, { useState, useRef, useEffect } from "react";
// 移除本地 mock 用户来源，显示逻辑改为后端返回的 name

const Card = ({ task, onDelete, onMove, onUpdate, availableColumns, currentColumn }) => {
  const [showMenu, setShowMenu] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [showAssigneeInfo, setShowAssigneeInfo] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editTask, setEditTask] = useState({
    title: task.title || '',
    description: task.description || '',
    due_date: task.due_date || '',
    assignee_id: task.assignee_id ?? 0,
  });
  const menuRef = useRef(null);
  const assigneeRef = useRef(null);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setShowMenu(false);
      }
      if (assigneeRef.current && !assigneeRef.current.contains(event.target)) {
        setShowAssigneeInfo(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleDelete = async (e) => {
    e.stopPropagation();
    
    if (window.confirm('Are you sure you want to delete this task?')) {
      try {
        setIsLoading(true);
        await onDelete(task.id);
      } catch (error) {
        console.error('Failed to delete task:', error);
        // Could show a toast notification here
      } finally {
        setIsLoading(false);
      }
    }
    setShowMenu(false);
  };

  const handleMove = async (toColumn) => {
    console.log(`Moving task ${task.id} from ${currentColumn} to ${toColumn}`);
    try {
      setIsLoading(true);
      await onMove(toColumn);
      console.log('Task moved successfully');
    } catch (error) {
      console.error('Failed to move task:', error);
      // Could show a toast notification here
    } finally {
      setIsLoading(false);
    }
    setShowMenu(false);
  };

  // Drag event handlers
  const handleDragStart = (e) => {
    setIsDragging(true);
    setShowMenu(false);
    
    const dragData = {
      taskId: task.id,
      fromColumn: currentColumn
    };
    
    e.dataTransfer.setData('application/json', JSON.stringify(dragData));
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragEnd = () => {
    setIsDragging(false);
  };

  // Filter out current column from available moves
  const moveOptions = availableColumns.filter(column => column !== currentColumn);

  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return null;
    // 直接显示选择的日期，不进行复杂格式化
    return dateString;
  };

  // Determine if task is overdue
  const isOverdue = task.due_date && new Date(task.due_date) < new Date();

  // Helper: get member info from backend-loaded members
  const getMemberById = (id) => {
    const list = Array.isArray(window.__projectMembers) ? window.__projectMembers : [];
    return list.find((m) => parseInt(m.id, 10) === parseInt(id, 10));
  };

  const handleEditInputChange = (field, value) => {
    setEditTask(prev => ({ ...prev, [field]: value }));
  };

  const handleStartEdit = () => {
    setIsEditing(true);
    setShowMenu(false);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditTask({
      title: task.title || '',
      description: task.description || '',
      due_date: task.due_date || '',
      assignee_id: task.assignee_id ?? 0,
    });
  };

  const handleSaveEdit = async (e) => {
    e?.stopPropagation?.();
    try {
      setIsLoading(true);
      const parsedAssignee = parseInt(editTask.assignee_id, 10);
      const updates = {
        title: editTask.title.trim(),
        description: (editTask.description ?? '').toString(),
        due_date: (editTask.due_date ?? '').toString(),
        assignee_id: Number.isNaN(parsedAssignee) ? 0 : parsedAssignee,
      };
      await onUpdate?.(updates);
      setIsEditing(false);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div 
      className={`card ${isLoading ? 'card-loading' : ''} ${isDragging ? 'card-dragging' : ''}`}
      draggable={!isLoading && !showMenu}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div className="card-content" onClick={() => !isEditing && handleStartEdit()}>
        {!isEditing && <div className="card-title">{task.title}</div>}
        {isEditing && (
          <div className="inline-task-form">
            <input
              type="text"
              value={editTask.title}
              onChange={(e) => handleEditInputChange('title', e.target.value)}
              className="task-input-title"
              autoFocus
            />
            <textarea
              value={editTask.description}
              onChange={(e) => handleEditInputChange('description', e.target.value)}
              className="task-input-description"
              rows={2}
            />
            <div className="task-input-row">
              <input
                type="date"
                value={editTask.due_date}
                onChange={(e) => handleEditInputChange('due_date', e.target.value)}
                className="task-input-date"
                min="2025-01-01"
                max="2025-12-31"
              />
            </div>
            <div className="task-assignee-row">
              <div className="assignee-selection">
                <span className="assignee-label">Assignee:</span>
                <div className="assignee-options">
                  <button
                    type="button"
                    className={`assignee-option ${!editTask.assignee_id ? 'selected' : ''}`}
                    onClick={() => handleEditInputChange('assignee_id', 0)}
                  >
                    <span className="default-avatar">👤</span>
                    <span>Unassigned</span>
                  </button>
                  {(window.__projectMembers || []).map(member => (
                    <button
                      key={member.id}
                      type="button"
                      className={`assignee-option ${parseInt(editTask.assignee_id, 10) === member.id ? 'selected' : ''}`}
                      onClick={() => handleEditInputChange('assignee_id', member.id)}
                    >
                      <span className="member-avatar">{member.avatar || '👤'}</span>
                      <span>{member.name}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
            <div className="task-form-buttons">
              <button type="button" className="btn-primary" onClick={handleSaveEdit} disabled={!editTask.title.trim()}>Save</button>
              <button type="button" className="btn-secondary" onClick={handleCancelEdit}>Cancel</button>
            </div>
          </div>
        )}
        
        {task.description && (
          <div className="card-description">{task.description}</div>
        )}
        
        {/* Task metadata */}
        <div className="card-metadata">
          {task.due_date && (
            <div className={`card-due-date ${isOverdue ? 'overdue' : ''}`}>
              📅 {formatDate(task.due_date)}
              {isOverdue && <span className="overdue-indicator">!</span>}
            </div>
          )}
          
          <div 
            className="card-assignee-wrapper" 
            ref={assigneeRef}
            style={{ position: 'relative' }}
          >
            {task.assignee_id ? (
              <div 
                className="card-assignee clickable assigned"
                onClick={(e) => {
                  e.stopPropagation();
                  setShowAssigneeInfo(!showAssigneeInfo);
                }}
              >
                {(() => {
                  const m = getMemberById(task.assignee_id);
                  return (
                    <>
                      <span className="assignee-avatar">{m?.avatar || '👤'}</span>
                      <span className="assignee-name">{m?.name || 'Unknown User'}</span>
                    </>
                  );
                })()}
              </div>
            ) : (
              <div className="card-assignee unassigned">
                <span className="assignee-avatar default">👤</span>
                <span className="assignee-name">Unassigned</span>
              </div>
            )}
              
            {showAssigneeInfo && task.assignee_id && (
              <div className="assignee-info-dropdown">
                {(() => {
                  const m = getMemberById(task.assignee_id);
                  return (
                    <>
                      <div className="assignee-name">{m?.name || 'Unknown User'}</div>
                      {m?.email && <div className="assignee-email">{m.email}</div>}
                    </>
                  );
                })()}
              </div>
            )}
          </div>
        </div>
        
        <div className="card-footer">
          {/* Menu button */}
          <button 
            className="card-menu-btn"
            onClick={(e) => {
              e.stopPropagation();
              setShowMenu(!showMenu);
            }}
            disabled={isLoading}
            aria-label="Task options"
          >
            {isLoading ? '⋯' : '⋮'}
          </button>
        </div>
      </div>
      
      {/* Dropdown menu */}
      {showMenu && (
        <div className="card-menu" ref={menuRef}>
          {moveOptions.length > 0 && (
            <>
              <div className="menu-section-title">MOVE TO</div>
              {moveOptions.map(column => (
                <button
                  key={column}
                  className="menu-item move"
                  onClick={() => handleMove(column)}
                  disabled={isLoading}
                >
                  ➤ {column}
                </button>
              ))}
              <div className="menu-divider"></div>
            </>
          )}
          
          <button 
            className="menu-item delete" 
            onClick={handleDelete}
            disabled={isLoading}
          >
            🗑️ Delete Task
          </button>
        </div>
      )}
      
      {/* Loading overlay */}
      {isLoading && (
        <div className="card-loading-overlay">
          <div className="loading-spinner"></div>
        </div>
      )}
    </div>
  );
};

export default Card;