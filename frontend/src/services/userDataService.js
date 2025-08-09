// 用户数据管理服务
class UserDataService {
  constructor() {
    this.users = new Map();
    this.projectMembers = new Map();
    this.initializeUsers();
    this.initializeProjectMembers();
  }

  // 初始化用户数据
  initializeUsers() {
    this.users.set(1, {
      id: 1,
      name: "Alice Johnson",
      email: "alice.johnson@company.com",
      avatar: "👩‍💼",
      role: "Frontend Developer"
    });

    this.users.set(2, {
      id: 2,
      name: "Bob Smith",
      email: "bob.smith@company.com",
      avatar: "👨‍💻",
      role: "Backend Developer"
    });

    this.users.set(3, {
      id: 3,
      name: "Charlie Wilson",
      email: "charlie.wilson@company.com",
      avatar: "👨‍🎨",
      role: "UI/UX Designer"
    });

    this.users.set(4, {
      id: 4,
      name: "Diana Chen",
      email: "diana.chen@company.com",
      avatar: "👩‍🔬",
      role: "Product Manager"
    });

    this.users.set(5, {
      id: 5,
      name: "Erik Anderson",
      email: "erik.anderson@company.com",
      avatar: "👨‍⚡",
      role: "DevOps Engineer"
    });

    this.users.set(6, {
      id: 6,
      name: "Fiona Martinez",
      email: "fiona.martinez@company.com",
      avatar: "👩‍💻",
      role: "Full Stack Developer"
    });

    this.users.set(7, {
      id: 7,
      name: "George Thompson",
      email: "george.thompson@company.com",
      avatar: "👨‍🔧",
      role: "QA Engineer"
    });

    this.users.set(8, {
      id: 8,
      name: "Hannah Lee",
      email: "hannah.lee@company.com",
      avatar: "👩‍🎨",
      role: "Graphic Designer"
    });
  }

  // 初始化项目成员分配
  initializeProjectMembers() {
    // Project A 成员 (Web Application Development)
    this.projectMembers.set(1, [1, 2, 3, 6, 7]);
    
    // Project B 成员 (E-commerce Platform)
    this.projectMembers.set(2, [2, 3, 4, 6, 8]);
    
    // Project C 成员 (Mobile App Development)
    this.projectMembers.set(3, [1, 4, 5, 6, 7, 8]);
  }

  // 获取用户信息
  getUser(userId) {
    return this.users.get(userId);
  }

  // 获取所有用户
  getAllUsers() {
    return Array.from(this.users.values());
  }

  // 获取项目成员
  getProjectMembers(projectId) {
    const memberIds = this.projectMembers.get(projectId) || [];
    return memberIds.map(id => this.users.get(id)).filter(Boolean);
  }

  // 获取用户显示名称
  getUserDisplayName(userId) {
    const user = this.getUser(userId);
    return user ? user.name : `User ${userId}`;
  }

  // 获取用户邮箱
  getUserEmail(userId) {
    const user = this.getUser(userId);
    return user ? user.email : '';
  }

  // 检查用户是否是项目成员
  isProjectMember(projectId, userId) {
    const memberIds = this.projectMembers.get(projectId) || [];
    return memberIds.includes(userId);
  }

  // 添加用户到项目
  addUserToProject(projectId, userId) {
    if (!this.projectMembers.has(projectId)) {
      this.projectMembers.set(projectId, []);
    }
    const members = this.projectMembers.get(projectId);
    if (!members.includes(userId)) {
      members.push(userId);
    }
  }

  // 从项目移除用户
  removeUserFromProject(projectId, userId) {
    if (this.projectMembers.has(projectId)) {
      const members = this.projectMembers.get(projectId);
      const index = members.indexOf(userId);
      if (index > -1) {
        members.splice(index, 1);
      }
    }
  }

  // 计算用户在项目中的任务数量
  calculateUserWorkload(projectId, projectData) {
    const workload = new Map();
    const members = this.getProjectMembers(projectId);
    
    // 初始化所有成员的工作量为0
    members.forEach(member => {
      workload.set(member.id, {
        user: member,
        taskCount: 0,
        tasks: []
      });
    });

    // 计算每个成员的任务数量
    if (projectData) {
      Object.entries(projectData).forEach(([columnName, tasks]) => {
        tasks.forEach(task => {
          if (task.assignee_id && workload.has(task.assignee_id)) {
            const userWorkload = workload.get(task.assignee_id);
            userWorkload.taskCount++;
            userWorkload.tasks.push({
              id: task.id,
              title: task.title,
              column: columnName
            });
          }
        });
      });
    }

    return Array.from(workload.values());
  }
}

// 创建单例实例
const userDataService = new UserDataService();

export default userDataService;