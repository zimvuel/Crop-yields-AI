import { Plus, MessageSquare, Trash2 } from 'lucide-react';
import { cn } from '../utils/cn';
import type { SidebarProps } from '../types';

export function Sidebar({ isOpen, onClose, onNewChat, sessions, onSelectSession, onDeleteSession }: SidebarProps & { onDeleteSession?: (id: string) => void }) {
  return (
    <>
      {/* Mobile Overlay */}
      <div 
        className={cn(
          "fixed inset-0 z-20 bg-black/50 transition-opacity md:hidden",
          isOpen ? "opacity-100" : "opacity-0 pointer-events-none"
        )}
        onClick={onClose}
      />

      {/* Sidebar Container */}
      <aside 
        className={cn(
          "fixed inset-y-0 left-0 z-30 flex w-65 flex-col bg-gray-900 text-gray-100 transition-transform duration-300 md:static md:translate-x-0 border-r border-gray-800/50",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* New Chat */}
        <div className="p-4">
          <button 
            onClick={onNewChat}
            className="flex w-full items-center gap-2 rounded-lg border border-gray-700 bg-gray-800/50 px-3 py-3 text-sm font-medium transition-colors hover:bg-gray-800 hover:text-white"
          >
            <Plus className="h-4 w-4" />
            Percakapan Baru
          </button>
        </div>

        {/* History List */}
        <div className="flex-1 overflow-y-auto px-2 py-2">
          <div className="mb-2 px-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
            Riwayat
          </div>
          <div className="space-y-1">
            {sessions?.map((item) => (
              <button
                key={item.id}
                onClick={() => onSelectSession?.(item.id)}
                className="group flex w-full items-center gap-3 rounded-lg px-2 py-2.5 text-sm text-gray-300 hover:bg-gray-800/70 hover:text-white transition-colors text-left"
              >
                <MessageSquare className="h-4 w-4 text-gray-500 group-hover:text-gray-300" />
                <span className="truncate flex-1">{item.title}</span>
                {onDeleteSession && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteSession(item.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-500/20 rounded transition-all"
                  >
                    <Trash2 className="h-3.5 w-3.5 text-gray-500 hover:text-red-500" />
                  </button>
                )}
              </button>
            ))}
          </div>
        </div>
      </aside>
    </>
  );
}
