// 用户认证服务
class AuthService {
  constructor() {
    this.currentUser = null;
    this.isAuthenticated = false;
    this.availableUsers = [
      {
        id: 1,
        name: "Alice Johnson",
        email: "alice.johnson@company.com",
        avatar: "👩‍💼",
        role: "Frontend Developer",
        isActive: true
      },
      {
        id: 2,
        name: "Bob Smith", 
        email: "bob.smith@company.com",
        avatar: "👨‍💻",
        role: "Backend Developer",
        isActive: false
      },
      {
        id: 3,
        name: "Charlie Wilson",
        email: "charlie.wilson@company.com",
        avatar: "👨‍🎨", 
        role: "UI/UX Designer",
        isActive: false
      },
      {
        id: 4,
        name: "Diana Chen",
        email: "diana.chen@company.com",
        avatar: "👩‍🔬",
        role: "Product Manager",
        isActive: false
      },
      {
        id: 5,
        name: "Erik Anderson",
        email: "erik.anderson@company.com",
        avatar: "👨",
        role: "DevOps Engineer", 
        isActive: false
      },
      {
        id: 6,
        name: "Fiona Martinez",
        email: "fiona.martinez@company.com",
        avatar: "👩‍💻",
        role: "Full Stack Developer",
        isActive: false
      },
      {
        id: 7,
        name: "George Thompson",
        email: "george.thompson@company.com",
        avatar: "👨‍🔧",
        role: "QA Engineer",
        isActive: false
      },
      {
        id: 8,
        name: "Hannah Lee",
        email: "hannah.lee@company.com",
        avatar: "👩‍🎨",
        role: "Graphic Designer",
        isActive: false
      }
    ];
    
    // 默认登录第一个用户
    this.login(this.availableUsers[0]);
  }

  // 登录用户
  login(user) {
    this.currentUser = { ...user };
    this.isAuthenticated = true;
    
    // 更新用户活跃状态
    this.availableUsers.forEach(u => {
      u.isActive = u.id === user.id;
    });
    
    // 模拟保存到localStorage
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
    
    // 清除活跃状态
    this.availableUsers.forEach(u => {
      u.isActive = false;
    });
    
    // 清除localStorage
    localStorage.removeItem('currentUser');
    localStorage.removeItem('isAuthenticated');
    
    console.log(`User ${prevUser?.name} logged out`);
    this.notifyAuthListeners();
  }

  // 切换用户
  switchAccount(userId) {
    const newUser = this.availableUsers.find(u => u.id === userId);
    if (newUser) {
      this.login(newUser);
      return true;
    }
    return false;
  }

  // 获取当前用户
  getCurrentUser() {
    return this.currentUser;
  }

  // 检查是否已登录
  isLoggedIn() {
    return this.isAuthenticated && this.currentUser !== null;
  }

  // 获取所有可用用户（用于切换账户）
  getAvailableUsers() {
    return this.availableUsers.filter(u => !u.isActive);
  }

  // 更新用户资料
  updateProfile(updates) {
    if (this.currentUser) {
      this.currentUser = { ...this.currentUser, ...updates };
      
      // 同步更新availableUsers中的数据
      const userIndex = this.availableUsers.findIndex(u => u.id === this.currentUser.id);
      if (userIndex !== -1) {
        this.availableUsers[userIndex] = { ...this.availableUsers[userIndex], ...updates };
      }
      
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

  // 从localStorage恢复认证状态
  restoreAuthState() {
    try {
      const savedUser = localStorage.getItem('currentUser');
      const savedAuthState = localStorage.getItem('isAuthenticated');
      
      if (savedUser && savedAuthState === 'true') {
        const user = JSON.parse(savedUser);
        this.login(user);
      }
    } catch (error) {
      console.error('Failed to restore auth state:', error);
      this.logout();
    }
  }

  // 模拟账户设置更新
  updateAccountSettings(settings) {
    console.log('Account settings updated:', settings);
    // 这里可以添加实际的设置保存逻辑
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

// 页面加载时恢复认证状态
if (typeof window !== 'undefined') {
  authService.restoreAuthState();
}

export default authService;