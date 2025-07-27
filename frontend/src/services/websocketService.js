class WebSocketService {
  constructor() {
    this.ws = null;
    this.url = 'ws://localhost:8000/ws';  // Fixed URL since we know backend runs on 8000
    this.listeners = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 3000;
    this.isConnected = false;
    this.onlineUsers = 0;
  }

  connect(userId = 'anonymous') {
    // If already connected, don't create a new connection
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    console.log(`Attempting to connect to WebSocket: ${this.url}?user_id=${userId}`);
    
    try {
      this.ws = new WebSocket(`${this.url}?user_id=${userId}`);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected successfully');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.notifyListeners('connection', { status: 'connected' });
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        this.isConnected = false;
        this.notifyListeners('connection', { status: 'disconnected' });
        
        // Only attempt reconnect if it wasn't a clean close
        if (event.code !== 1000) {
          this.attemptReconnect(userId);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket connection error:', error);
        this.isConnected = false;
        this.notifyListeners('connection', { status: 'error', error });
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.notifyListeners('connection', { status: 'error', error });
      this.isConnected = false;
      setTimeout(() => this.attemptReconnect(userId), this.reconnectInterval);
    }
  }

  attemptReconnect(userId) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        this.connect(userId);
      }, this.reconnectInterval);
    } else {
      console.log('Max reconnection attempts reached');
    }
  }

  handleMessage(data) {
    switch (data.type) {
      case 'task_created':
        this.notifyListeners('taskCreated', data.payload);
        break;
      case 'task_updated':
        this.notifyListeners('taskUpdated', data.payload);
        break;
      case 'task_moved':
        this.notifyListeners('taskMoved', data.payload);
        break;
      case 'task_deleted':
        this.notifyListeners('taskDeleted', data.payload);
        break;
      case 'user_count':
        this.onlineUsers = data.payload.count;
        this.notifyListeners('userCount', data.payload);
        break;
      case 'board_sync':
        this.notifyListeners('boardSync', data.payload);
        break;
      default:
        console.log('Unknown message type:', data.type);
    }
  }

  subscribe(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);

    // Return unsubscribe function
    return () => {
      const callbacks = this.listeners.get(event);
      if (callbacks) {
        const index = callbacks.indexOf(callback);
        if (index > -1) {
          callbacks.splice(index, 1);
        }
      }
    };
  }

  notifyListeners(event, data) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('Error in WebSocket listener:', error);
        }
      });
    }
  }

  sendMessage(type, payload) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message = {
        type,
        payload,
        timestamp: new Date().toISOString()
      };
      this.ws.send(JSON.stringify(message));
      console.log(`Sent WebSocket message: ${type}`, payload);
    } else {
      console.warn(`WebSocket is not connected, skipping message: ${type}`, payload);
      // In local mode, we can still update UI locally without broadcasting
    }
  }

  // Task operations
  createTask(task, column, projectId) {
    this.sendMessage('create_task', { task, column, projectId });
  }

  updateTask(taskId, updates, projectId) {
    this.sendMessage('update_task', { taskId, updates, projectId });
  }

  moveTask(taskId, fromColumn, toColumn, position, projectId) {
    this.sendMessage('move_task', { taskId, fromColumn, toColumn, position, projectId });
  }

  deleteTask(taskId, column, projectId) {
    this.sendMessage('delete_task', { taskId, column, projectId });
  }

  // Request board sync
  requestBoardSync(projectId) {
    this.sendMessage('request_board_sync', { projectId });
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnected = false;
    this.listeners.clear();
  }

  getConnectionStatus() {
    return {
      isConnected: this.isConnected,
      onlineUsers: this.onlineUsers
    };
  }
}

// Create a singleton instance
const websocketService = new WebSocketService();

export default websocketService;