import React, { useState, useRef, useEffect } from "react";
import authService from "../services/authService";
import "../styles/global.css";

const Topbar = () => {
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [availableUsers, setAvailableUsers] = useState([]);
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

    // 获取可切换的用户列表
    setAvailableUsers(authService.getAvailableUsers());

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
    // 更新可切换用户列表
    setAvailableUsers(authService.getAvailableUsers());
  };

  const handleProfile = () => {
    console.log('Opening profile...');
    setShowUserMenu(false);
    // 这里可以打开profile modal或导航到profile页面
  };

  const handleAccountSettings = () => {
    console.log('Opening account settings...');
    setShowUserMenu(false);
    // 这里可以打开设置modal或导航到设置页面
  };

  const handleSwitchAccount = (userId) => {
    console.log(`Switching to user ${userId}`);
    authService.switchAccount(userId);
    setShowUserMenu(false);
  };

  const handleLogout = () => {
    console.log('Logging out...');
    authService.logout();
    setShowUserMenu(false);
    // 这里可以重定向到登录页面
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

              {/* 菜单选项 */}
              <button className="dropdown-menu-item" onClick={handleProfile}>
                👤 Profile
              </button>
              
              <button className="dropdown-menu-item" onClick={handleAccountSettings}>
                ⚙️ Account Settings
              </button>

              {/* 切换账户 */}
              {availableUsers.length > 0 && (
                <>
                  <div className="menu-divider"></div>
                  <div className="submenu-section">
                    <div className="submenu-title">Switch Account</div>
                    {availableUsers.map(user => (
                      <button 
                        key={user.id}
                        className="dropdown-menu-item switch-user"
                        onClick={() => handleSwitchAccount(user.id)}
                      >
                        <span className="switch-user-avatar">{user.avatar}</span>
                        <div className="switch-user-info">
                          <div className="switch-user-name">{user.name}</div>
                          <div className="switch-user-email">{user.email}</div>
                        </div>
                      </button>
                    ))}
                  </div>
                </>
              )}

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

export default Topbar;
