// 图像编辑参数类型
export interface ImageEditParams {
    prompt: string;
    negative_prompt?: string;
    width?: number;
    height?: number;
    num_inference_steps?: number;
    guidance_scale?: number;
    seed?: number;
}

// 图像编辑响应类型
export interface ImageEditResponse {
    success: boolean;
    message: string;
    image_base64?: string;
}