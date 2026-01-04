import { useState } from 'react';
import type { Message } from '../types';
import { fetchCropPrediction } from '../services/api';

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleSendMessage = async (text: string) => {
    // Add User Message
    const userMsg: Message = { text, isUser: true };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      // Get AI Response
      const responseText = await fetchCropPrediction(text);
      const aiMsg: Message = { text: responseText, isUser: false };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMsg: Message = { text: "Maaf, terjadi kesalahan saat menghubungi server kami.", isUser: false };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearMessages = () => {
    setMessages([]);
  };

  return {
    messages,
    isLoading,
    handleSendMessage,
    clearMessages
  };
}
