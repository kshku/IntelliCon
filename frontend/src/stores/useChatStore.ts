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
  reasoning?: string;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  timestamp: string;
}

interface ChatState {
  conversations: Conversation[];
  activeSessionId: string;
  sessionId: string;
  messages: Message[];
  isStreaming: boolean;
  isConnected: boolean;
  
  // Actions
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => string;
  updateLastMessageContent: (content: string) => void;
  setStreaming: (isStreaming: boolean) => void;
  setConnected: (isConnected: boolean) => void;
  addToolCallToLastMessage: (toolName: string, args?: any) => void;
  updateToolResultInLastMessage: (toolName: string, output: string) => void;
  updateLastMessageReasoning: (content: string) => void;
  
  // Conversation actions
  createNewChat: () => void;
  switchChat: (id: string) => void;
  deleteChat: (id: string) => void;
  renameChat: (id: string, title: string) => void;
  clearChat: () => void;
}

const generateUUID = () => {
  if (typeof window !== 'undefined' && window.crypto && window.crypto.randomUUID) {
    return window.crypto.randomUUID();
  }
  return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
};

const initialSessionId = generateUUID();
const initialConversation: Conversation = {
  id: initialSessionId,
  title: 'New Chat',
  messages: [],
  timestamp: new Date().toISOString(),
};

export const useChatStore = create<ChatState>((set) => ({
  conversations: [initialConversation],
  activeSessionId: initialSessionId,
  sessionId: initialSessionId,
  messages: [],
  isStreaming: false,
  isConnected: false,
  
  addMessage: (msg) => {
    const id = generateUUID();
    const newMessage: Message = {
      ...msg,
      id,
      timestamp: new Date().toISOString(),
    };
    
    set((state) => {
      const updatedConversations = state.conversations.map((c) => {
        if (c.id === state.activeSessionId) {
          let title = c.title;
          if (c.messages.length === 0 && msg.role === 'user') {
            title = msg.content.length > 25 ? msg.content.substring(0, 25) + '...' : msg.content;
          }
          return {
            ...c,
            title,
            messages: [...c.messages, newMessage],
            timestamp: new Date().toISOString(),
          };
        }
        return c;
      });
      
      const active = updatedConversations.find(c => c.id === state.activeSessionId) || initialConversation;
      return {
        conversations: updatedConversations,
        messages: active.messages,
      };
    });
    
    return id;
  },

  updateLastMessageContent: (content) => {
    set((state) => {
      const updatedConversations = state.conversations.map((c) => {
        if (c.id === state.activeSessionId) {
          const newMessages = [...c.messages];
          const lastIdx = newMessages.length - 1;
          const last = newMessages[lastIdx];
          if (last && last.role === 'assistant') {
            newMessages[lastIdx] = { ...last, content: last.content + content, status: 'streaming' as const };
          }
          return { ...c, messages: newMessages };
        }
        return c;
      });
      
      const active = updatedConversations.find(c => c.id === state.activeSessionId) || initialConversation;
      return {
        conversations: updatedConversations,
        messages: active.messages,
      };
    });
  },

  setStreaming: (isStreaming) => set({ isStreaming }),
  setConnected: (isConnected) => set({ isConnected }),

  addToolCallToLastMessage: (toolName, args) => {
    set((state) => {
      const updatedConversations = state.conversations.map((c) => {
        if (c.id === state.activeSessionId) {
          const newMessages = [...c.messages];
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
          return { ...c, messages: newMessages };
        }
        return c;
      });
      
      const active = updatedConversations.find(c => c.id === state.activeSessionId) || initialConversation;
      return {
        conversations: updatedConversations,
        messages: active.messages,
      };
    });
  },

  updateToolResultInLastMessage: (toolName, output) => {
    set((state) => {
      const updatedConversations = state.conversations.map((c) => {
        if (c.id === state.activeSessionId) {
          const newMessages = [...c.messages];
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
          return { ...c, messages: newMessages };
        }
        return c;
      });
      
      const active = updatedConversations.find(c => c.id === state.activeSessionId) || initialConversation;
      return {
        conversations: updatedConversations,
        messages: active.messages,
      };
    });
  },

  updateLastMessageReasoning: (content) => {
    set((state) => {
      const updatedConversations = state.conversations.map((c) => {
        if (c.id === state.activeSessionId) {
          const newMessages = [...c.messages];
          const lastIdx = newMessages.length - 1;
          const last = newMessages[lastIdx];
          if (last && last.role === 'assistant') {
            newMessages[lastIdx] = {
              ...last,
              reasoning: (last.reasoning || '') + content,
            };
          }
          return { ...c, messages: newMessages };
        }
        return c;
      });
      
      const active = updatedConversations.find(c => c.id === state.activeSessionId) || initialConversation;
      return {
        conversations: updatedConversations,
        messages: active.messages,
      };
    });
  },

  createNewChat: () => {
    const newId = generateUUID();
    const newConv: Conversation = {
      id: newId,
      title: 'New Chat',
      messages: [],
      timestamp: new Date().toISOString(),
    };
    set((state) => ({
      conversations: [newConv, ...state.conversations],
      activeSessionId: newId,
      sessionId: newId,
      messages: [],
    }));
  },

  switchChat: (id) => {
    set((state) => {
      const active = state.conversations.find((c) => c.id === id);
      if (!active) return {};
      return {
        activeSessionId: id,
        sessionId: id,
        messages: active.messages,
      };
    });
  },

  deleteChat: (id) => {
    set((state) => {
      const remaining = state.conversations.filter((c) => c.id !== id);
      if (remaining.length === 0) {
        const fallbackId = generateUUID();
        const fallback: Conversation = {
          id: fallbackId,
          title: 'New Chat',
          messages: [],
          timestamp: new Date().toISOString(),
        };
        return {
          conversations: [fallback],
          activeSessionId: fallbackId,
          sessionId: fallbackId,
          messages: [],
        };
      }

      let nextActiveId = state.activeSessionId;
      if (state.activeSessionId === id) {
        nextActiveId = remaining[0].id;
      }

      const active = remaining.find((c) => c.id === nextActiveId) || remaining[0];
      return {
        conversations: remaining,
        activeSessionId: nextActiveId,
        sessionId: nextActiveId,
        messages: active.messages,
      };
    });
  },

  renameChat: (id, title) => {
    set((state) => {
      const updated = state.conversations.map((c) => {
        if (c.id === id) {
          return { ...c, title };
        }
        return c;
      });
      const active = updated.find(c => c.id === state.activeSessionId) || initialConversation;
      return {
        conversations: updated,
        messages: active.messages,
      };
    });
  },

  clearChat: () => set(() => {
    const freshId = generateUUID();
    const freshConv: Conversation = {
      id: freshId,
      title: 'New Chat',
      messages: [],
      timestamp: new Date().toISOString(),
    };
    return {
      conversations: [freshConv],
      activeSessionId: freshId,
      sessionId: freshId,
      messages: [],
      isStreaming: false,
    };
  }),
}));
