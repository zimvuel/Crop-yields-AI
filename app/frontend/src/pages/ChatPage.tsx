import { useState } from 'react';
import { Sidebar } from '../components/Sidebar';
import { ChatArea } from '../components/ChatArea';
import { useChat } from '../hooks/useChat';

export function ChatPage() {
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);
  const { messages, isLoading, handleSendMessage, clearMessages } = useChat();

  const handleNewChat = () => {
    clearMessages();
    setSidebarOpen(false);
  };

  return (
    <div className="flex h-screen w-full bg-gray-950 text-gray-100 overflow-hidden">
      <Sidebar 
        isOpen={sidebarOpen} 
        onClose={() => setSidebarOpen(false)}
        onNewChat={handleNewChat}
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
