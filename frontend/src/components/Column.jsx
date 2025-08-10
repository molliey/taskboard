// src/components/Column.jsx
import React, { useState, useRef, useEffect } from "react";
import Card from "./Card";
import { projectAPI } from "../api/taskboard";
import websocketService from "../services/websocketService";
// 移除本地 mock 用户，全部从后端加载成员

const Column = ({ title, tasks, onAddClick, onDeleteTask, onMoveTask, onUpdateTask, availableColumns, currentColumn, projectId }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [isCreatingTask, setIsCreatingTask] = useState(false);
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    due_date: '',
    assignee_id: null
  });
  const [projectMembers, setProjectMembers] = useState([]);
  const createFormRef = useRef(null);

  // Load project members and refresh on membership events
  useEffect(() => {
    const loadMembers = async () => {
      if (!projectId) return;
      const members = await projectAPI.getMembers(projectId);
      setProjectMembers(members || []);
    };
    loadMembers();

    const onMemberAdded = (payload) => {
      if (payload?.project_id === projectId) loadMembers();
    };
    const onMemberRemoved = (payload) => {
      if (payload?.project_id === projectId) loadMembers();
    };

    const unsubAdded = websocketService.subscribe('member_added', onMemberAdded);
    const unsubRemoved = websocketService.subscribe('member_removed', onMemberRemoved);
    return () => {
      unsubAdded?.();
      unsubRemoved?.();
    };
  }, [projectId]);

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
      due_date: '',
      assignee_id: null
    });
  };

  const handleCancelCreate = () => {
    setIsCreatingTask(false);
    setNewTask({
      title: '',
      description: '',
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
      tag: 'GENERAL' // 使用默认tag值
    };

    console.log('Creating task with data:', taskToCreate);
    console.log('Original newTask.description:', newTask.description);
    console.log('Trimmed description:', newTask.description.trim());

    if (onAddClick) {
      onAddClick(taskToCreate);
    }

    handleCancelCreate();
  };

  const handleInputChange = (field, value) => {
    console.log(`handleInputChange: ${field} = "${value}" (type: ${typeof value})`);
    setNewTask(prev => {
      const newState = { ...prev, [field]: value };
      console.log(`New newTask state:`, newState);
      return newState;
    });
  };

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
            onUpdate={(updates) => onUpdateTask(task.id, currentColumn, updates)}
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
                type="date"
                value={newTask.due_date}
                onChange={(e) => handleInputChange('due_date', e.target.value)}
                className="task-input-date"
                min="2025-01-01"
                max="2025-12-31"
              />
            </div>
            
            {/* 移除选择的时间预览显示 */}
            
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
                      <span className="member-avatar">{member.avatar || '👤'}</span>
                      <span>{member.name}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
            
            {/* 移除选择的负责人预览显示 */}
            
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

