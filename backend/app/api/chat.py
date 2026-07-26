from __future__ import annotations

import asyncio
import json
import logging

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from langchain_core.messages import AIMessage, HumanMessage

from app.agent import create_agent
from app.agent.streaming import stream_agent_response
from app.auth import decode_access_token
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Instantiate the agent graph and session manager once
graph, session_manager = create_agent()


@router.websocket("/ws")
async def chat_websocket(
    websocket: WebSocket,
    token: str | None = Query(default=None),
) -> None:
    if not token:
        await websocket.close(code=4001, reason="Authentication required")
        return

    try:
        decode_access_token(token)
    except Exception:
        await websocket.close(code=4001, reason="Invalid token")
        return

    await websocket.accept()
    logger.info("WebSocket connection established")

    try:
        while True:
            # Read message from the client
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json(
                    {"event": "error", "data": {"error": "Invalid JSON format"}}
                )
                continue

            user_msg = payload.get("message")
            session_id = payload.get("session_id", "default-session")
            llm_provider = payload.get("llm_provider")
            llm_model = payload.get("llm_model")
            api_key = payload.get("api_key")

            if not user_msg:
                await websocket.send_json({"event": "error", "data": {"error": "Empty message"}})
                continue

            # Load or initialize chat state/history from Redis
            state = await session_manager.load_session(session_id)
            if state is None:
                state = {
                    "messages": [],
                    "session_id": session_id,
                    "context": {},
                    "iteration_count": 0,
                }

            # Append the new user message to history
            state["messages"].append(HumanMessage(content=user_msg))
            state["iteration_count"] = 0

            config = {"configurable": {"thread_id": session_id}}

            # Check if LLM API key is provided (either from frontend override or backend settings)
            active_api_key = api_key or settings.LLM_API_KEY
            if not active_api_key:
                logger.warning("No LLM API key provided. Running in mock streaming fallback mode.")

                # Custom mock agent streaming
                mock_text = (
                    f"Intelligence response regarding investigation query: '{user_msg}'.\n\n"
                    "Data Analysed: Under IPC sections, Koramangala crime incidence shows a "
                    "downward trend, whereas robbery incidents in Whitefield are high. "
                    "Recommended action: deploy additional night patrols "
                    "and verify repeat offenders."
                )

                # Stream words one by one to simulate an active LLM agent
                words = mock_text.split(" ")
                for word in words:
                    await asyncio.sleep(0.05)
                    await websocket.send_json({"event": "message", "data": {"content": word + " "}})

                await websocket.send_json({"event": "done", "data": {}})

                # Persist the mock reply to history
                state["messages"].append(AIMessage(content=mock_text))
                await session_manager.save_session(session_id, state)
            else:
                agent_message_content = ""
                try:
                    active_provider = llm_provider or settings.LLM_PROVIDER
                    active_model = llm_model or settings.LLM_MODEL
                    current_graph, _ = create_agent(
                        provider=active_provider,
                        model=active_model,
                        api_key=active_api_key,
                    )
                    async for event in stream_agent_response(
                        current_graph,
                        state,  # type: ignore[arg-type]
                        config,
                        session_id=session_id,
                    ):
                        await websocket.send_json({"event": event.event, "data": event.data})
                        if event.event == "message":
                            agent_message_content += event.data.get("content", "")

                    if agent_message_content:
                        state["messages"].append(AIMessage(content=agent_message_content))
                        await session_manager.save_session(session_id, state)
                except Exception as exc:
                    logger.error("Error during agent flow: %s", exc, exc_info=True)
                    await websocket.send_json(
                        {"event": "error", "data": {"error": "Agent execution failed"}}
                    )

    except WebSocketDisconnect:
        logger.info("WebSocket connection disconnected by client")
    except Exception as err:
        logger.error("Unexpected WebSocket handler error: %s", err, exc_info=True)
