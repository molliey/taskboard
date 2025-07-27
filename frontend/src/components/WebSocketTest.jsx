import React, { useState, useEffect } from 'react';

const WebSocketTest = () => {
  const [connectionStatus, setConnectionStatus] = useState('Not connected');
  const [messages, setMessages] = useState([]);
  const [ws, setWs] = useState(null);

  useEffect(() => {
    console.log('Starting WebSocket test...');
    
    // Test WebSocket URL
    const testUrls = [
      'ws://localhost:8000/ws?user_id=test_user'
    ];

    const tryConnection = async (url) => {
      return new Promise((resolve) => {
        console.log(`Trying connection to: ${url}`);
        setConnectionStatus(`Trying ${url}...`);
        
        try {
          const websocket = new WebSocket(url);
          
          const timeout = setTimeout(() => {
            websocket.close();
            resolve({ success: false, url, error: 'Timeout' });
          }, 3000);
          
          websocket.onopen = () => {
            clearTimeout(timeout);
            console.log(`✅ Connected to: ${url}`);
            setConnectionStatus(`Connected to ${url}`);
            setWs(websocket);
            resolve({ success: true, url, websocket });
          };
          
          websocket.onerror = (error) => {
            clearTimeout(timeout);
            console.log(`❌ Failed to connect to: ${url}`, error);
            resolve({ success: false, url, error: 'Connection failed' });
          };
          
          websocket.onmessage = (event) => {
            console.log('Received message:', event.data);
            setMessages(prev => [...prev, `Received: ${event.data}`]);
          };
          
          websocket.onclose = (event) => {
            console.log(`Connection closed: ${url}`, event.code, event.reason);
            if (event.code !== 1000) {
              setConnectionStatus('Disconnected');
            }
          };
          
        } catch (error) {
          console.log(`❌ Error creating connection to: ${url}`, error);
          resolve({ success: false, url, error: error.message });
        }
      });
    };

    const testConnections = async () => {
      for (const url of testUrls) {
        const result = await tryConnection(url);
        if (result.success) {
          setMessages(prev => [...prev, `✅ Successfully connected to ${url}`]);
          break;
        } else {
          setMessages(prev => [...prev, `❌ Failed to connect to ${url}: ${result.error}`]);
        }
      }
    };

    testConnections();

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  const sendTestMessage = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      const testMessage = {
        type: 'test_message',
        payload: { message: 'Hello from frontend!' },
        timestamp: new Date().toISOString()
      };
      ws.send(JSON.stringify(testMessage));
      setMessages(prev => [...prev, `Sent: ${JSON.stringify(testMessage)}`]);
    } else {
      setMessages(prev => [...prev, '❌ Cannot send message - not connected']);
    }
  };

  return (
    <div style={{ 
      padding: '20px', 
      backgroundColor: '#e8f5e8', 
      margin: '20px', 
      borderRadius: '8px',
      fontFamily: 'monospace' 
    }}>
      <h3>WebSocket Connection Test</h3>
      <p><strong>Status:</strong> {connectionStatus}</p>
      
      <button 
        onClick={sendTestMessage}
        style={{
          padding: '10px 15px',
          backgroundColor: '#36b37e',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          marginBottom: '15px'
        }}
      >
        Send Test Message
      </button>
      
      <div style={{ 
        maxHeight: '300px', 
        overflowY: 'auto', 
        backgroundColor: 'white',
        padding: '10px',
        borderRadius: '4px',
        border: '1px solid #ddd'
      }}>
        <h4>Messages:</h4>
        {messages.map((msg, index) => (
          <div key={index} style={{ 
            padding: '2px 0', 
            borderBottom: '1px solid #eee',
            fontSize: '12px'
          }}>
            {msg}
          </div>
        ))}
        {messages.length === 0 && <p style={{ color: '#666' }}>No messages yet...</p>}
      </div>
    </div>
  );
};

export default WebSocketTest;