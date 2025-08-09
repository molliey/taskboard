import React, { useState } from 'react';
import { userAPI } from '../api/taskboard';
import authService from '../services/authService';

const Auth = ({ onAuthSuccess }) => {
  const [mode, setMode] = useState('login'); // 'login' | 'register'
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Login form state
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');

  // Register form state
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('Developer');

  const switchMode = (nextMode) => {
    setMode(nextMode);
    setError('');
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await userAPI.login({ email: loginEmail, password: loginPassword });
      if (!res?.success) {
        setError(res?.error || 'Login failed');
        return;
      }
      if (res?.user) {
        authService.login(res.user);
      }
      onAuthSuccess?.();
      window.dispatchEvent(new Event('auth:changed'));
    } catch (err) {
      setError(err?.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await userAPI.register({ name, email, password, role });
      // Auto login after successful registration
      const res = await userAPI.login({ email, password });
      if (!res?.success) {
        setError(res?.error || 'Login failed after registration');
        return;
      }
      if (res?.user) {
        authService.login(res.user);
      }
      onAuthSuccess?.();
      window.dispatchEvent(new Event('auth:changed'));
    } catch (err) {
      setError(err?.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
      <div className="auth-card" style={{ width: 360, padding: 24, border: '1px solid #eee', borderRadius: 12, background: '#fff' }}>
        <div style={{ display: 'flex', marginBottom: 16 }}>
          <button onClick={() => switchMode('login')} style={{ flex: 1, padding: 8, fontWeight: mode === 'login' ? 700 : 400 }}>Login</button>
          <button onClick={() => switchMode('register')} style={{ flex: 1, padding: 8, fontWeight: mode === 'register' ? 700 : 400 }}>Register</button>
        </div>

        {error && (
          <div style={{ color: 'red', marginBottom: 12 }}>{error}</div>
        )}

        {mode === 'login' ? (
          <form onSubmit={handleLogin}>
            <div style={{ marginBottom: 12 }}>
              <label>Email</label>
              <input type="email" value={loginEmail} onChange={(e) => setLoginEmail(e.target.value)} required style={{ width: '100%', padding: 8, marginTop: 4 }} />
            </div>
            <div style={{ marginBottom: 12 }}>
              <label>Password</label>
              <input type="password" value={loginPassword} onChange={(e) => setLoginPassword(e.target.value)} required style={{ width: '100%', padding: 8, marginTop: 4 }} />
            </div>
            <button type="submit" disabled={loading} style={{ width: '100%', padding: 10 }}>{loading ? 'Logging in...' : 'Login'}</button>
          </form>
        ) : (
          <form onSubmit={handleRegister}>
            <div style={{ marginBottom: 12 }}>
              <label>Name</label>
              <input type="text" value={name} onChange={(e) => setName(e.target.value)} required style={{ width: '100%', padding: 8, marginTop: 4 }} />
            </div>
            <div style={{ marginBottom: 12 }}>
              <label>Email</label>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required style={{ width: '100%', padding: 8, marginTop: 4 }} />
            </div>
            <div style={{ marginBottom: 12 }}>
              <label>Password</label>
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required style={{ width: '100%', padding: 8, marginTop: 4 }} />
            </div>
            <div style={{ marginBottom: 16 }}>
              <label>Role</label>
              <input type="text" value={role} onChange={(e) => setRole(e.target.value)} required style={{ width: '100%', padding: 8, marginTop: 4 }} />
            </div>
            <button type="submit" disabled={loading} style={{ width: '100%', padding: 10 }}>{loading ? 'Registering...' : 'Register & Login'}</button>
          </form>
        )}
      </div>
    </div>
  );
};

export default Auth; 