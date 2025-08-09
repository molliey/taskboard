#!/usr/bin/env python3
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws?user_id=test_python_user"
    
    print(f"Attempting to connect to: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!")
            
            # Send a test message
            test_message = {
                "type": "test_message",
                "payload": {
                    "message": "Hello from Python test!"
                }
            }
            
            await websocket.send(json.dumps(test_message))
            print(f"📤 Sent: {test_message}")
            
            # Listen for responses
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📨 Received: {response}")
            except asyncio.TimeoutError:
                print("⏰ No response received within 5 seconds")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())