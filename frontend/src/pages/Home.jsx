import React, { useState } from "react";
import Topbar from "../components/Topbar"; 
import Sidebar from "../components/Sidebar";
import Board from "../components/Board";
import Summary from "../components/Summary";
import "../styles/global.css";

const Home = () => {
  const [currentProjectId, setCurrentProjectId] = useState(1);
  const [boardTasks, setBoardTasks] = useState({});
  const [boardColumns, setBoardColumns] = useState([]);

  const handleProjectSelect = (projectId) => {
    setCurrentProjectId(projectId);
  };

  const handleBoardDataChange = (tasks, columns) => {
    setBoardTasks(tasks);
    setBoardColumns(columns);
  };

  return (
    <div className="app">
      <Topbar />   
      <div className="main-content">
        <Sidebar 
          currentProjectId={currentProjectId}
          onProjectSelect={handleProjectSelect}
        />
        <Board 
          projectId={currentProjectId} 
          onDataChange={handleBoardDataChange}
        />
        <Summary 
          tasks={boardTasks}
          columns={boardColumns}
          projectId={currentProjectId}
        />
      </div>
    </div>
  );
};

export default Home;

