// User authentication service
class AuthService {
  constructor() {
    this.currentUser = null;
    this.isAuthenticated = false;
    // Mock用户数据已删除 - 所有用户数据来自真实后端API
    
    // 移除默认自动登录，改为等待真实登录
  }

  // 登录用户
  login(user) {
    this.currentUser = { ...user };
    this.isAuthenticated = true;
    
    // 用户活跃状态通过真实后端API管理
    
    // 保存到localStorage（仅用于显示当前用户信息）
    localStorage.setItem('currentUser', JSON.stringify(this.currentUser));
    localStorage.setItem('isAuthenticated', 'true');
    
    console.log(`User ${user.name} logged in successfully`);
    this.notifyAuthListeners();
  }

  // 登出用户
  logout() {
    const prevUser = this.currentUser;
    this.currentUser = null;
    this.isAuthenticated = false;
    
    // 用户状态通过真实后端API管理
    
    // 清除localStorage
    localStorage.removeItem('currentUser');
    localStorage.removeItem('isAuthenticated');
    
    console.log(`User ${prevUser?.name} logged out`);
    this.notifyAuthListeners();
  }

  // switchAccount方法已删除 - 不再支持mock用户切换

  // 获取当前用户
  getCurrentUser() {
    return this.currentUser;
  }

  // 检查是否已登录
  isLoggedIn() {
    return this.isAuthenticated && this.currentUser !== null;
  }

  // getAvailableUsers方法已删除 - 用户数据来自真实API

  // 更新用户资料
  updateProfile(updates) {
    if (this.currentUser) {
      this.currentUser = { ...this.currentUser, ...updates };
      
      // 用户数据更新通过真实后端API同步
      
      // 更新localStorage
      localStorage.setItem('currentUser', JSON.stringify(this.currentUser));
      
      this.notifyAuthListeners();
      return true;
    }
    return false;
  }

  // 认证状态监听器
  authListeners = new Set();

  // 添加认证状态监听器
  addAuthListener(callback) {
    this.authListeners.add(callback);
    
    // 返回取消监听的函数
    return () => {
      this.authListeners.delete(callback);
    };
  }

  // 通知所有监听器
  notifyAuthListeners() {
    this.authListeners.forEach(callback => {
      try {
        callback({
          user: this.currentUser,
          isAuthenticated: this.isAuthenticated
        });
      } catch (error) {
        console.error('Error in auth listener:', error);
      }
    });
  }

  // 从localStorage恢复认证状态（仅在存在后端token时）
  restoreAuthState() {
    try {
      const token = localStorage.getItem('access_token');
      const savedUser = localStorage.getItem('currentUser');
      const savedAuthState = localStorage.getItem('isAuthenticated');
      
      if (token && savedUser && savedAuthState === 'true') {
        const user = JSON.parse(savedUser);
        this.login(user);
      } else {
        // 确保未登录态
        this.logout();
      }
    } catch (error) {
      console.error('Failed to restore auth state:', error);
      this.logout();
    }
  }

  // 模拟账户设置更新
  updateAccountSettings(settings) {
    console.log('Account settings updated:', settings);
    return Promise.resolve(true);
  }

  // 模拟profile更新
  updateUserProfile(profileData) {
    console.log('Profile updated:', profileData);
    return this.updateProfile(profileData);
  }
}

// 创建单例实例
const authService = new AuthService();

// 页面加载时恢复认证状态（要求存在有效后端token）
if (typeof window !== 'undefined') {
  authService.restoreAuthState();
}

export default authService;