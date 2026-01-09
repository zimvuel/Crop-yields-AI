export interface Session {
  id: string;
  title: string;
  created_at: string;
}

export interface Message {
  role: string;
  content: string;
}

const API_BASE = import.meta.env.VITE_API_URL;

export const fetchSessions = async (): Promise<Session[]> => {
  const res = await fetch(`${API_BASE}/sessions`);
  if (!res.ok) throw new Error('Failed to load history');
  return res.json();
};

export const createSession = async (title: string = 'New Chat'): Promise<Session> => {
  const res = await fetch(`${API_BASE}/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title })
  });
  if (!res.ok) throw new Error('Failed to create session');
  return res.json();
};

export const fetchMessages = async (sessionId: string): Promise<Message[]> => {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/messages`);
  if (!res.ok) throw new Error('Failed to load messages');
  return res.json();
};

export const deleteSession = async (sessionId: string): Promise<void> => {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete session');
};

export const fetchCropPrediction = async (prompt: string, sessionId?: string): Promise<string> => {
  try {
    const response = await fetch(`${API_BASE}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query: prompt, session_id: sessionId }), 
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data.ai_message; 
    
  } catch (error) {
    console.error("Failed to fetch prediction:", error);
    throw error;
  }
};
