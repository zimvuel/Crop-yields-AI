import { useState } from 'react';
import { Sidebar } from '../components/Sidebar';
import { ChatArea } from '../components/ChatArea';
import { useChat } from '../hooks/useChat';

export function ChatPage() {
  const { messages, isLoading,    handleSendMessage, 
    sessions, 
    loadSession, 
    startNewSession,
    handleDeleteSession
  } = useChat();
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);

  const handleNewChat = () => {
    startNewSession();
    setSidebarOpen(false);
  };

  return (
    <div className="flex h-screen w-full bg-gray-950 text-gray-100 overflow-hidden">
      <Sidebar 
        isOpen={sidebarOpen} 
        onClose={() => setSidebarOpen(false)}
        onNewChat={handleNewChat}
        sessions={sessions}
        onSelectSession={(id) => {
          loadSession(id);
          setSidebarOpen(false);
        }}
        onDeleteSession={handleDeleteSession}
      />
      
      <div className="flex-1 flex flex-col h-full relative w-full">
        <ChatArea 
          messages={messages}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          onToggleSidebar={() => setSidebarOpen(true)}
        />
      </div>
    </div>
  );
}
