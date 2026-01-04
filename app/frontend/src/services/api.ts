export const fetchCropPrediction = async (prompt: string): Promise<string> => {
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/predict';

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt }),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data.response;
  } catch (error) {
    console.error("Failed to fetch prediction:", error);
    throw error;
  }
};
