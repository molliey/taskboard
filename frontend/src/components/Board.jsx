import React, { useState, useEffect } from "react";
import Column from "./Column";
import { projectAPI } from "../api/taskboard";
import authService from "../services/authService";
import websocketService from "../services/websocketService";
import "../styles/global.css";

const normalizeColumns = (columns) => {
  const result = {};
  Object.entries(columns || {}).forEach(([col, tasks]) => {
    result[col] = (tasks || []).map((t) => ({
      ...t,
      assignee_id: t?.assignee_id != null ? parseInt(t.assignee_id, 10) : null,
    }));
  });
  return result;
};

const Board = ({ projectId = 1, onDataChange }) => {
  const [columns, setColumns] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const reloadBoard = async (pid = projectId) => {
    setError("");
    try {
      const data = await projectAPI.getBoard(pid);
      // Provide project members globally (frontend memory only) for Card editor
      const members = await projectAPI.getMembers(pid);
      window.__projectMembers = members || [];
      setColumns(normalizeColumns(data || {}));
    } catch (e) {
      setError(e?.message || "Failed to load board");
      setColumns({});
    }
  };

  // Load board when project changes
  useEffect(() => {
    const loadBoard = async () => {
      setLoading(true);
      try {
        await reloadBoard(projectId);
      } finally {
        setLoading(false);
      }
    };
    if (projectId) {
      loadBoard();
    }
  }, [projectId]);

  // Subscribe to WebSocket events for near-realtime refresh
  useEffect(() => {
    // Ensure connection
    const userId = authService.getCurrentUser()?.id || "anonymous";
    websocketService.connect(userId);

    const onTaskCreated = (payload) => {
      if (payload?.project_id === projectId) reloadBoard();
    };
    const onTaskMoved = (payload) => {
      if (payload?.project_id === projectId) reloadBoard();
    };
    const onTaskDeleted = (payload) => {
      if (payload?.project_id === projectId) reloadBoard();
    };

    const unsubCreate = websocketService.subscribe('taskCreated', onTaskCreated);
    const unsubMove = websocketService.subscribe('taskMoved', onTaskMoved);
    const unsubDelete = websocketService.subscribe('taskDeleted', onTaskDeleted);

    return () => {
      unsubCreate?.();
      unsubMove?.();
      unsubDelete?.();
    };
  }, [projectId]);

  // Notify parent when data changes
  useEffect(() => {
    if (onDataChange) {
      const columnNames = Object.keys(columns);
      onDataChange(columns, columnNames);
    }
  }, [columns, onDataChange]);

  // Create task in a column (ensure backend-required fields)
  const handleAddTaskInline = (columnTitle) => async (newTask) => {
    try {
      const currentUserId = authService.getCurrentUser()?.id || 0;
      const assigneeId =
        newTask.assignee_id === null || newTask.assignee_id === undefined || newTask.assignee_id === ''
          ? 0
          : parseInt(newTask.assignee_id, 10);

      const created = await projectAPI.createTask(projectId, {
        title: newTask.title,
        description: (newTask.description ?? "").toString(),
        tag: (newTask.tag && newTask.tag.trim()) ? newTask.tag.trim() : "GENERAL",
        due_date: (newTask.due_date ?? "").toString(),
        // Convert assignee_id to integer; default to 0 if unselected
        assignee_id: Number.isNaN(assigneeId) ? 0 : assigneeId,
        column_name: columnTitle,
      });
      setColumns((prev) => ({
        ...prev,
        [columnTitle]: [...(prev[columnTitle] || []), { ...created, assignee_id: parseInt(created.assignee_id, 10) }],
      }));
    } catch (e) {
      console.error("Create task failed", e);
    }
  };

  // Move task between columns
  const handleMoveTask = async (taskId, fromColumn, toColumn) => {
    try {
      const position = (columns[toColumn]?.length || 0);
      await projectAPI.moveTask(projectId, taskId, {
        from_column: fromColumn,
        to_column: toColumn,
        position,
      });
      setColumns((prev) => {
        const task = (prev[fromColumn] || []).find((t) => t.id === taskId);
        if (!task) return prev;
        return {
          ...prev,
          [fromColumn]: (prev[fromColumn] || []).filter((t) => t.id !== taskId),
          [toColumn]: [...(prev[toColumn] || []), { ...task, column_name: toColumn }],
        };
      });
    } catch (e) {
      console.error("Move task failed", e);
    }
  };

  // Update task fields (title/description/due_date/assignee_id)
  const handleUpdateTask = async (taskId, columnTitle, updates) => {
    // Optimistic update first to immediately reflect selected assignee
    setColumns((prev) => ({
      ...prev,
      [columnTitle]: (prev[columnTitle] || []).map((t) =>
        t.id === taskId
          ? {
              ...t,
              ...updates,
              assignee_id: updates?.assignee_id !== undefined ? parseInt(updates.assignee_id, 10) : t.assignee_id,
            }
          : t
      ),
    }));

    try {
      const updated = await projectAPI.updateTask(projectId, taskId, updates);
      setColumns((prev) => ({
        ...prev,
        [columnTitle]: (prev[columnTitle] || []).map((t) =>
          t.id === taskId
            ? {
                ...t,
                ...updated,
                assignee_id:
                  updated?.assignee_id != null && updated?.assignee_id !== ''
                    ? parseInt(updated.assignee_id, 10)
                    : t.assignee_id,
              }
            : t
        ),
      }));
    } catch (e) {
      console.error('Update task failed', e);
      // Optional on backend failure: refresh board once to maintain consistency
      try { await reloadBoard(projectId); } catch (_) {}
    }
  };

  // Delete task
  const handleDeleteTask = async (taskId, columnTitle) => {
    try {
      await projectAPI.deleteTask(projectId, taskId);
      setColumns((prev) => ({
        ...prev,
        [columnTitle]: (prev[columnTitle] || []).filter((t) => t.id !== taskId),
      }));
    } catch (e) {
      console.error("Delete task failed", e);
    }
  };

  if (loading) {
    return (
      <div className="board-loading">
        <div className="loading-spinner" />
        <div>Loading board...</div>
      </div>
    );
  }
  if (error) {
    return (
      <div className="board-error">
        <div>Failed to load board</div>
        <div style={{ fontSize: 12, color: '#888' }}>{error}</div>
      </div>
    );
  }

  return (
    <div className="board">
      {Object.entries(columns).map(([title, tasks]) => (
        <Column
          key={title}
          title={title}
          tasks={tasks}
          onAddClick={handleAddTaskInline(title)}
          onMoveTask={handleMoveTask}
          onDeleteTask={handleDeleteTask}
          onUpdateTask={handleUpdateTask}
          availableColumns={Object.keys(columns)}
          currentColumn={title}
          projectId={projectId}
        />
      ))}
    </div>
  );
};

export default Board;