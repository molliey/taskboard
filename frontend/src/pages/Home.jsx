import React, { useState } from "react";
import Topbar from "../components/Topbar"; 
import Sidebar from "../components/Sidebar";
import Board from "../components/Board";
import Summary from "../components/Summary";
import "../styles/global.css";

const Home = () => {
  const [currentProjectId, setCurrentProjectId] = useState(null);
  const [boardTasks, setBoardTasks] = useState({});
  const [boardColumns, setBoardColumns] = useState([]);

  const handleProjectSelect = (projectId) => {
    setCurrentProjectId(projectId);
  };

  const handleBoardDataChange = (tasks, columns) => {
    setBoardTasks(tasks);
    setBoardColumns(columns);
  };

  const handleLogout = () => {
    // 简单触发一次全局事件，让App重新检查认证状态
    window.dispatchEvent(new Event('auth:changed'));
  };

  return (
    <div className="app">
      <Topbar onLogout={handleLogout} />   
      <div className="main-content">
        <Sidebar 
          currentProjectId={currentProjectId}
          onProjectSelect={handleProjectSelect}
        />
        {currentProjectId && (
          <>
            <Board 
              projectId={currentProjectId} 
              onDataChange={handleBoardDataChange}
            />
            <Summary 
              tasks={boardTasks}
              columns={boardColumns}
              projectId={currentProjectId}
            />
          </>
        )}
      </div>
    </div>
  );
};

export default Home;

