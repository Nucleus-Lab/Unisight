// get the base url from the environment variable
const BACKEND_API_BASE_URL = import.meta.env.VITE_BACKEND_API_BASE_URL;

export const createUser = async (walletAddress) => {
  try {
    const response = await fetch(`${BACKEND_API_BASE_URL}/users/${walletAddress}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    }); 

    if (!response.ok) {
      throw new Error('Failed to create user');
    }

    return await response.json();
  } catch (error) {
    console.error('Error creating user:', error);
    throw error;
  }
};

export const sendMessage = async ({ walletAddress, canvasId = null, text }) => {
  try {
    console.log('Sending request with:', { walletAddress, canvasId, text }); // Debug log
    const response = await fetch(`${BACKEND_API_BASE_URL}/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        wallet_address: walletAddress,
        canvas_id: canvasId,
        text: text
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to send message');
    }

    const data = await response.json();
    console.log('Response data:', data); // Debug log
    return data;
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};

export const getUserCanvases = async (walletAddress) => {
  try {
    const response = await fetch(`${BACKEND_API_BASE_URL}/canvas/user/${walletAddress}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch canvases');
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching canvases:', error);
    throw error;
  }
};

export const getCanvasFirstMessage = async (canvasId) => {
  try {
    const response = await fetch(`${BACKEND_API_BASE_URL}/canvas/${canvasId}/first-message`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch first message');
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching first message:', error);
    throw error;
  }
};

export const getCanvasFirstVisualization = async (canvasId) => {
  try {
    const response = await fetch(`${BACKEND_API_BASE_URL}/canvas/${canvasId}/first-visualization`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch first visualization');
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching first visualization:', error);
    throw error;
  }
}; 