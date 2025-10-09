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
        # Get conversation_id and thread_id from message if provided
        convo_id = message_data.get("conversation_id") or convo_id
        thread_id = message_data.get("thread_id") or thread_id
    except json.JSONDecodeError:
        # Plain text message
        user_message = user_input

    # Echo user message back
    user_echo = WebSocketMessage(type="User", content=user_message, timestamp=datetime.now().isoformat())
    await websocket.send_text(json.dumps(user_echo.to_dict()))

    # Send initial thinking indicator
    thinking_indicator = ProgressMessage(type="progress", content="🤔 Agent is starting to analyze your request...", progress_type="initializing")
    await websocket.send_text(json.dumps(thinking_indicator.to_dict()))

    # Determine if this is a new conversation
    is_new_conversation = not convo_id
    if is_new_conversation:
        thread_id = f"user_{user_id}_{int(datetime.now().timestamp())}"

    # Stream agent response with real-time progress (pass thread_id and is_new_conversation)
    agent_message, chat_title = await query_agent_service_streaming(websocket=websocket, user_id=user_id, user_name='Daniel',user_message=user_message, thread_id=thread_id, is_new_conversation=is_new_conversation)

    # Use default title if none was generated
    title = chat_title or "New Conversation"
    current_conversation_id, thread_id = await websocket_conversation_handle(conversation_service=conversation_service, thread_id=thread_id, current_conversation_id=convo_id  ,user_id=user_id , title=title)

    # Send conversation details to client if this is a new conversation
    if is_new_conversation:
        conversation_info = {
            "type": "conversation_started",
            "conversation_id": current_conversation_id,
            "thread_id": thread_id,
            "content": f"Started conversation {current_conversation_id}",
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send_text(json.dumps(conversation_info))

    # Save user message to database
    await message_service.create_message(
        conversation_id=current_conversation_id,
        message=MessageCreate(role="user", message=user_message)
    )

    # Update conversation title if this is a new conversation and we got a title
    if is_new_conversation:
        conversation = await conversation_service.get_conversation_by_conversation_id(current_conversation_id)
        if conversation:
            conversation.title = chat_title
            await conversation_service.repo.add_conversation_message(conversation)
            logger.info(f"Updated conversation {current_conversation_id} title to: {chat_title}")

    # Save agent response to database
    if agent_message and agent_message.content:
        await message_service.create_message(
            conversation_id=current_conversation_id,
            message=MessageCreate(
                role="agent",
                message=agent_message.content,
                reasoning_steps=getattr(agent_message, 'reasoning_steps', None)
            )
        )

        # Update conversation activity
        await conversation_service.update_last_activity(current_conversation_id)