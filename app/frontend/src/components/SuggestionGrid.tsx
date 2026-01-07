import { Sprout, CloudRain, Calendar, TrendingUp } from 'lucide-react';
import type { Suggestion, SuggestionGridProps } from '../types';

export function SuggestionGrid({ onSelect }: SuggestionGridProps) {
  const suggestions: Suggestion[] = [
    {
      icon: <Sprout className="h-6 w-6 text-green-400" />,
      text: "Kapan waktu terbaik untuk menanam jeruk nipis di Bandung?",
      label: "Rekomendasi Tanam"
    },
    {
      icon: <CloudRain className="h-6 w-6 text-blue-400" />,
      text: "Prediksi hasil panen Padi di Surabaya tanggal 20 Januari",
      label: "Prediksi Panen"
    },
    {
      icon: <Calendar className="h-6 w-6 text-orange-400" />,
      text: "Apakah cocok menanam Lengkuas di Jakarta bulan ini?",
      label: "Kecocokan Lahan"
    },
    {
      icon: <TrendingUp className="h-6 w-6 text-purple-400" />,
      text: "Berapa estimasi hasil panen Jagung di Medan?",
      label: "Estimasi Yield"
    }
  ];

  return (
    <div className="grid w-full max-w-3xl grid-cols-1 gap-4 px-4 sm:grid-cols-2">
      {suggestions.map((item, index) => (
        <button
          key={index}
          onClick={() => onSelect(item.text)}
          className="group flex flex-col items-start gap-2 rounded-xl border border-gray-800 bg-gray-800/30 p-4 text-left transition-all hover:bg-gray-800 hover:border-gray-700 hover:shadow-lg hover:-translate-y-0.5"
        >
          <div className="rounded-lg bg-gray-900/50 p-2 group-hover:bg-gray-900 transition-colors">
            {item.icon}
          </div>
          <div className="space-y-1">
            <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              {item.label}
            </span>
            <p className="text-sm font-medium text-gray-200 group-hover:text-white">
              {item.text}
            </p>
          </div>
        </button>
      ))}
    </div>
  );
}
