import React, { useEffect, useState } from "react";
import "../styles/global.css";
import { projectAPI } from "../api/taskboard";
import websocketService from "../services/websocketService";
import authService from "../services/authService";
import AddMemberModal from "./modals/AddMemberModal";

const Sidebar = ({ currentProjectId, onProjectSelect }) => {
  // Sidebar is no longer collapsible; always expanded
  const [projects, setProjects] = useState([]);
  const [showAddMember, setShowAddMember] = useState(false);
  const [members, setMembers] = useState([]);

  const loadProjects = async () => {
    const data = await projectAPI.getMyProjects();
    setProjects(data || []);
    if ((!currentProjectId || currentProjectId === 0) && data && data.length > 0 && onProjectSelect) {
      onProjectSelect(data[0].id);
    }
  };

  const loadMembers = async (pid) => {
    if (!pid) { setMembers([]); return; }
    const list = await projectAPI.getMembers(pid);
    setMembers(list || []);
  };

  useEffect(() => {
    loadProjects();
  }, []);
  useEffect(() => {
    loadMembers(currentProjectId);
  }, [currentProjectId]);

  useEffect(() => {
    const onMemberAdded = (payload) => { if (payload?.project_id === currentProjectId) loadMembers(currentProjectId); };
    const onMemberRemoved = (payload) => { if (payload?.project_id === currentProjectId) loadMembers(currentProjectId); };
    const ua = websocketService.subscribe('member_added', onMemberAdded);
    const ur = websocketService.subscribe('member_removed', onMemberRemoved);
    return () => { ua?.(); ur?.(); };
  }, [currentProjectId]);

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

  // Removed collapsible behavior

  const handleProjectClick = (project) => {
    if (onProjectSelect) {
      onProjectSelect(project.id);
    }
  };

  const handleDeleteProject = async (projectId) => {
    const target = projects.find(p => p.id === projectId);
    if (!target) return;
    const ok = window.confirm(`Delete project "${target.name}"? This action cannot be undone.`);
    if (!ok) return;
    try {
      await projectAPI.deleteProject(projectId);
      const newList = projects.filter(p => p.id !== projectId);
      setProjects(newList);
      if (currentProjectId === projectId) {
        if (newList.length > 0) {
          onProjectSelect && onProjectSelect(newList[0].id);
        } else {
          onProjectSelect && onProjectSelect(null);
        }
      }
    } catch (e) {
      console.error('Delete project failed', e);
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
    <div className="sidebar">
      <div className="sidebar-header">
        <strong>PROJECTS</strong>
      </div>
      
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
                <button
                  className="delete-project-btn"
                  title="Delete project"
                  onClick={(e) => { e.stopPropagation(); handleDeleteProject(project.id); }}
                >
                  🗑️
                </button>
              </li>
            ))}
          </ul>
          
          <button 
            className="add-project-btn"
            onClick={handleAddProject}
          >
            +
          </button>

          {/* MEMBERS section - fixed visible even if empty */}
          {currentProject && (
            <div className="project-members-section" style={{ marginTop: 12 }}>
              <h4 className="section-title">MEMBERS</h4>
              <div className="project-members-list">
                {members.map((m) => (
                  <div key={m.id} className="member-item" onClick={(e) => e.stopPropagation()}>
                    <div className="member-avatar">{m.avatar || '👤'}</div>
                    <div className="member-info">
                      <div className="member-name">{m.name}</div>
                      <div className="member-email">{m.email}</div>
                    </div>
                    <button
                      className="delete-project-btn"
                      title="Remove member"
                      onClick={async () => {
                        try {
                          await projectAPI.removeMember(currentProject.id, m.id);
                          loadMembers(currentProject.id);
                        } catch (e) {
                          console.error('Remove member failed', e);
                        }
                      }}
                    >
                      🗑️
                    </button>
                  </div>
                ))}
              </div>
              {/* Add Member button below list, same style as project + */}
              <button 
                className="add-project-btn"
                onClick={() => setShowAddMember(true)}
                style={{ marginTop: 8 }}
              >
                +
              </button>
            </div>
          )}
      </>

      {showAddMember && currentProject && (
        <AddMemberModal 
          project={currentProject}
          onClose={() => setShowAddMember(false)}
          onMemberAdded={() => {
            loadMembers(currentProjectId);
            setShowAddMember(false);
          }}
        />
      )}
    </div>
  );
};

export default Sidebar;

