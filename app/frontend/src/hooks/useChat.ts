import { useState, useEffect } from 'react';
import type { Message } from '../types';
import { fetchCropPrediction, fetchSessions, createSession, fetchMessages, deleteSession, type Session } from '../services/api';

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const [sessions, setSessions] = useState<Session[]>([]);

  // Load History on Mount
  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const list = await fetchSessions();
      setSessions(list);
    } catch (e) {
      console.error(e);
    }
  };

  const loadSession = async (id: string) => {
    setIsLoading(true);
    setSessionId(id);
    try {
      const serverMessages = await fetchMessages(id);
      // Map server messages (role/content) to UI messages (text/isUser)
      const uiMessages = serverMessages.map(m => ({
        text: m.content,
        isUser: m.role === 'user'
      }));
      setMessages(uiMessages);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const startNewSession = async () => {
    setIsLoading(true);
    try {
      const sess = await createSession();
      setSessionId(sess.id);
      setMessages([]);
      await loadSessions();
    } catch(e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteSession = async (id: string) => {
    try {
      await deleteSession(id);
      
      // Update local state
      const updatedSessions = sessions.filter(s => s.id !== id);
      setSessions(updatedSessions);

      // If deleted session was active, reset or switch
      if (sessionId === id) {
        setSessionId(undefined);
        setMessages([]);
        if (updatedSessions.length > 0) {
            // Optional: Automatically switch to the first available session
            // loadSession(updatedSessions[0].id); 
        }
      }
    } catch (e) {
      console.error("Failed to delete session", e);
    }
  };

  const handleSendMessage = async (text: string) => {
    // Ensure session exists
    let currentSessionId = sessionId;
    if (!currentSessionId) {
      const sess = await createSession();
      currentSessionId = sess.id;
      setSessionId(sess.id);
      loadSessions();
    }

    // Add User Message
    const userMsg: Message = { text, isUser: true };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      // Get AI Response
      const responseText = await fetchCropPrediction(text, currentSessionId);
      const aiMsg: Message = { text: responseText, isUser: false };
      setMessages((prev) => [...prev, aiMsg]);
      
      // Refresh sessions to update title if it was "New Chat"
      loadSessions();

    } catch (error: any) {
      console.error("Error sending message:", error);
      const errorText = error.message || "Maaf, terjadi kesalahan saat menghubungi server.";
      const errorMsg: Message = { text: `[ERROR] ${errorText}`, isUser: false };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearMessages = () => {
    setMessages([]);
    setSessionId(undefined);
  };

  return {
    messages,
    isLoading,
    handleSendMessage,
    clearMessages,
    sessions,
    loadSession,
    startNewSession,
    handleDeleteSession,
    currentSessionId: sessionId
  };
}

