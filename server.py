import asyncio
import websockets
import json

# Store connected users
connected_users = {}

# Mock user database (for login validation)
user_database = {
    "Sala": "password123",
    "John": "password456"
}

async def handle_client(websocket, path):
    try:
        # Receive authentication data
        data = await websocket.recv()
        credentials = json.loads(data)
        email = credentials.get("email")
        password = credentials.get("password")

        # Authenticate user
        if email in user_database and user_database[email] == password:
            # Store user in the connected list
            connected_users[email] = websocket
            await websocket.send(json.dumps({"status": "success", "message": "Login successful"}))

            # Notify all users about the updated online list
            await broadcast_user_list()

            # Keep connection open
            while True:
                try:
                    msg = await websocket.recv()
                    print(f"Message from {email}: {msg}")  # For debugging
                except websockets.exceptions.ConnectionClosed:
                    break

        else:
            await websocket.send(json.dumps({"status": "error", "message": "Invalid credentials"}))

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Remove user from the list on disconnect
        if email in connected_users:
            del connected_users[email]
            await broadcast_user_list()

async def broadcast_user_list():
    """Broadcasts the list of online users to all clients."""
    user_list = list(connected_users.keys())
    message = json.dumps({"type": "user_list", "users": user_list})

    # Send to all connected users
    await asyncio.gather(*[ws.send(message) for ws in connected_users.values()])

# Start the WebSocket server
start_server = websockets.serve(handle_client, "localhost", 5148)

print("WebSocket server started on ws://localhost:5148")

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
