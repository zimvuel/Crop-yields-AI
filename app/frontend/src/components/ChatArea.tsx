import { useState, useRef, useEffect } from 'react';
import { Send, Menu, Sparkles } from 'lucide-react';
import { MessageBubble } from './MessageBubble';
import { SuggestionGrid } from './SuggestionGrid';
import type { ChatAreaProps } from '../types';

export function ChatArea({ 
  messages, 
  onSendMessage, 
  isLoading, 
  onToggleSidebar 
}: ChatAreaProps) {
  const [inputValue, setInputValue] = useState<string>('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [inputValue]);

  // Scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSubmit = (e: React.FormEvent | React.KeyboardEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;
    onSendMessage(inputValue);
    setInputValue('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <main className="flex h-full flex-1 flex-col bg-gray-950 relative">
      {/* Top Bar */}
      <div className="sticky top-0 z-10 flex h-16 items-center border-b border-gray-800 bg-gray-950/80 px-4 backdrop-blur-md md:hidden">
        <button 
          onClick={onToggleSidebar}
          className="mr-3 rounded-lg p-2 text-gray-400 hover:bg-gray-800 hover:text-white"
        >
          <Menu className="h-6 w-6" />
        </button>
        <span className="font-semibold text-white">Crop Helper AI</span>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center gap-8 py-10">
            <div className="flex flex-col items-center gap-4 text-center">
              <div className="mb-4 rounded-full bg-blue-500/10 p-4 ring-1 ring-blue-500/20">
                <Sparkles className="h-10 w-10 text-blue-400" />
              </div>
              <h1 className="text-3xl font-bold text-white tracking-tight sm:text-4xl">
                Apa yang bisa saya bantu hari ini?
              </h1>
              <p className="max-w-md text-gray-400">
                Tanyakan tentang jadwal penanaman tanaman atau prediksi cuaca untuk tanaman anda.
              </p>
            </div>
            <SuggestionGrid onSelect={onSendMessage} />
          </div>
        ) : (
          <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 py-4">
            {messages.map((msg, i) => (
              <MessageBubble 
                key={i} 
                message={msg.text} 
                isUser={msg.isUser} 
              />
            ))}
            {isLoading && <MessageBubble isLoading={true} />}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="p-4 bg-gray-950">
        <div className="mx-auto max-w-3xl">
          <form 
            onSubmit={handleSubmit}
            className="relative flex items-end gap-2 rounded-xl border border-gray-800 bg-gray-900 p-2 shadow-2xl focus-within:border-blue-500/50 focus-within:ring-1 focus-within:ring-blue-500/50 transition-all"
          >
            <textarea
              ref={textareaRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Tanyakan apapun tentang tanaman anda..."
              rows={1}
              className="max-h-50 min-h-11 w-full resize-none bg-transparent px-4 py-3 text-sm text-gray-100 placeholder-gray-500 focus:outline-none custom-scrollbar"
              style={{ height: '44px' }}
            />
            <button
              type="submit"
              disabled={!inputValue.trim() || isLoading}
              className="mb-1 mr-1 flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-blue-600 text-white transition-all hover:bg-blue-500 disabled:bg-gray-800 disabled:text-gray-500 disabled:cursor-not-allowed"
            >
              <Send className="h-5 w-5" />
            </button>
          </form>
          <div className="mt-2 text-center text-xs text-gray-500">
            AI bisa membuat kesalahan. Verifikasi informasi penting tentang tanaman anda dengan teliti.
          </div>
        </div>
      </div>
    </main>
  );
}
