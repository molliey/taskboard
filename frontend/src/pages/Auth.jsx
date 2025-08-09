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

  // 通过按钮切换 login/register
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
      // 注册成功后切换到登录页面（不自动登录），并预填邮箱
      setMode('login');
      setLoginEmail(email);
      setLoginPassword('');
    } catch (err) {
      setError(err?.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
      <div className="auth-card" style={{ width: 360, padding: 24, border: '1px solid #eee', borderRadius: 12, background: '#fff' }}>
        {error && (
          <div style={{ color: 'red', marginBottom: 12 }}>{error}</div>
        )}

        {mode === 'login' && (
          <>
            {/* Login 表单 */}
            <form onSubmit={handleLogin} style={{ marginBottom: 12 }}>
              <div style={{ marginBottom: 12 }}>
                <label>Email</label>
                <input type="email" value={loginEmail} onChange={(e) => setLoginEmail(e.target.value)} required style={{ width: '100%', padding: 8, marginTop: 4 }} />
              </div>
              <div style={{ marginBottom: 12 }}>
                <label>Password</label>
                <input type="password" value={loginPassword} onChange={(e) => setLoginPassword(e.target.value)} required style={{ width: '100%', padding: 8, marginTop: 4 }} />
              </div>
              <button type="submit" disabled={loading} style={{ width: '100%', padding: 10 }}>
                {loading ? 'Logging in...' : 'Login'}
              </button>
            </form>
            {/* Register 蓝色模块（点击切换到注册表单） */}
            <button type="button" disabled={loading} onClick={() => switchMode('register')} style={{ width: '100%', padding: 10 }}>
              Register
            </button>
          </>
        )}

        {mode === 'register' && (
          <>
            {/* Register 表单：仅 Name/Email/Password，Role 使用默认值 */}
            <form onSubmit={handleRegister} style={{ marginBottom: 12 }}>
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
              {/* 隐藏 role 输入，使用默认 Developer */}
              <button type="submit" disabled={loading} style={{ width: '100%', padding: 10 }}>
                {loading ? 'Registering...' : 'Register'}
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
};

export default Auth; 