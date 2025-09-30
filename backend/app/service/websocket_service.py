# Agent service configuration
import json
import aiohttp
from app.infra.logger import setup_logger
from app.schemas.websocket_schema import ProgressMessage, WebSocketMessage
from fastapi import WebSocket
import os

logger = setup_logger(__name__)

AGENT_SERVICE_URL = os.getenv("AGENT_SERVICE_URL", "http://agent-service:8001")

async def query_agent_service_streaming(websocket: WebSocket, user_message: str, thread_id: str):
    """
    Query the agent service with streaming responses via WebSocket.

    This function sends a user message to the agent service and streams the response
    back to the client through the WebSocket connection. It handles both progress
    updates and final responses, converting them to appropriate WebSocket message formats.

    Args:
        websocket (WebSocket): The WebSocket connection to send responses to
        user_message (str): The user's query/message to send to the agent service

    Returns:
        None: Results are sent directly through the WebSocket connection

    Raises:
        aiohttp.ClientError: If connection to agent service fails
        Exception: For any other unexpected errors during processing

    Message Flow:
        1. Sends POST request to agent service /user_message/stream endpoint
        2. Processes streaming response line by line
        3. Converts agent responses to ProgressMessage or WebSocketMessage objects
        4. Sends formatted messages through WebSocket to client
        5. Handles final_response type messages as agent responses

    Error Handling:
        - Agent service errors: Sends error message through WebSocket
        - Connection errors: Logs and sends connection failure message
        - JSON parsing errors: Logs and continues processing
        - General exceptions: Logs and sends unexpected error message
    """
    reasoning_steps = []  # Collect reasoning steps

    try:
        async with aiohttp.ClientSession() as session:
            payload = {"query": user_message, "thread_id": thread_id}
            async with session.post(f"{AGENT_SERVICE_URL}/user_message/stream", json=payload, headers={"Content-Type": "application/json"}) as response:
                if response.status == 200:
                    # Process streaming response
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data: '):
                            try:
                                data = json.loads(line_str[6:])  # Remove 'data: ' prefix

                                # Collect reasoning step - only add if it's not the final response
                                if data.get("type") != "final_response":
                                    reasoning_step = {
                                        "type": data.get("type", "unknown"),
                                        "content": data.get("message", ""),
                                        "tool_name": data.get("tool_name"),
                                        "tool_args": data.get("tool_args"),
                                        "timestamp": data.get("timestamp")
                                    }
                                    reasoning_steps.append(reasoning_step)

                                # Send progress update to WebSocket
                                progress_message = ProgressMessage(
                                    type="progress",
                                    content=data.get("message", "Processing..."),
                                    progress_type=data.get("type", "unknown"),
                                    tool_name=data.get("tool_name"),
                                    tool_args=data.get("tool_args")
                                )
                                await websocket.send_text(json.dumps(progress_message.to_dict()))

                                # If it's the final response, send it as agent message
                                if data.get("type") == "final_response":
                                    final_message = WebSocketMessage( type="Agent", content=data.get("content", "No response available"))
                                    final_message.reasoning_steps = reasoning_steps  # Attach reasoning steps
                                    await websocket.send_text(json.dumps(final_message.to_dict()))
                                    return final_message

                            except json.JSONDecodeError as e:
                                logger.error(f"Failed to parse streaming data: {line_str}")
                                continue
                else:
                    error_text = await response.text()
                    logger.error(f"Agent service error {response.status}: {error_text}")
                    error_message = WebSocketMessage(type="Agent", content=f"Agent service error: {response.status}")
                    await websocket.send_text(json.dumps(error_message.to_dict()))

    except aiohttp.ClientError as e:
        logger.error(f"Failed to connect to agent service: {str(e)}")
        error_message = WebSocketMessage(type="Agent", content=f"Failed to connect to agent service. Please check if the service is running.")
        await websocket.send_text(json.dumps(error_message.to_dict()))
    except Exception as e:
        logger.error(f"Unexpected error querying agent service: {str(e)}")
        error_message = WebSocketMessage(type="Agent", content=f"Unexpected error:")
        await websocket.send_text(json.dumps(error_message.to_dict()))