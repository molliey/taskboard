// src/components/Column.jsx
import React, { useState, useRef, useEffect } from "react";
import Card from "./Card";
import userDataService from "../services/userDataService";

const Column = ({ title, tasks, onAddClick, onDeleteTask, onMoveTask, availableColumns, currentColumn, projectId }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [isCreatingTask, setIsCreatingTask] = useState(false);
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    tag: '',
    due_date: '',
    assignee_id: null
  });
  const createFormRef = useRef(null);

  // Close form when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (createFormRef.current && !createFormRef.current.contains(event.target)) {
        handleCancelCreate();
      }
    };

    if (isCreatingTask) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isCreatingTask]);

  const handleStartCreate = () => {
    setIsCreatingTask(true);
    setNewTask({
      title: '',
      description: '',
      tag: '',
      due_date: '',
      assignee_id: null
    });
  };

  const handleCancelCreate = () => {
    setIsCreatingTask(false);
    setNewTask({
      title: '',
      description: '',
      tag: '',
      due_date: '',
      assignee_id: null
    });
  };

  const handleSubmitCreate = (e) => {
    e.preventDefault();
    if (!newTask.title.trim()) return;

    const taskToCreate = {
      ...newTask,
      title: newTask.title.trim(),
      description: newTask.description.trim(),
      tag: newTask.tag.trim() || 'GENERAL'
    };

    if (onAddClick) {
      // Call the original add task function from Board
      onAddClick(taskToCreate);
    }

    handleCancelCreate();
  };

  const handleInputChange = (field, value) => {
    setNewTask(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Get project members for assignee selection
  const projectMembers = userDataService.getProjectMembers(projectId);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const taskData = e.dataTransfer.getData('application/json');
    if (taskData) {
      try {
        const { taskId, fromColumn } = JSON.parse(taskData);
        if (fromColumn !== currentColumn) {
          onMoveTask(taskId, fromColumn, currentColumn);
        }
      } catch (error) {
        console.error('Error parsing drag data:', error);
      }
    }
  };

  return (
    <div 
      className={`column ${isDragOver ? 'column-drag-over' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <div className="column-header">
        <h3>{title}</h3>
        <span className="count">{tasks.length}</span>
      </div>

      <div className="card-list">
        {tasks.map((task) => (
          <Card 
            key={task.id} 
            task={task} 
            onDelete={() => onDeleteTask(task.id, currentColumn)}
            onMove={(toColumn) => onMoveTask(task.id, currentColumn, toColumn)}
            availableColumns={availableColumns}
            currentColumn={currentColumn}
          />
        ))}
      </div>

      {/* Inline task creation */}
      {onAddClick && !isCreatingTask && (
        <div className="create-button" onClick={handleStartCreate}>
          ＋ Create Task
        </div>
      )}

      {isCreatingTask && (
        <div className="inline-task-form" ref={createFormRef}>
          <form onSubmit={handleSubmitCreate}>
            <input
              type="text"
              placeholder="Task title"
              value={newTask.title}
              onChange={(e) => handleInputChange('title', e.target.value)}
              autoFocus
              className="task-input-title"
            />
            
            <textarea
              placeholder="Description (optional)"
              value={newTask.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              className="task-input-description"
              rows={2}
            />
            
            <div className="task-input-row">
              <input
                type="text"
                placeholder="Tag"
                value={newTask.tag}
                onChange={(e) => handleInputChange('tag', e.target.value)}
                className="task-input-tag"
              />
              
              <input
                type="date"
                value={newTask.due_date}
                onChange={(e) => handleInputChange('due_date', e.target.value)}
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
                    className={`assignee-option ${!newTask.assignee_id ? 'selected' : ''}`}
                    onClick={() => handleInputChange('assignee_id', null)}
                  >
                    <span className="default-avatar">👤</span>
                    <span>Unassigned</span>
                  </button>
                  {projectMembers.map(member => (
                    <button
                      key={member.id}
                      type="button"
                      className={`assignee-option ${newTask.assignee_id === member.id ? 'selected' : ''}`}
                      onClick={() => handleInputChange('assignee_id', member.id)}
                    >
                      <span className="member-avatar">{member.avatar}</span>
                      <span>{member.name}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="task-form-buttons">
              <button type="submit" className="btn-primary" disabled={!newTask.title.trim()}>
                Create Task
              </button>
              <button type="button" className="btn-secondary" onClick={handleCancelCreate}>
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default Column;

