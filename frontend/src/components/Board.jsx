import React, { useState, useEffect } from "react";
import Column from "./Column";
import projectDataService from "../services/projectDataService";
import "../styles/global.css";

const Board = ({ projectId = 1, onDataChange }) => {
  // 每列的任务列表作为状态
  const [columns, setColumns] = useState({});

  // 当项目ID变化时加载项目数据
  useEffect(() => {
    console.log(`Loading data for project ${projectId}`);
    const projectData = projectDataService.getProjectData(projectId);
    setColumns(projectData);
  }, [projectId]);

  // 当数据变化时通知父组件
  useEffect(() => {
    if (onDataChange) {
      const columnNames = Object.keys(columns);
      onDataChange(columns, columnNames);
    }
  }, [columns, onDataChange]);

  // 处理内联任务创建（替代模态框）
  const handleAddTaskInline = (columnTitle) => (newTask) => {
    const taskWithId = {
      ...newTask,
      id: `P${projectId}-${Date.now()}`, // 生成带项目前缀的唯一ID
    };
    
    // 更新本地状态
    setColumns((prev) => ({
      ...prev,
      [columnTitle]: [...prev[columnTitle], taskWithId],
    }));
    
    // 更新项目数据服务
    projectDataService.addTaskToProject(projectId, columnTitle, taskWithId);
  };

  // 处理任务移动
  const handleMoveTask = (taskId, fromColumn, toColumn) => {
    console.log(`Board: Moving task ${taskId} from ${fromColumn} to ${toColumn} in project ${projectId}`);
    
    // 更新本地状态
    setColumns((prev) => {
      const task = prev[fromColumn].find(t => t.id === taskId);
      if (!task) {
        console.log('Task not found in source column');
        return prev;
      }
      
      console.log('Task found, updating columns');
      return {
        ...prev,
        [fromColumn]: prev[fromColumn].filter(t => t.id !== taskId),
        [toColumn]: [...prev[toColumn], task],
      };
    });
    
    // 更新项目数据服务
    projectDataService.moveTaskInProject(projectId, taskId, fromColumn, toColumn);
  };

  // 处理任务删除
  const handleDeleteTask = (taskId, columnTitle) => {
    // 更新本地状态
    setColumns((prev) => ({
      ...prev,
      [columnTitle]: prev[columnTitle].filter(t => t.id !== taskId),
    }));
    
    // 更新项目数据服务
    projectDataService.deleteTaskFromProject(projectId, taskId, columnTitle);
  };

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
          availableColumns={Object.keys(columns)}
          currentColumn={title}
          projectId={projectId}
        />
      ))}
    </div>
  );
};

export default Board;