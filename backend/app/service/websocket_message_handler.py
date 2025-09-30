from datetime import datetime
from app.service.message_service import ConversationService, MessageService, websocket_conversation_handle
from app.schemas.websocket_schema import ProgressMessage, WebSocketMessage
from app.service.websocket_service import query_agent_service_streaming
from app.infra.logger import setup_logger
from app.schemas.message_schema import MessageCreate
from fastapi import WebSocket
import json

logger = setup_logger(__name__)

async def websocket_message_handler(websocket: WebSocket, message_service: MessageService, conversation_service: ConversationService, convo_id : int, thread_id : str , user_id : int):
    # Receive user message
    user_input = await websocket.receive_text()
    try:
        # Parse JSON if it's structured data
        message_data = json.loads(user_input)
        user_message = message_data.get("content", user_input)
    except json.JSONDecodeError:
        # Plain text message
        user_message = user_input
    
    current_conversation_id, thread_id = await websocket_conversation_handle(conversation_service=conversation_service, current_conversation_id=convo_id  ,user_id=user_id)
    # Send conversation details to client
    conversation_info = WebSocketMessage(
        type="conversation_started",
        content=f"Created conversation {current_conversation_id} (Thread: {thread_id})"
    )
    await websocket.send_text(json.dumps(conversation_info.to_dict()))

    # Save user message to database
    await message_service.create_message(
        conversation_id=convo_id,
        message=MessageCreate(role="user", message=user_message)
    )

    # Echo user message back
    user_echo = WebSocketMessage(type="User", content=user_message, timestamp=datetime.now().isoformat())
    await websocket.send_text(json.dumps(user_echo.to_dict()))

    # Send initial thinking indicator
    thinking_indicator = ProgressMessage(type="progress", content="🤔 Agent is starting to analyze your request...", progress_type="initializing")
    await websocket.send_text(json.dumps(thinking_indicator.to_dict()))

    # Stream agent response with real-time progress (pass thread_id)
    agent_message = await query_agent_service_streaming(websocket, user_message, thread_id)

    # Save agent response to database
    if agent_message and agent_message.content:
        await message_service.create_message(
            conversation_id=convo_id,
            message=MessageCreate(role="assistant", message=agent_message.content)
        )

        # Update conversation activity
        await conversation_service.update_last_activity(convo_id)

    logger.info(f"THIS WAS THE LAST AGENT_MESSAGE -> {agent_message.content if agent_message else 'None'}")