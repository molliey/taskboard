import React, { useState, useEffect } from "react";
import { projectAPI } from "../api/taskboard";
import "../styles/global.css";

const Summary = ({ tasks, columns, projectId }) => {
  const [stats, setStats] = useState({
    total: 0,
    completed: 0,
    incompleted: 0,
    dueSoon: 0,
    statusDistribution: {
      'TO DO': 0,
      'IN PROGRESS': 0,
      'IN REVIEW': 0,
      'DONE': 0
    }
  });
  
  const [projectMembers, setProjectMembers] = useState([]);
  const [workloadData, setWorkloadData] = useState([]);

  useEffect(() => {
    calculateStats();
  }, [tasks, columns]);

  useEffect(() => {
    const loadMembers = async () => {
      if (!projectId) return;
      const members = await projectAPI.getMembers(projectId);
      setProjectMembers(members || []);
    };
    loadMembers();
  }, [projectId]);

  useEffect(() => {
    // recompute workload whenever members or tasks change
    if (!projectId || !tasks) return;
    const memberIndex = new Map();
    projectMembers.forEach(m => {
      memberIndex.set(m.id, { user: m, taskCount: 0, tasks: [] });
    });
    Object.entries(tasks || {}).forEach(([columnName, colTasks]) => {
      const list = Array.isArray(colTasks) ? colTasks : [];
      list.forEach(task => {
        const uid = parseInt(task.assignee_id, 10);
        if (uid && memberIndex.has(uid)) {
          const entry = memberIndex.get(uid);
          entry.taskCount += 1;
          entry.tasks.push({ id: task.id, title: task.title, column: columnName });
        }
      });
    });
    setWorkloadData(Array.from(memberIndex.values()));
  }, [projectMembers, tasks, projectId]);

  const calculateStats = () => {
    if (!tasks) return;

    let total = 0;
    let completed = 0;
    let dueSoon = 0;
    const distribution = {
      'TO DO': 0,
      'IN PROGRESS': 0,
      'IN REVIEW': 0,
      'DONE': 0
    };

    const today = new Date();
    const tenDaysFromNow = new Date(today.getTime() + 10 * 24 * 60 * 60 * 1000);

    Object.entries(tasks).forEach(([columnName, columnTasks]) => {
      if (Array.isArray(columnTasks)) {
        total += columnTasks.length;
        if (distribution[columnName] !== undefined) {
          distribution[columnName] = columnTasks.length;
        }

        if (columnName === 'DONE') {
          completed += columnTasks.length;
        }

        columnTasks.forEach(task => {
          if (task.due_date) {
            const dueDate = new Date(task.due_date);
            if (dueDate <= tenDaysFromNow && dueDate >= today && columnName !== 'DONE') {
              dueSoon++;
            }
          }
        });
      }
    });

    const incompleted = total - completed;

    setStats({
      total,
      completed,
      incompleted,
      dueSoon,
      statusDistribution: distribution
    });
  };

  // 简化的圆环图SVG组件
  const DonutChart = ({ data }) => {
    const colors = {
      'TO DO': '#6B73FF',
      'IN PROGRESS': '#00B8D9', 
      'IN REVIEW': '#FFAB00',
      'DONE': '#36B37E'
    };

    const total = Object.values(data).reduce((sum, val) => sum + val, 0);
    if (total === 0) {
      return (
        <div className="chart-container">
          <div className="empty-chart">No tasks</div>
        </div>
      );
    }

    const size = 120;
    const strokeWidth = 20;
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;

    let accumulatedLength = 0;
    const segments = Object.entries(data)
      .filter(([_, count]) => count > 0)
      .map(([status, count]) => {
        const percentage = count / total;
        const strokeDasharray = `${percentage * circumference} ${circumference}`;
        const strokeDashoffset = -accumulatedLength;
        accumulatedLength += percentage * circumference;

        return (
          <circle
            key={status}
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="transparent"
            stroke={colors[status]}
            strokeWidth={strokeWidth}
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            transform={`rotate(-90 ${size / 2} ${size / 2})`}
          />
        );
      });

    return (
      <div className="chart-container">
        <svg width={size} height={size} className="donut-chart">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="transparent"
            stroke="#f0f0f0"
            strokeWidth={strokeWidth}
          />
          {segments}
        </svg>
        <div className="chart-legend">
          {Object.entries(data).map(([status, count]) => {
            if (count === 0) return null;
            return (
              <div key={status} className="legend-item">
                <span 
                  className="legend-color" 
                  style={{ backgroundColor: colors[status] }}
                ></span>
                <span className="legend-text">{status}</span>
                <span className="legend-count">{count}</span>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  // Workload条形图组件
  const WorkloadChart = ({ data }) => {
    if (!data || data.length === 0) {
      return <div className="workload-empty">No workload data</div>;
    }

    const maxTasks = Math.max(...data.map(item => item.taskCount));
    
    return (
      <div className="workload-chart">
        <h4 className="workload-title">Team Workload</h4>
        {data.map((item) => (
          <div key={item.user.id} className="workload-item">
            <div className="workload-user">
              <span className="workload-avatar">{item.user.avatar || '👤'}</span>
              <span className="workload-name">{item.user.name}</span>
            </div>
            <div className="workload-bar-container">
              <div 
                className="workload-bar"
                style={{ 
                  width: maxTasks > 0 ? `${(item.taskCount / maxTasks) * 100}%` : '0%'
                }}
              ></div>
              <span className="workload-count">{item.taskCount}</span>
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="summary">
      <div className="summary-header">
        <h3 className="summary-title">SUMMARY</h3>
        {projectId && (
          <div className="project-indicator">
            Project {String.fromCharCode(64 + projectId)}
          </div>
        )}
      </div>
      
      <div className="summary-content">
        {/* 统计数据一行显示 */}
        <div className="stats-inline">
          <span className="stat-inline">
            <span className="stat-label">TOTAL</span>
            <span className="stat-value-black">{stats.total}</span>
          </span>
          <span className="stat-inline">
            <span className="stat-label">COMPLETED</span>
            <span className="stat-value-black">{stats.completed}</span>
          </span>
          <span className="stat-inline">
            <span className="stat-label">INCOMPLETED</span>
            <span className="stat-value-black">{stats.incompleted}</span>
          </span>
          <span className="stat-inline">
            <span className="stat-label">DUE SOON</span>
            <span className="stat-value-red">{stats.dueSoon}</span>
          </span>
        </div>

        {/* 第二行圆环图 */}
        <div className="chart-section">
          <DonutChart data={stats.statusDistribution} />
        </div>

        {/* Project Members */}
        {projectMembers.length > 0 && (
          <div className="project-members-section">
            <h4 className="section-title">Project Members</h4>
            <div className="project-members-list">
              {projectMembers.map((member) => (
                <div key={member.id} className="member-item">
                  <div className="member-avatar">{member.avatar || '👤'}</div>
                  <div className="member-info">
                    <div className="member-name">{member.name}</div>
                    <div className="member-email">{member.email}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Workload Chart */}
        <WorkloadChart data={workloadData} />
      </div>
    </div>
  );
};

export default Summary;