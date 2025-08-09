import React, { useState, useRef, useEffect } from "react";
import authService from "../services/authService";
import { userAPI } from "../api/taskboard";
import "../styles/global.css";

const Topbar = ({ onLogout }) => {
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const userMenuRef = useRef(null);

  // 监听认证状态变化
  useEffect(() => {
    const updateAuthState = (authState) => {
      setCurrentUser(authState.user);
    };

    // 初始化当前用户状态
    updateAuthState({
      user: authService.getCurrentUser(),
      isAuthenticated: authService.isLoggedIn()
    });

    // 添加认证状态监听器
    const unsubscribe = authService.addAuthListener(updateAuthState);

    return unsubscribe;
  }, []);

  // 点击外部关闭菜单
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setShowUserMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleUserMenuToggle = () => {
    setShowUserMenu(!showUserMenu);
  };

  const handleLogout = () => {
    console.log('Logging out...');
    // Clear backend token as well
    userAPI.logout();
    authService.logout();
    setShowUserMenu(false);
    if (typeof onLogout === 'function') {
      onLogout();
    }
  };

  return (
    <div className="topbar">
      <span className="platform-name">Genspark Board</span>
      <div className="user-actions">
        <span className="action">Help</span>
        <span className="action">Settings</span>
        
        {/* 用户头像和下拉菜单 */}
        <div className="user-menu-container" ref={userMenuRef}>
          <button 
            className="user-avatar-btn"
            onClick={handleUserMenuToggle}
          >
            <span className="user-avatar">
              {currentUser?.avatar || '👤'}
            </span>
          </button>

          {showUserMenu && (
            <div className="user-dropdown-menu">
              {/* 用户信息 */}
              <div className="user-info-section">
                <div className="user-display-name">{currentUser?.name || 'Unknown User'}</div>
                <div className="user-display-email">{currentUser?.email || ''}</div>
              </div>

              <div className="menu-divider"></div>

              <button className="dropdown-menu-item logout" onClick={handleLogout}>
                🚪 Log Out
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

Topbar.defaultProps = {
  onLogout: undefined,
};

export default Topbar;
