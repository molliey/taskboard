// Simple WebSocket test utility
export function testWebSocketConnection() {
  const testUrls = [
    'ws://localhost:8000/ws',
    'ws://localhost:8080/ws', 
    'ws://localhost:3001/ws'
  ];

  const testConnection = (url, userId = 'test_user') => {
    return new Promise((resolve) => {
      console.log(`Testing WebSocket connection to: ${url}`);
      
      try {
        const ws = new WebSocket(`${url}?user_id=${userId}`);
        
        const timeout = setTimeout(() => {
          ws.close();
          resolve({ url, success: false, error: 'Connection timeout' });
        }, 5000);
        
        ws.onopen = () => {
          clearTimeout(timeout);
          console.log(`✅ WebSocket connected successfully to: ${url}`);
          ws.close();
          resolve({ url, success: true });
        };
        
        ws.onerror = (error) => {
          clearTimeout(timeout);
          console.log(`❌ WebSocket connection failed to: ${url}`, error);
          resolve({ url, success: false, error: error.message || 'Connection failed' });
        };
        
        ws.onclose = (event) => {
          if (event.code !== 1000) {
            console.log(`WebSocket closed unexpectedly: ${url}`, event.code, event.reason);
          }
        };
        
      } catch (error) {
        console.log(`❌ WebSocket creation failed for: ${url}`, error);
        resolve({ url, success: false, error: error.message });
      }
    });
  };

  // Test all URLs
  Promise.all(testUrls.map(url => testConnection(url)))
    .then(results => {
      console.log('\n=== WebSocket Connection Test Results ===');
      results.forEach(result => {
        const status = result.success ? '✅ SUCCESS' : '❌ FAILED';
        console.log(`${status}: ${result.url}`);
        if (!result.success && result.error) {
          console.log(`   Error: ${result.error}`);
        }
      });
      
      const successfulConnections = results.filter(r => r.success);
      if (successfulConnections.length > 0) {
        console.log(`\n🎉 Found ${successfulConnections.length} working WebSocket endpoint(s)`);
        return successfulConnections[0].url;
      } else {
        console.log('\n⚠️  No WebSocket endpoints are available');
        return null;
      }
    });
}

// Auto-run test when imported in development
if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
  testWebSocketConnection();
}