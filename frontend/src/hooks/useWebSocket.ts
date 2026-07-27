import { useEffect, useRef, useCallback } from 'react';
import { useChatStore } from '../stores/useChatStore';

const RECONNECT_INTERVAL = 3000;
const MAX_RECONNECT_ATTEMPTS = 5;
const MAX_RECONNECT_INTERVAL = 30000;

const getWsUrl = () => {
  const token = localStorage.getItem('token') || '';
  const apiBase = import.meta.env.VITE_API_URL;
  let baseUrl = '';

  if (apiBase) {
    const url = new URL('/api/chat/ws', apiBase);
    url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
    baseUrl = url.toString();
  } else {
    const loc = window.location;
    if (loc.hostname === 'localhost' || loc.hostname === '127.0.0.1') {
      baseUrl = 'ws://localhost:8000/api/chat/ws';
    } else {
      const proto = loc.protocol === 'https:' ? 'wss:' : 'ws:';
      baseUrl = `${proto}//${loc.host}/api/chat/ws`;
    }
  }

  return token ? `${baseUrl}?token=${encodeURIComponent(token)}` : baseUrl;
};

export const useWebSocket = () => {
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const reconnectAttemptsRef = useRef(0);
  
  const {
    sessionId,
    isConnected,
    setConnected,
    setStreaming,
    addMessage,
    updateLastMessageContent,
    addToolCallToLastMessage,
    updateToolResultInLastMessage,
    updateLastMessageReasoning,
  } = useChatStore();

  const connect = useCallback(() => {
    if (socketRef.current?.readyState === WebSocket.OPEN) return;

    try {
      const url = getWsUrl();
      const ws = new WebSocket(url);
      socketRef.current = ws;

      ws.onopen = () => {
        console.log('Chat WebSocket connected');
        setConnected(true);
        reconnectAttemptsRef.current = 0;
        if (reconnectTimeoutRef.current) {
          window.clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }
      };

      ws.onclose = () => {
        console.log('Chat WebSocket closed');
        setConnected(false);
        setStreaming(false);
        if (reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
          const delay = Math.min(RECONNECT_INTERVAL * Math.pow(2, reconnectAttemptsRef.current), MAX_RECONNECT_INTERVAL);
          reconnectAttemptsRef.current += 1;
          console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current}/${MAX_RECONNECT_ATTEMPTS})`);
          reconnectTimeoutRef.current = window.setTimeout(() => {
            connect();
          }, delay);
        } else {
          console.warn('Max WebSocket reconnect attempts reached');
        }
      };

      ws.onerror = (err) => {
        console.error('Chat WebSocket error:', err);
        ws.close();
      };

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          const { event: type, data } = payload;

          switch (type) {
            case 'message':
              updateLastMessageContent(data.content);
              break;
            case 'tool_call':
              addToolCallToLastMessage(data.tool, data.args);
              break;
            case 'tool_result':
              updateToolResultInLastMessage(data.tool, data.output);
              break;
            case 'reasoning':
              updateLastMessageReasoning(data.content);
              break;
            case 'done':
              setStreaming(false);
              break;
            case 'error':
              console.error('Agent error event:', data.error);
              updateLastMessageContent(`\n[Error: ${data.error}]`);
              setStreaming(false);
              break;
            default:
              console.warn('Unknown event type:', type);
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };
    } catch (err) {
      console.error('Failed to establish WebSocket connection:', err);
      if (reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
        const delay = Math.min(RECONNECT_INTERVAL * Math.pow(2, reconnectAttemptsRef.current), MAX_RECONNECT_INTERVAL);
        reconnectAttemptsRef.current += 1;
        reconnectTimeoutRef.current = window.setTimeout(() => {
          connect();
        }, delay);
      }
    }
  }, [
    setConnected,
    setStreaming,
    updateLastMessageContent,
    addToolCallToLastMessage,
    updateToolResultInLastMessage,
    updateLastMessageReasoning,
  ]);

  const sendMessage = useCallback((text: string) => {
    if (!text.trim()) return;

    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      console.error('WebSocket is not connected');
      addMessage({
        role: 'system',
        content: 'Failed to send message: Not connected to server. Attempting reconnect...',
      });
      connect();
      return;
    }

    // Add user message to history
    addMessage({
      role: 'user',
      content: text,
    });

    // Add placeholder assistant message for incoming stream
    addMessage({
      role: 'assistant',
      content: '',
      status: 'streaming',
    });

    setStreaming(true);

    const storedProvider = localStorage.getItem('intellicon_llm_provider') || 'openai';
    const storedModel = localStorage.getItem('intellicon_llm_model') || 'gpt-4o';
    const storedApiKey = localStorage.getItem('intellicon_api_key') || '';

    // Send payload to backend
    socketRef.current.send(JSON.stringify({
      message: text,
      session_id: sessionId,
      llm_provider: storedProvider,
      llm_model: storedModel,
      api_key: storedApiKey,
    }));
  }, [sessionId, addMessage, setStreaming, connect]);

  useEffect(() => {
    connect();

    return () => {
      if (socketRef.current) {
        // Clear listeners to prevent state updates on unmount
        socketRef.current.onopen = null;
        socketRef.current.onclose = null;
        socketRef.current.onerror = null;
        socketRef.current.onmessage = null;
        socketRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        window.clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connect]);

  return {
    isConnected,
    sendMessage,
  };
};
