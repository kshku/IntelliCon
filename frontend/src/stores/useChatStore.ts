import { create } from 'zustand';

export interface ToolCall {
  name: string;
  args?: any;
  output?: string;
  status: 'running' | 'completed' | 'error';
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  status?: 'sending' | 'streaming' | 'completed' | 'error';
  toolCalls?: ToolCall[];
}

interface ChatState {
  messages: Message[];
  sessionId: string;
  isStreaming: boolean;
  isConnected: boolean;
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => string;
  updateLastMessageContent: (content: string) => void;
  setStreaming: (isStreaming: boolean) => void;
  setConnected: (isConnected: boolean) => void;
  addToolCallToLastMessage: (toolName: string, args?: any) => void;
  updateToolResultInLastMessage: (toolName: string, output: string) => void;
  clearChat: () => void;
}

const generateUUID = () => {
  if (typeof window !== 'undefined' && window.crypto && window.crypto.randomUUID) {
    return window.crypto.randomUUID();
  }
  return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
};

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  sessionId: generateUUID(),
  isStreaming: false,
  isConnected: false,
  
  addMessage: (msg) => {
    const id = generateUUID();
    const newMessage: Message = {
      ...msg,
      id,
      timestamp: new Date().toISOString(),
    };
    set((state) => ({
      messages: [...state.messages, newMessage],
    }));
    return id;
  },

  updateLastMessageContent: (content) => {
    set((state) => {
      const newMessages = [...state.messages];
      const lastIdx = newMessages.length - 1;
      const last = newMessages[lastIdx];
      if (last && last.role === 'assistant') {
        newMessages[lastIdx] = { ...last, content: last.content + content, status: 'streaming' as const };
      }
      return { messages: newMessages };
    });
  },

  setStreaming: (isStreaming) => set({ isStreaming }),
  setConnected: (isConnected) => set({ isConnected }),

  addToolCallToLastMessage: (toolName, args) => {
    set((state) => {
      const newMessages = [...state.messages];
      const lastIdx = newMessages.length - 1;
      const last = newMessages[lastIdx];
      if (last && last.role === 'assistant') {
        const existingToolCalls = last.toolCalls || [];
        if (!existingToolCalls.some(t => t.name === toolName && t.status === 'running')) {
          newMessages[lastIdx] = {
            ...last,
            toolCalls: [...existingToolCalls, { name: toolName, args, status: 'running' as const }],
          };
        }
      }
      return { messages: newMessages };
    });
  },

  updateToolResultInLastMessage: (toolName, output) => {
    set((state) => {
      const newMessages = [...state.messages];
      const lastIdx = newMessages.length - 1;
      const last = newMessages[lastIdx];
      if (last && last.role === 'assistant' && last.toolCalls) {
        newMessages[lastIdx] = {
          ...last,
          toolCalls: last.toolCalls.map((t) => {
            if (t.name === toolName && t.status === 'running') {
              return { ...t, output, status: 'completed' as const };
            }
            return t;
          }),
        };
      }
      return { messages: newMessages };
    });
  },

  clearChat: () => set(() => ({
    messages: [],
    sessionId: generateUUID(),
    isStreaming: false,
  })),
}));
