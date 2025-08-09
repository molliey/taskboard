import React, { useState } from "react";
import userDataService from "../services/userDataService";

const AddTaskModal = ({ onClose, onSubmit, projectId }) => {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [assignedTo, setAssignedTo] = useState("");
  
  // 获取项目成员作为可选的assignee
  const projectMembers = projectId ? userDataService.getProjectMembers(projectId) : [];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (title.trim()) {
      onSubmit({
        title: title.trim(),
        description: description.trim() || null,
        due_date: dueDate || null,
        assignee_id: assignedTo ? parseInt(assignedTo) : null,
        position: 0, // 默认位置
      });
      onClose();
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal bg-white p-6 rounded shadow-md w-full max-w-md">
        <h3 className="text-xl font-semibold mb-4">Create New Task</h3>
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <input
            type="text"
            placeholder="Task Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="border rounded px-3 py-2 w-full"
            required
          />

          <textarea
            placeholder="Description (optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="border rounded px-3 py-2 w-full"
            rows="3"
          />

          <input
            type="date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            className="border rounded px-3 py-2 w-full"
          />

          <select
            value={assignedTo}
            onChange={(e) => setAssignedTo(e.target.value)}
            className="border rounded px-3 py-2 w-full"
          >
            <option value="">Select Assignee (optional)</option>
            {projectMembers.map((member) => (
              <option key={member.id} value={member.id}>
                {member.avatar} {member.name}
              </option>
            ))}
          </select>

          <div className="flex justify-between mt-4">
            <button
              type="submit"
              className="border border-blue-600 text-blue-600 px-4 py-2 rounded hover:bg-blue-50"
            >
              Create
            </button>
            <button
              type="button"
              onClick={onClose}
              className="bg-gray-200 text-gray-800 px-4 py-2 rounded hover:bg-gray-300"
            >
              Cancel
            </button>
          </div>
        </form>

      </div>
    </div>
  );
};

export default AddTaskModal;
