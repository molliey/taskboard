import React, { useState } from "react";
import "../styles/global.css";

const Sidebar = ({ currentProjectId, onProjectSelect }) => {
  const [collapsed, setCollapsed] = useState(false);
  const [projects, setProjects] = useState([
    { id: 1, name: "Project A" },
    { id: 2, name: "Project B" },
    { id: 3, name: "Project C" }
  ]);

  const toggleSidebar = () => {
    setCollapsed(!collapsed);
  };

  const handleProjectClick = (project) => {
    if (onProjectSelect) {
      onProjectSelect(project.id);
    }
  };

  const handleAddProject = () => {
    const newName = prompt("Enter project name:");
    if (newName && newName.trim()) {
      const newProject = {
        id: Date.now(),
        name: newName.trim()
      };
      setProjects(prev => [...prev, newProject]);
    }
  };

  return (
    <div className={`sidebar ${collapsed ? "collapsed" : ""}`}>
      <div className="sidebar-header">
        {!collapsed && <strong>PROJECTS</strong>}
        <button className="collapse-btn" onClick={toggleSidebar}>
          {collapsed ? "▶" : "◀"}
        </button>
      </div>
      
      {!collapsed && (
        <>
          <ul className="project-list">
            {projects.map((project) => (
              <li 
                key={project.id}
                className={`project-item ${currentProjectId === project.id ? 'active' : ''}`}
                onClick={() => handleProjectClick(project)}
              >
                <span role="img" aria-label="folder">📁</span>
                <span className="project-name">{project.name}</span>
              </li>
            ))}
          </ul>
          
          <button 
            className="add-project-btn"
            onClick={handleAddProject}
          >
            +
          </button>
        </>
      )}
    </div>
  );
};

export default Sidebar;

