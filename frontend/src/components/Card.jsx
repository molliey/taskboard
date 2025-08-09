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
  const [showInlineDatePicker, setShowInlineDatePicker] = useState(false);
  const [showAssigneeDropdown, setShowAssigneeDropdown] = useState(false);
  const menuRef = useRef(null);
  const assigneeRef = useRef(null);
  const cardRef = useRef(null);
  const dateRef = useRef(null);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setShowMenu(false);
      }
      if (assigneeRef.current && !assigneeRef.current.contains(event.target)) {
        setShowAssigneeInfo(false);
        setShowAssigneeDropdown(false);
      }
      if (dateRef.current && !dateRef.current.contains(event.target)) {
        setShowInlineDatePicker(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Auto-save on clicking outside the card while editing
  useEffect(() => {
    if (!isEditing) return;
    const handleOutsideForEdit = (event) => {
      if (cardRef.current && !cardRef.current.contains(event.target)) {
        if (editTask.title && editTask.title.trim()) {
          handleSaveEdit();
        } else {
          // Revert if title is empty
          handleCancelEdit();
        }
      }
    };
    document.addEventListener('mousedown', handleOutsideForEdit);
    return () => {
      document.removeEventListener('mousedown', handleOutsideForEdit);
    };
  }, [isEditing, editTask.title]);

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

  // Determine overdue removed (no exclamation indicator)

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
    // 进入编辑时，用最新任务数据初始化编辑表单，确保 assignee 等保持一致
    setEditTask({
      title: task.title || '',
      description: task.description || '',
      due_date: task.due_date || '',
      assignee_id: task.assignee_id ?? 0,
    });
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

  // 当任务数据变化时（且未在编辑中），同步编辑表单的初始值，确保再次编辑时是最新值
  useEffect(() => {
    if (isEditing) return;
    setEditTask({
      title: task.title || '',
      description: task.description || '',
      due_date: task.due_date || '',
      assignee_id: task.assignee_id ?? 0,
    });
  }, [task.title, task.description, task.due_date, task.assignee_id, isEditing]);

  return (
    <div 
      className={`card ${isLoading ? 'card-loading' : ''} ${isDragging ? 'card-dragging' : ''}`}
      draggable={!isLoading && !showMenu}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      ref={cardRef}
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
                    onClick={() => {
                      handleEditInputChange('assignee_id', 0);
                      const next = { ...editTask, assignee_id: 0 };
                      const updates = {
                        title: (next.title || '').trim(),
                        description: (next.description ?? '').toString(),
                        due_date: (next.due_date ?? '').toString(),
                        assignee_id: 0,
                      };
                      onUpdate?.(updates);
                    }}
                  >
                    <span className="default-avatar">👤</span>
                    <span>Unassigned</span>
                  </button>
                   {(window.__projectMembers || []).map(member => (
                    <button
                      key={member.id}
                      type="button"
                      className={`assignee-option ${parseInt(editTask.assignee_id, 10) === member.id ? 'selected' : ''}`}
                       onClick={() => {
                         handleEditInputChange('assignee_id', member.id);
                         // 选择后立即保存（Jira风格更少操作）
                         const next = { ...editTask, assignee_id: member.id };
                         const parsedAssignee = parseInt(next.assignee_id, 10);
                         const updates = {
                           title: (next.title || '').trim(),
                           description: (next.description ?? '').toString(),
                           due_date: (next.due_date ?? '').toString(),
                           assignee_id: Number.isNaN(parsedAssignee) ? 0 : parsedAssignee,
                         };
                         onUpdate?.(updates);
                       }}
                    >
                      <span className="member-avatar">{member.avatar || '👤'}</span>
                      <span>{member.name}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
        
        {!isEditing && task.description && (
          <div className="card-description">{task.description}</div>
        )}
        
        {/* Task metadata */}
        {!isEditing && (
          <div className="card-metadata">
            <div ref={dateRef} style={{ position: 'relative' }}>
              <div 
                className="card-due-date"
                onClick={(e) => { e.stopPropagation(); setShowInlineDatePicker(true); }}
              >
                📅 {formatDate(task.due_date)}
              </div>
              {showInlineDatePicker && (
                <input
                  type="date"
                  value={editTask.due_date}
                  onChange={async (e) => {
                    const nextDate = e.target.value;
                    setEditTask(prev => ({ ...prev, due_date: nextDate }));
                    await onUpdate?.({
                      title: (task.title || '').trim(),
                      description: (task.description ?? '').toString(),
                      due_date: (nextDate ?? '').toString(),
                      assignee_id: Number.isNaN(parseInt(task.assignee_id, 10)) ? 0 : parseInt(task.assignee_id, 10),
                    });
                    setShowInlineDatePicker(false);
                  }}
                  className="task-input-date"
                  min="2025-01-01"
                  max="2025-12-31"
                  style={{ position: 'absolute', top: '100%', left: 0, zIndex: 1001 }}
                  onClick={(e) => e.stopPropagation()}
                />
              )}
            </div>
            
            <div 
              className="card-assignee-wrapper" 
              ref={assigneeRef}
              style={{ position: 'relative' }}
            >
              <div 
                className={`card-assignee ${task.assignee_id ? 'clickable assigned' : 'unassigned'}`}
                onClick={(e) => { e.stopPropagation(); setShowAssigneeDropdown((v) => !v); setShowAssigneeInfo(false); }}
              >
                {(() => {
                  const m = getMemberById(task.assignee_id);
                  return (
                    <>
                      <span className="assignee-avatar">{m?.avatar || '👤'}</span>
                      <span className="assignee-name">{m?.name || 'Unassigned'}</span>
                    </>
                  );
                })()}
              </div>

              {showAssigneeDropdown && (
                <div className="assignee-select-dropdown">
                  <div className="assignee-options" style={{ padding: 4 }}>
                    <button
                      type="button"
                      className={`assignee-option ${!task.assignee_id ? 'selected' : ''}`}
                      onClick={async () => {
                        await onUpdate?.({
                          title: (task.title || '').trim(),
                          description: (task.description ?? '').toString(),
                          due_date: (task.due_date ?? '').toString(),
                          assignee_id: 0,
                        });
                        setShowAssigneeDropdown(false);
                      }}
                    >
                      <span className="default-avatar">👤</span>
                      <span>Unassigned</span>
                    </button>
                    {(window.__projectMembers || []).map((member) => (
                      <button
                        key={member.id}
                        type="button"
                        className={`assignee-option ${parseInt(task.assignee_id, 10) === member.id ? 'selected' : ''}`}
                        onClick={async () => {
                          await onUpdate?.({
                            title: (task.title || '').trim(),
                            description: (task.description ?? '').toString(),
                            due_date: (task.due_date ?? '').toString(),
                            assignee_id: member.id,
                          });
                          setShowAssigneeDropdown(false);
                        }}
                      >
                        <span className="member-avatar">{member.avatar || '👤'}</span>
                        <span>{member.name}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
        
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