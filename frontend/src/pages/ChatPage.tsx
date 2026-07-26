import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Send, Sparkles, Terminal, Activity, Wifi, WifiOff, Mic, MicOff, Volume2, VolumeX, ChevronDown, ChevronRight, Brain, Plus, Trash2, Edit3, MessageSquare, Check, X } from 'lucide-react';
import { useWebSocket } from '../hooks/useWebSocket';
import { useChatStore } from '../stores/useChatStore';
import { useVoiceRecognition } from '../hooks/useVoiceRecognition';
import { useSpeechSynthesis } from '../hooks/useSpeechSynthesis';
import { useLanguageStore } from '../stores/useLanguageStore';

export const ChatPage: React.FC = () => {
  const { t } = useTranslation();
  const { isConnected, sendMessage } = useWebSocket();
  const {
    messages,
    isStreaming,
    conversations,
    activeSessionId,
    createNewChat,
    switchChat,
    deleteChat,
    renameChat,
  } = useChatStore();
  const [input, setInput] = useState('');
  const [expandedReasoning, setExpandedReasoning] = useState<Set<string>>(new Set());
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleRename = (id: string) => {
    if (editTitle.trim()) {
      renameChat(id, editTitle.trim());
    }
    setEditingSessionId(null);
  };

  const toggleReasoning = (msgId: string) => {
    setExpandedReasoning((prev) => {
      const next = new Set(prev);
      if (next.has(msgId)) next.delete(msgId);
      else next.add(msgId);
      return next;
    });
  };

  const { language } = useLanguageStore();
  const voiceLang = language === 'kn' ? 'kn-IN' : 'en-US';

  const {
    isListening,
    interimTranscript,
    startListening,
    stopListening,
    isSupported: sttSupported,
  } = useVoiceRecognition({
    lang: voiceLang,
    continuous: false,
    interimResults: true,
    onResult: (text) => {
      setInput(text);
      if (text.trim()) {
        sendMessage(text);
      }
    },
  });

  const {
    speak,
    stop: stopSpeaking,
    isSpeaking,
    isSupported: ttsSupported,
  } = useSpeechSynthesis({ lang: voiceLang });

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
    t('chat.suggestion_1'),
    t('chat.suggestion_2'),
    t('chat.suggestion_3'),
    t('chat.suggestion_4'),
  ];

  return (
    <div className="h-[calc(100vh-154px)] flex font-sans max-w-[1200px] mx-auto bg-white rounded-card border border-border-light shadow-sm overflow-hidden">
      {/* Left Chat Sessions Sidebar */}
      <div className="w-64 bg-slate-50 border-r border-border-light flex flex-col h-full flex-shrink-0">
        {/* New Chat Button */}
        <div className="p-4 border-b border-border-light">
          <button
            type="button"
            onClick={createNewChat}
            className="w-full h-10 rounded-btn border border-primary-blue/30 text-primary-blue bg-white hover:bg-blue-50 font-bold text-[13px] flex items-center justify-center gap-1.5 transition-all cursor-pointer shadow-sm hover:shadow"
          >
            <Plus className="w-4 h-4" />
            <span>New Chat</span>
          </button>
        </div>

        {/* Conversation List */}
        <div className="flex-1 overflow-y-auto p-3 space-y-1">
          {conversations.map((conv) => {
            const isActive = conv.id === activeSessionId;
            const isEditing = conv.id === editingSessionId;

            return (
              <div
                key={conv.id}
                onClick={() => !isEditing && switchChat(conv.id)}
                className={`group flex items-center justify-between p-2.5 rounded-btn text-[13px] font-semibold transition-all cursor-pointer ${
                  isActive
                    ? 'bg-blue-50/70 text-primary-blue border border-blue-100/70'
                    : 'text-heading-dark hover:bg-slate-100 border border-transparent'
                }`}
              >
                <div className="flex items-center gap-2 truncate flex-1 pr-2" onClick={(e) => isEditing && e.stopPropagation()}>
                  <MessageSquare className={`w-4 h-4 flex-shrink-0 ${isActive ? 'text-primary-blue' : 'text-slate-400'}`} />
                  
                  {isEditing ? (
                    <input
                      type="text"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleRename(conv.id);
                        if (e.key === 'Escape') setEditingSessionId(null);
                      }}
                      className="w-full bg-white border border-primary-blue/50 rounded px-1.5 py-0.5 text-[12px] font-semibold focus:outline-none"
                      autoFocus
                    />
                  ) : (
                    <span className="truncate">{conv.title}</span>
                  )}
                </div>

                {/* Actions: Edit / Delete */}
                {!isEditing && (
                  <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        setEditingSessionId(conv.id);
                        setEditTitle(conv.title);
                      }}
                      className="p-1 rounded text-slate-400 hover:text-primary-blue hover:bg-slate-200 transition-colors"
                      title="Rename Chat"
                    >
                      <Edit3 className="w-3.5 h-3.5" />
                    </button>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteChat(conv.id);
                      }}
                      className="p-1 rounded text-slate-400 hover:text-red-500 hover:bg-slate-200 transition-colors"
                      title="Delete Chat"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                )}

                {isEditing && (
                  <div className="flex items-center gap-0.5" onClick={(e) => e.stopPropagation()}>
                    <button
                      type="button"
                      onClick={() => handleRename(conv.id)}
                      className="p-1 text-green-600 hover:bg-slate-200 rounded"
                    >
                      <Check className="w-3.5 h-3.5" />
                    </button>
                    <button
                      type="button"
                      onClick={() => setEditingSessionId(null)}
                      className="p-1 text-red-600 hover:bg-slate-200 rounded"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Right Chat Container Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Header bar of Chat Workspace */}
        <div className="px-6 py-4 border-b border-border-light flex items-center justify-between bg-white z-10">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-btn bg-blue-50 flex items-center justify-center text-primary-blue">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-[16px] font-bold text-heading-dark leading-tight">{t('chat.ai_investigative_assistant')}</h2>
            <span className="text-[12px] text-gray-text font-medium">{t('chat.powered_by')}</span>
          </div>
        </div>

        {/* Connection status + Voice controls */}
        <div className="flex items-center gap-2">
          {sttSupported && (
            <button
              onClick={isListening ? stopListening : startListening}
              className={`w-9 h-9 rounded-btn flex items-center justify-center transition-all cursor-pointer ${
                isListening
                  ? 'bg-red-50 text-red-600 border border-red-200 animate-pulse'
                  : 'bg-slate-50 text-slate-500 border border-slate-200 hover:bg-slate-100'
              }`}
              title={isListening ? t('chat.stop_listening') : t('chat.voice_mode')}
            >
              {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </button>
          )}

          {ttsSupported && (
            <button
              onClick={isSpeaking ? stopSpeaking : () => {
                const lastAssistant = [...messages].reverse().find(m => m.role === 'assistant' && m.content);
                if (lastAssistant) speak(lastAssistant.content);
              }}
              className={`w-9 h-9 rounded-btn flex items-center justify-center transition-all cursor-pointer ${
                isSpeaking
                  ? 'bg-blue-50 text-blue-600 border border-blue-200'
                  : 'bg-slate-50 text-slate-500 border border-slate-200 hover:bg-slate-100'
              }`}
              title={isSpeaking ? t('chat.stop_speaking') : t('chat.speak_response')}
            >
              {isSpeaking ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
            </button>
          )}

          {isConnected ? (
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-green-50 border border-green-200 text-green-700 text-[12px] font-bold">
              <Wifi className="w-3.5 h-3.5" />
              <span>{t('common.online')}</span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-50 border border-amber-200 text-amber-700 text-[12px] font-bold animate-pulse">
              <WifiOff className="w-3.5 h-3.5" />
              <span>{t('common.connecting')}</span>
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
              <h3 className="text-[20px] font-bold text-heading-dark">{t('chat.ask_crime_database')}</h3>
              <p className="text-[14px] text-gray-text font-medium leading-relaxed">
                {t('chat.chat_description')}
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

                  {/* Show reasoning toggle */}
                  {msg.role === 'assistant' && msg.reasoning && (
                    <div className="rounded-btn border border-purple-100 bg-purple-50/50 overflow-hidden">
                      <button
                        onClick={() => toggleReasoning(msg.id)}
                        className="w-full flex items-center gap-2 px-3 py-2 text-[12px] font-bold text-purple-700 hover:bg-purple-100/50 transition-colors cursor-pointer"
                      >
                        <Brain className="w-3.5 h-3.5" />
                        <span>Show Reasoning</span>
                        {expandedReasoning.has(msg.id) ? (
                          <ChevronDown className="w-3.5 h-3.5 ml-auto" />
                        ) : (
                          <ChevronRight className="w-3.5 h-3.5 ml-auto" />
                        )}
                      </button>
                      {expandedReasoning.has(msg.id) && (
                        <div className="px-3 pb-3 text-[12px] font-mono text-purple-900 whitespace-pre-wrap leading-relaxed border-t border-purple-100 pt-2">
                          {msg.reasoning}
                        </div>
                      )}
                    </div>
                  )}

                  {/* TTS button on assistant messages */}
                  {msg.role === 'assistant' && msg.content && ttsSupported && (
                    <button
                      onClick={() => {
                        if (isSpeaking) {
                          stopSpeaking();
                        } else {
                          speak(msg.content);
                        }
                      }}
                      className="w-7 h-7 rounded-btn flex items-center justify-center text-slate-400 hover:text-primary-blue hover:bg-blue-50 transition-all cursor-pointer"
                      title={isSpeaking ? t('chat.stop_speaking') : t('chat.speak_response')}
                    >
                      {isSpeaking ? <VolumeX className="w-3.5 h-3.5" /> : <Volume2 className="w-3.5 h-3.5" />}
                    </button>
                  )}

                  {/* Tool execution audit trace */}
                  {msg.toolCalls && msg.toolCalls.length > 0 && (
                    <div className="rounded-btn border border-slate-100 bg-slate-100/50 p-3 space-y-2 max-w-full overflow-hidden">
                      <div className="flex items-center gap-1.5 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                        <Terminal className="w-3.5 h-3.5 text-slate-400" />
                        <span>{t('chat.investigation_log')}</span>
                      </div>
                      <div className="space-y-2">
                        {msg.toolCalls.map((tc, tIdx) => (
                          <div key={tIdx} className="bg-white border border-slate-200/60 rounded-btn p-2 text-[12px] font-mono shadow-sm">
                            <div className="flex items-center justify-between">
                              <span className="text-slate-700 font-bold flex items-center gap-1.5">
                                <Activity className="w-3 h-3 text-blue-500 animate-pulse" />
                                {tc.name}
                              </span>
                              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                tc.status === 'completed' 
                                  ? 'bg-green-50 text-green-700' 
                                  : 'bg-blue-50 text-blue-700'
                              }`}>
                                {tc.status}
                              </span>
                            </div>
                            {tc.args && (
                              <div className="mt-1 bg-slate-50 p-1.5 rounded text-slate-500 overflow-x-auto text-[11px]">
                                <span className="font-bold text-slate-600">{t('chat.args')}</span> {JSON.stringify(tc.args)}
                              </div>
                            )}
                            {tc.output && (
                              <div className="mt-1.5 border-t border-slate-100 pt-1.5 text-slate-600 overflow-x-auto text-[11px] max-h-24 overflow-y-auto">
                                <span className="font-bold text-slate-700">{t('chat.output')}</span> {tc.output}
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
      <form onSubmit={handleSend} className="relative p-4 border-t border-border-light bg-white flex gap-3">
        {isListening && (
          <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-4 py-2 bg-red-50 border border-red-200 rounded-full text-[12px] font-bold text-red-600 flex items-center gap-2 animate-pulse">
            <Mic className="w-3.5 h-3.5" />
            {t('chat.listening')}
            {interimTranscript && (
              <span className="text-red-400 ml-1 max-w-[200px] truncate">{interimTranscript}</span>
            )}
          </div>
        )}

        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isStreaming || isListening}
          placeholder={isListening ? t('chat.listening') : t('common.ask_placeholder')}
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
  </div>
  );
};
