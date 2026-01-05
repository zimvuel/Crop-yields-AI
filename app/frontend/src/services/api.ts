export const fetchCropPrediction = async (prompt: string): Promise<string> => {
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/predict';

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      // FIX 1: Change 'prompt' to 'query' so Python can read it
      body: JSON.stringify({ query: prompt }), 
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    
    // FIX 2: Change 'response' to 'ai_message' (or 'result_text' if you prefer raw stats)
    return data.ai_message; 
    
  } catch (error) {
    console.error("Failed to fetch prediction:", error);
    throw error;
  }
};