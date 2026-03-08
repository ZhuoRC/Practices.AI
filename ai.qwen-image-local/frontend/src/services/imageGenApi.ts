import axios from 'axios';

const API_BASE_URL = 'http://localhost:8501';

export interface ImageGenRequest {
    prompt: string;
    negative_prompt?: string;
    width?: number;
    height?: number;
    num_inference_steps?: number;
    guidance_scale?: number;
    seed?: number;
    enhance_prompt?: boolean;
    return_base64?: boolean;
}

export interface ImageGenResponse {
    success: boolean;
    message: string;
    image_base64?: string;
}

export const imageGenApi = {
    // Generate image from text
    generateImage: async (request: ImageGenRequest, onProgress?: (progress: number) => void) => {
        try {
            const response = await axios.post<Blob>(`${API_BASE_URL}/generate`, request, {
                responseType: 'blob',
                onUploadProgress: (progressEvent) => {
                    if (progressEvent.total && onProgress) {
                        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                        onProgress(progress);
                    }
                },
            });

            return response.data;
        } catch (error: any) {
            console.error('Error generating image:', error);
            throw new Error(error.response?.data?.detail || error.message || 'Failed to generate image');
        }
    },

    // Check health
    checkHealth: async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/health`);
            return response.data;
        } catch (error) {
            console.error('Error checking health:', error);
            throw error;
        }
    },
};