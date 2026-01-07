import type { ReactNode } from "react";

export interface Message {
  text: string;
  isUser: boolean;
}

export interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  onNewChat: () => void;
  sessions?: { id: string; title: string }[];
  onSelectSession?: (id: string) => void;
}


export interface MessageBubbleProps {
  message?: string;
  isUser?: boolean;
  isLoading?: boolean;
}

export interface SuggestionGridProps {
  onSelect: (text: string) => void;
}

export interface Suggestion {
  icon: ReactNode;
  text: string;
  label: string;
}

export interface ChatAreaProps {
  messages: Message[];
  onSendMessage: (text: string) => void;
  isLoading: boolean;
  onToggleSidebar: () => void;
}
