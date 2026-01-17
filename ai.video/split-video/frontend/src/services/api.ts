import axios from 'axios';
import { UploadResponse, StatusResponse, TreeResponse } from '../types';

const api = axios.create({
    baseURL: '/api',
    timeout: 300000, // 5 minutes for large uploads
});

export const uploadVideo = async (
    file: File,
    onProgress?: (progress: number, speed: number) => void
): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    let startTime = Date.now();
    let loadedPrevious = 0;

    const response = await api.post<UploadResponse>('/video/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
            if (progressEvent.total && onProgress) {
                const progress = Math.round((progressEvent.loaded / progressEvent.total) * 100);

                // Calculate upload speed (bytes per second)
                const currentTime = Date.now();
                const timeElapsed = (currentTime - startTime) / 1000; // seconds
                const bytesUploaded = progressEvent.loaded - loadedPrevious;
                const speed = timeElapsed > 0 ? bytesUploaded / timeElapsed : 0;

                loadedPrevious = progressEvent.loaded;
                startTime = currentTime;

                onProgress(progress, speed);
            }
        },
    });

    return response.data;
};

export const getProcessingStatus = async (taskId: string): Promise<StatusResponse> => {
    const response = await api.get<StatusResponse>(`/video/status/${taskId}`);
    return response.data;
};

export const getVideoTree = async (videoId: string): Promise<TreeResponse> => {
    const response = await api.get<TreeResponse>(`/video/tree/${videoId}`);
    return response.data;
};

export const getVideoUrl = (videoId: string): string => {
    return `/api/video/preview/${videoId}`;
};

export const getSubtitle = async (videoId: string): Promise<string> => {
    const response = await api.get<{ subtitle: string }>(`/video/subtitle/${videoId}`);
    return response.data.subtitle;
};

export default api;
