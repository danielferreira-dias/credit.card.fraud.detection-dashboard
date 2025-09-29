from app.security.security import SecurityManager
from app.ws.connection_manager import ConnectionManager
from app.schemas.websocket_schema import WebSocketMessage
from fastapi import WebSocket
import json

async def authenticate_websocket(websocket: WebSocket , security_manager: SecurityManager, token: str, connection_manager: ConnectionManager, user_id : int):
    try:
        # Validate token BEFORE accepting WebSocket connection
        payload = security_manager.verify_token(token)  
        authenticated_user_id = payload.get('id')  

        # Verify the user_id matches the token
        if authenticated_user_id != user_id:
            await websocket.close(code=4001, reason="Unauthorized: User ID mismatch")
            return
    except Exception as e:
        await websocket.close(code=4001, reason=f"Unauthorized: {str(e)}")
        return

    # Accept WebSocket connection after successful authentication
    await connection_manager.connect(websocket)

    # Send authentication success message
    auth_success = WebSocketMessage(
        type="auth_success",
        content=f"Successfully authenticated user {authenticated_user_id}"
    )
    await websocket.send_text(json.dumps(auth_success.to_dict()))