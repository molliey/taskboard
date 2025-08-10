import React, { useState } from 'react';
import { projectAPI } from '../../api/taskboard';

const AddMemberModal = ({ project, onClose, onMemberAdded }) => {
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('Developer');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email) return;
    setLoading(true);
    setError('');
    try {
      await projectAPI.addMemberByEmail(project.id, { email, role: role || 'Member' });
      if (onMemberAdded) onMemberAdded();
      onClose();
    } catch (e) {
      if (e?.status === 404) {
        setError('User not found');
      } else {
        setError(e?.message || 'Failed to add member');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h3>Add Member to {project.name}</h3>
        {error && <div className="error-message" style={{ marginBottom: 12 }}>{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="flex flex-col gap-3">
            <label>
              Email
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required placeholder="user@example.com" />
            </label>
            <label>
              Role
              <input type="text" value={role} onChange={(e) => setRole(e.target.value)} placeholder="Role in project" />
            </label>
          </div>
          <div className="modal-buttons" style={{ marginTop: 16 }}>
            <button type="button" onClick={onClose}>Cancel</button>
            <button type="submit" disabled={loading}>{loading ? 'Adding...' : 'Add Member'}</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddMemberModal; 