import React, { useState, useRef, useEffect } from "react";
// Remove local mock users, display logic uses backend-returned name

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
    assignee_id: parseInt(task.assignee_id, 10) || 0,
  });
  const [showInlineDatePicker, setShowInlineDatePicker] = useState(false);
  const [showAssigneeDropdown, setShowAssigneeDropdown] = useState(false);
  const [justUpdated, setJustUpdated] = useState(false);
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
        // Save directly and exit edit mode, don't call handleSaveEdit
        const updates = {
          title: editTask.title.trim(),
          description: (editTask.description ?? '').toString(),
          due_date: (editTask.due_date ?? '').toString(),
          assignee_id: Number.isNaN(parseInt(editTask.assignee_id, 10)) ? 0 : parseInt(editTask.assignee_id, 10),
        };
        console.log('Saving updates:', updates);
        console.log('Current editTask.assignee_id:', editTask.assignee_id);
        console.log('Parsed assignee_id:', updates.assignee_id);
        onUpdate?.(updates);
        setIsEditing(false);
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
  }, [isEditing, editTask]);

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
    // Display selected date directly without complex formatting
    return dateString;
  };

  // Determine overdue removed (no exclamation indicator)

  // Helper: get member info from backend-loaded members
  const getMemberById = (id) => {
    // If id is 0 or null/undefined, return null for Unassigned
    if (!id || id === 0 || id === '0') {
      return null;
    }
    
    const list = Array.isArray(window.__projectMembers) ? window.__projectMembers : [];
    const member = list.find((m) => parseInt(m.id, 10) === parseInt(id, 10));
    return member;
  };

  const handleEditInputChange = (field, value) => {
    console.log(`handleEditInputChange: ${field} = ${value}`);
    setEditTask(prev => {
      const newState = { ...prev, [field]: value };
      console.log('New editTask state:', newState);
      return newState;
    });
  };

  const handleStartEdit = () => {
    setIsEditing(true);
    setShowMenu(false);
    // Initialize edit form with latest task data on edit, ensure assignee consistency
    setEditTask({
      title: task.title || '',
      description: task.description || '',
      due_date: task.due_date || '',
      assignee_id: parseInt(task.assignee_id, 10) || 0,
    });
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditTask({
      title: task.title || '',
      description: task.description || '',
      due_date: task.due_date || '',
      assignee_id: parseInt(task.assignee_id, 10) || 0,
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

  // Sync edit form initial values when task data changes (not in edit mode)
  useEffect(() => {
    if (isEditing) return;
    setEditTask({
      title: task.title || '',
      description: task.description || '',
      due_date: task.due_date || '',
      assignee_id: parseInt(task.assignee_id, 10) || 0,
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
      <div className="card-content">
        {!isEditing && (
          <div 
            className="card-title" 
            onClick={(e) => {
              e.stopPropagation();
              if (!isEditing && !justUpdated) {
                handleStartEdit();
                // Delayed focus to title input
                setTimeout(() => {
                  const titleInput = document.querySelector('.task-input-title');
                  if (titleInput) titleInput.focus();
                }, 100);
              }
            }}
          >
            {task.title}
          </div>
        )}
        {isEditing && (
          <div className="inline-task-form">
            <input
              type="text"
              value={editTask.title}
              onChange={(e) => handleEditInputChange('title', e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  handleOutsideForEdit(e);
                }
              }}
              className="task-input-title"
              autoFocus
            />
            <textarea
              value={editTask.description}
              onChange={(e) => handleEditInputChange('description', e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleOutsideForEdit(e);
                }
              }}
              className="task-input-description"
              rows={2}
            />
            <div className="task-input-row">
              <div style={{ position: 'relative' }}>
                <input
                  type="date"
                  value={editTask.due_date}
                  onChange={(e) => {
                    const nextDate = e.target.value;
                    handleEditInputChange('due_date', nextDate);
                  }}
                  className="task-input-date"
                  min="2025-01-01"
                  max="2025-12-31"
                />
              </div>
            </div>
            <div className="task-assignee-row">
              <div className="assignee-selection">
                <div className="assignee-options">
                  <button
                    type="button"
                    className={`assignee-option ${parseInt(editTask.assignee_id, 10) === 0 ? 'selected' : ''}`}
                    onClick={() => {
                      console.log('Clicking Unassigned, current editTask.assignee_id:', editTask.assignee_id);
                      handleEditInputChange('assignee_id', 0);
                    }}
                  >
                    <span className="default-avatar">👤</span>
                    <span>Unassigned</span>
                  </button>
                   {(window.__projectMembers || []).map(member => (
                    <button
                      key={member.id}
                      type="button"
                      className={`assignee-option ${parseInt(editTask.assignee_id, 10) === parseInt(member.id, 10) ? 'selected' : ''}`}
                       onClick={() => {
                         console.log(`Clicking member ${member.name} (id: ${member.id}), current editTask.assignee_id:`, editTask.assignee_id);
                         handleEditInputChange('assignee_id', parseInt(member.id, 10));
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
          <div 
            className="card-description"
            onClick={(e) => {
              e.stopPropagation();
              if (!isEditing && !justUpdated) {
                handleStartEdit();
                // Delayed focus to description input
                setTimeout(() => {
                  const descInput = document.querySelector('.task-input-description');
                  if (descInput) descInput.focus();
                }, 100);
              }
            }}
          >
            {task.description}
          </div>
        )}
        
        
        {/* Spacer line */}
        {!isEditing && task.description && (
          <div style={{ height: '8px' }}></div>
        )}
        
        {/* Task metadata */}
        {!isEditing && (
          <div className="card-metadata">
            <div ref={dateRef} style={{ position: 'relative' }}>
              <div 
                className="card-due-date"
                onClick={(e) => { 
                  e.stopPropagation(); 
                  // Show date picker directly
                  setShowInlineDatePicker(true);
                  // Focus to date input immediately
                  setTimeout(() => {
                    const dateInput = document.querySelector('.inline-date-picker');
                    if (dateInput) {
                      dateInput.focus();
                      dateInput.showPicker?.(); // Open calendar picker directly
                    }
                  }, 10);
                }}
              >
                {formatDate(task.due_date)}
              </div>
              {showInlineDatePicker && (
                <input
                  type="date"
                  value={task.due_date || ''}
                  onChange={async (e) => {
                    const nextDate = e.target.value;
                    // Update directly without setting editTask first
                    await onUpdate?.({
                      title: (task.title || '').trim(),
                      description: (task.description ?? '').toString(),
                      due_date: (nextDate ?? '').toString(),
                      assignee_id: Number.isNaN(parseInt(task.assignee_id, 10)) ? 0 : parseInt(task.assignee_id, 10),
                    });
                    setShowInlineDatePicker(false);
                    // Mark as just updated to prevent entering edit mode
                    setJustUpdated(true);
                    setTimeout(() => setJustUpdated(false), 100);
                  }}
                  className="task-input-date inline-date-picker"
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
                onClick={(e) => { 
                  e.stopPropagation(); 
                  setShowAssigneeDropdown((v) => !v); 
                  setShowAssigneeInfo(false); 
                }}
              >
                {(() => {
                  const m = getMemberById(task.assignee_id);
                  console.log('Local assignee display - task.assignee_id:', task.assignee_id, 'getMemberById result:', m);
                  return (
                    <>
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
                      className={`assignee-option ${!task.assignee_id || parseInt(task.assignee_id, 10) === 0 ? 'selected' : ''}`}
                      onClick={async () => {
                        await onUpdate?.({
                          title: (task.title || '').trim(),
                          description: (task.description ?? '').toString(),
                          due_date: (task.due_date ?? '').toString(),
                          assignee_id: 0,
                        });
                        setShowAssigneeDropdown(false);
                        setJustUpdated(true);
                        setTimeout(() => setJustUpdated(false), 100);
                      }}
                    >
                      <span className="default-avatar">👤</span>
                      <span>Unassigned</span>
                    </button>
                    {(window.__projectMembers || []).map((member) => (
                      <button
                        key={member.id}
                        type="button"
                        className={`assignee-option ${parseInt(task.assignee_id, 10) === parseInt(member.id, 10) ? 'selected' : ''}`}
                        onClick={async () => {
                          await onUpdate?.({
                            title: (task.title || '').trim(),
                            description: (task.description ?? '').toString(),
                            due_date: (task.due_date ?? '').toString(),
                            assignee_id: parseInt(member.id, 10),
                          });
                          setShowAssigneeDropdown(false);
                          setJustUpdated(true);
                          setTimeout(() => setJustUpdated(false), 100);
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
          <button 
            className="menu-item edit" 
            onClick={(e) => {
              e.stopPropagation();
              handleStartEdit();
              setShowMenu(false);
              setTimeout(() => {
                const titleInput = document.querySelector('.task-input-title');
                if (titleInput) titleInput.focus();
              }, 100);
            }}
            disabled={isLoading}
          >
            ✏️ Edit Task
          </button>
          
          {moveOptions.length > 0 && (
            <>
              <div className="menu-divider"></div>
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