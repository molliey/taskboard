import React, { useEffect, useState } from "react";
import "../styles/global.css";
import { projectAPI } from "../api/taskboard";
import websocketService from "../services/websocketService";
import authService from "../services/authService";
import AddMemberModal from "./modals/AddMemberModal";

const Sidebar = ({ currentProjectId, onProjectSelect }) => {
  const [collapsed, setCollapsed] = useState(false);
  const [projects, setProjects] = useState([]);
  const [showAddMember, setShowAddMember] = useState(false);

  const loadProjects = async () => {
    const data = await projectAPI.getMyProjects();
    setProjects(data || []);
    if ((!currentProjectId || currentProjectId === 0) && data && data.length > 0 && onProjectSelect) {
      onProjectSelect(data[0].id);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  useEffect(() => {
    const userId = authService.getCurrentUser()?.id || "anonymous";
    websocketService.connect(userId);

    const onMemberAdded = (payload) => {
      if (!payload) return;
      if (payload.id === authService.getCurrentUser()?.id) {
        loadProjects();
      }
    };

    const unsubMemberAdded = websocketService.subscribe('member_added', onMemberAdded);
    return () => {
      unsubMemberAdded?.();
    };
  }, []);

  const toggleSidebar = () => {
    setCollapsed(!collapsed);
  };

  const handleProjectClick = (project) => {
    if (onProjectSelect) {
      onProjectSelect(project.id);
    }
  };

  const handleAddProject = async () => {
    const newName = prompt("Enter project name:");
    if (newName && newName.trim()) {
      try {
        const created = await projectAPI.createProject({
          name: newName.trim(),
          description: "",
          is_active: true,
        });
        setProjects((prev) => [...prev, created]);
        if (onProjectSelect) onProjectSelect(created.id);
      } catch (e) {
        console.error("Create project failed", e);
      }
    }
  };

  const currentProject = projects.find(p => p.id === currentProjectId);

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

          {currentProject && (
            <button 
              className="add-project-btn"
              onClick={() => setShowAddMember(true)}
              style={{ marginTop: 8 }}
            >
              Add Member
            </button>
          )}
        </>
      )}

      {showAddMember && currentProject && (
        <AddMemberModal 
          project={currentProject}
          onClose={() => setShowAddMember(false)}
          onMemberAdded={() => setShowAddMember(false)}
        />
      )}
    </div>
  );
};

export default Sidebar;

