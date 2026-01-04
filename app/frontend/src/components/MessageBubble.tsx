import { Bot, User } from 'lucide-react';
import { cn } from '../utils/cn';
import type { MessageBubbleProps } from '../types';

export function MessageBubble({ message, isUser, isLoading }: MessageBubbleProps) {
  if (isLoading) {
    return (
      <div className="flex w-full items-start gap-3">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-600/20 text-blue-400">
          <Bot className="h-5 w-5" />
        </div>
        <div className="flex items-center gap-1 rounded-2xl bg-gray-800/50 px-4 py-3 text-gray-400">
          <span className="h-2 w-2 animate-bounce rounded-full bg-current" style={{ animationDelay: '0ms' }} />
          <span className="h-2 w-2 animate-bounce rounded-full bg-current" style={{ animationDelay: '150ms' }} />
          <span className="h-2 w-2 animate-bounce rounded-full bg-current" style={{ animationDelay: '300ms' }} />
        </div>
      </div>
    );
  }

  return (
    <div className={cn("flex w-full gap-3", isUser ? "justify-end" : "justify-start")}>
      {!isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-600/20 text-blue-400 mt-1">
          <Bot className="h-5 w-5" />
        </div>
      )}

      <div
        className={cn(
          "max-w-[80%] rounded-2xl px-5 py-3 text-sm leading-relaxed",
          isUser
            ? "bg-blue-600 text-white rounded-tr-sm"
            : "bg-gray-800/50 text-gray-100 rounded-tl-sm"
        )}
      >
        {message}
      </div>

       {isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-700 text-gray-300 mt-1">
          <User className="h-5 w-5" />
        </div>
      )}
    </div>
  );
}
