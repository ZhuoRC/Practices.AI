import axios from 'axios';
import { ImageEditParams } from '../types';

const API_BASE_URL = '/api';

// 图像编辑 API
export const editImage = async (
    file: File,
    params: ImageEditParams
): Promise<Blob> => {
    const formData = new FormData();

    // 添加图片文件
    formData.append('image', file);

    // 添加编辑参数
    formData.append('prompt', params.prompt);

    if (params.negative_prompt) {
        formData.append('negative_prompt', params.negative_prompt);
    }

    if (params.width) {
        formData.append('width', params.width.toString());
    }

    if (params.height) {
        formData.append('height', params.height.toString());
    }

    if (params.num_inference_steps) {
        formData.append('num_inference_steps', params.num_inference_steps.toString());
    }

    if (params.guidance_scale) {
        formData.append('guidance_scale', params.guidance_scale.toString());
    }

    if (params.seed) {
        formData.append('seed', params.seed.toString());
    }

    formData.append('return_base64', 'false');

    try {
        const response = await axios.post<Blob>('/edit', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
            responseType: 'blob',
        });

        return response.data;
    } catch (error) {
        console.error('图像编辑失败:', error);
        throw error;
    }
};

// 健康检查 API
export const healthCheck = async () => {
    try {
        const response = await axios.get('/health');
        return response.data;
    } catch (error) {
        console.error('健康检查失败:', error);
        throw error;
    }
};