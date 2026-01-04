import { Plus, MessageSquare } from 'lucide-react';
import { cn } from '../utils/cn';
import type { SidebarProps } from '../types';

export function Sidebar({ isOpen, onClose, onNewChat }: SidebarProps) {
  // history data example
  const history = [
    "Prediksi Panen Jagung",
    "Penyakit Daun Padi",
    "Jadwal Pupuk Kedelai",
    "Analisa Tanah Lempung",
    "Cuaca Minggu Ini"
  ];

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
            {history.map((item, index) => (
              <button
                key={index}
                className="group flex w-full items-center gap-3 rounded-lg px-2 py-2.5 text-sm text-gray-300 hover:bg-gray-800/70 hover:text-white transition-colors text-left"
              >
                <MessageSquare className="h-4 w-4 text-gray-500 group-hover:text-gray-300" />
                <span className="truncate">{item}</span>
              </button>
            ))}
          </div>
        </div>

        {/* User */}
        <div className="border-t border-gray-800 p-4">
          <div className="flex items-center gap-3 rounded-lg p-2 hover:bg-gray-800/50 transition-colors cursor-pointer">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-xs font-bold text-white">
              US
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-medium text-white">User</span>
              <span className="text-xs text-gray-500">Free Plan</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
