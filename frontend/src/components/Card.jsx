import React, { useState, useRef, useEffect } from "react";
import userDataService from "../services/userDataService";

const Card = ({ task, onDelete, onMove, availableColumns, currentColumn }) => {
  const [showMenu, setShowMenu] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [showAssigneeInfo, setShowAssigneeInfo] = useState(false);
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
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  // Determine if task is overdue
  const isOverdue = task.due_date && new Date(task.due_date) < new Date();

  return (
    <div 
      className={`card ${isLoading ? 'card-loading' : ''} ${isDragging ? 'card-dragging' : ''}`}
      draggable={!isLoading && !showMenu}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div className="card-content">
        <div className="card-title">{task.title}</div>
        
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
                <span className="assignee-avatar">
                  {userDataService.getUser(task.assignee_id)?.avatar || '👤'}
                </span>
                <span className="assignee-name">
                  {userDataService.getUserDisplayName(task.assignee_id)}
                </span>
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
                  const user = userDataService.getUser(task.assignee_id);
                  return user ? (
                    <>
                      <div className="assignee-name">{user.name}</div>
                      <div className="assignee-email">{user.email}</div>
                    </>
                  ) : (
                    <div className="assignee-name">Unknown User</div>
                  );
                })()}
              </div>
            )}
          </div>
        </div>
        
        <div className="card-footer">
          <div className="card-id">#{task.id}</div>
          
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