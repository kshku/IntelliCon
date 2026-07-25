import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Send, Sparkles, Terminal, Activity, Wifi, WifiOff } from 'lucide-react';
import { useWebSocket } from '../hooks/useWebSocket';
import { useChatStore } from '../stores/useChatStore';

export const ChatPage: React.FC = () => {
  const { t } = useTranslation();
  const { isConnected, sendMessage } = useWebSocket();
  const { messages, isStreaming } = useChatStore();
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;
    sendMessage(input);
    setInput('');
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isStreaming]);

  const suggestions = [
    "Analyze property crime trends in Koramangala",
    "List all active investigations under IPC section 379",
    "Identify connection pathways between repeat offender 'Raju' and 'Kumar'",
    "Generate a summary report for violent crimes in Yeshwanthpur division"
  ];

  return (
    <div className="h-[calc(100vh-154px)] flex flex-col font-sans max-w-[1000px] mx-auto bg-white rounded-card border border-border-light shadow-sm overflow-hidden">
      {/* Header bar of Chat Workspace */}
      <div className="px-6 py-4 border-b border-border-light flex items-center justify-between bg-white z-10">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-btn bg-blue-50 flex items-center justify-center text-primary-blue">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-[16px] font-bold text-heading-dark leading-tight">AI Investigative Assistant</h2>
            <span className="text-[12px] text-gray-text font-medium">Powered by LangGraph ReAct Agent</span>
          </div>
        </div>

        {/* Connection status badge */}
        <div className="flex items-center gap-2">
          {isConnected ? (
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-green-50 border border-green-200 text-green-700 text-[12px] font-bold">
              <Wifi className="w-3.5 h-3.5" />
              <span>Online</span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-50 border border-amber-200 text-amber-700 text-[12px] font-bold animate-pulse">
              <WifiOff className="w-3.5 h-3.5" />
              <span>Connecting...</span>
            </div>
          )}
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/50">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center max-w-[600px] mx-auto space-y-8">
            <div className="w-16 h-16 rounded-2xl bg-blue-50 flex items-center justify-center text-primary-blue shadow-md shadow-blue-500/5">
              <Sparkles className="w-8 h-8" />
            </div>
            <div className="space-y-3">
              <h3 className="text-[20px] font-bold text-heading-dark">Ask the Crime Database Assistant</h3>
              <p className="text-[14px] text-gray-text font-medium leading-relaxed">
                Query FIR details, search suspect profiles, discover accomplice networks, or generate summaries using conversational English or Kannada.
              </p>
            </div>
            
            {/* Suggestion Cards */}
            <div className="grid grid-cols-2 gap-3.5 w-full text-left">
              {suggestions.map((s, idx) => (
                <button
                  key={idx}
                  onClick={() => setInput(s)}
                  className="p-4 rounded-btn bg-white border border-border-light hover:border-primary-blue hover:bg-blue-50/20 text-slate-700 hover:text-primary-blue transition-all duration-150 text-[13px] font-semibold text-left shadow-sm hover:shadow cursor-pointer"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.role !== 'user' && (
                  <div className="w-8 h-8 rounded-btn bg-blue-50 flex items-center justify-center text-primary-blue flex-shrink-0 border border-blue-100 shadow-sm">
                    <Sparkles className="w-4 h-4" />
                  </div>
                )}
                
                <div className="max-w-[80%] space-y-3">
                  {/* Message bubble card */}
                  <div className={`p-4 rounded-card shadow-sm border text-[14px] font-medium leading-relaxed ${
                    msg.role === 'user'
                      ? 'bg-primary-blue border-blue-600 text-white rounded-tr-none'
                      : 'bg-white border-border-light text-heading-dark rounded-tl-none'
                  }`}>
                    {msg.content ? (
                      <p className="whitespace-pre-wrap">{msg.content}</p>
                    ) : (
                      msg.status === 'streaming' && (
                        <div className="flex items-center gap-1.5 py-1">
                          <span className="w-1.5 h-1.5 bg-primary-blue rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                          <span className="w-1.5 h-1.5 bg-primary-blue rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                          <span className="w-1.5 h-1.5 bg-primary-blue rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                        </div>
                      )
                    )}
                  </div>

                  {/* Tool execution audit trace */}
                  {msg.toolCalls && msg.toolCalls.length > 0 && (
                    <div className="rounded-btn border border-slate-100 bg-slate-100/50 p-3 space-y-2 max-w-full overflow-hidden">
                      <div className="flex items-center gap-1.5 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                        <Terminal className="w-3.5 h-3.5 text-slate-400" />
                        <span>Investigation Log</span>
                      </div>
                      <div className="space-y-2">
                        {msg.toolCalls.map((t, tIdx) => (
                          <div key={tIdx} className="bg-white border border-slate-200/60 rounded-btn p-2 text-[12px] font-mono shadow-sm">
                            <div className="flex items-center justify-between">
                              <span className="text-slate-700 font-bold flex items-center gap-1.5">
                                <Activity className="w-3 h-3 text-blue-500 animate-pulse" />
                                {t.name}
                              </span>
                              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                t.status === 'completed' 
                                  ? 'bg-green-50 text-green-700' 
                                  : 'bg-blue-50 text-blue-700'
                              }`}>
                                {t.status}
                              </span>
                            </div>
                            {t.args && (
                              <div className="mt-1 bg-slate-50 p-1.5 rounded text-slate-500 overflow-x-auto text-[11px]">
                                <span className="font-bold text-slate-600">Args:</span> {JSON.stringify(t.args)}
                              </div>
                            )}
                            {t.output && (
                              <div className="mt-1.5 border-t border-slate-100 pt-1.5 text-slate-600 overflow-x-auto text-[11px] max-h-24 overflow-y-auto">
                                <span className="font-bold text-slate-700">Output:</span> {t.output}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {msg.role === 'user' && (
                  <div className="w-8 h-8 rounded-btn bg-blue-600 flex items-center justify-center text-white flex-shrink-0 border border-blue-700 shadow-sm">
                    <span className="text-[12px] font-bold">U</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input panel at bottom */}
      <form onSubmit={handleSend} className="p-4 border-t border-border-light bg-white flex gap-3">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isStreaming}
          placeholder={t('common.ask_placeholder')}
          className="flex-1 h-12 px-5 rounded-btn bg-bg-light border border-border-light text-[14px] text-heading-dark placeholder-slate-400 focus:outline-none focus:border-primary-blue focus:ring-2 focus:ring-primary-blue/10 transition-all font-medium disabled:opacity-60"
        />
        <button
          type="submit"
          disabled={!input.trim() || isStreaming}
          className="h-12 w-12 rounded-btn bg-primary-blue hover:bg-blue-600 disabled:bg-slate-100 text-white disabled:text-slate-400 flex items-center justify-center shadow-md shadow-blue-500/10 hover:shadow-lg hover:shadow-blue-500/20 active:scale-98 transition-all cursor-pointer"
        >
          <Send className="w-5 h-5" strokeWidth={2} />
        </button>
      </form>
    </div>
  );
};
