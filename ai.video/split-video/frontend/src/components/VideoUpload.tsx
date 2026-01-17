import React, { useState } from 'react';
import { Upload, message, Progress } from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';
import { uploadVideo } from '../services/api';

const { Dragger } = Upload;

interface VideoUploadProps {
    onUploadSuccess: (taskId: string, videoId: string) => void;
}

const VideoUpload: React.FC<VideoUploadProps> = ({ onUploadSuccess }) => {
    const [uploading, setUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [uploadSpeed, setUploadSpeed] = useState(0);

    const formatSpeed = (bytesPerSecond: number): string => {
        const mbps = bytesPerSecond / (1024 * 1024);
        return `${mbps.toFixed(2)} MB/s`;
    };

    const props: UploadProps = {
        name: 'file',
        multiple: false,
        accept: 'video/*',
        beforeUpload: async (file) => {
            // Validate file type
            if (!file.type.startsWith('video/')) {
                message.error('请上传视频文件!');
                return Upload.LIST_IGNORE;
            }

            // Validate file size (max 2GB)
            const maxSize = 2 * 1024 * 1024 * 1024; // 2GB
            if (file.size > maxSize) {
                message.error('视频文件不能超过 2GB!');
                return Upload.LIST_IGNORE;
            }

            setUploading(true);
            setUploadProgress(0);
            setUploadSpeed(0);

            try {
                const response = await uploadVideo(file, (progress, speed) => {
                    setUploadProgress(progress);
                    setUploadSpeed(speed);
                });

                message.success('视频上传成功,开始处理...');
                setUploadProgress(100);
                onUploadSuccess(response.task_id, response.video_id);
            } catch (error: any) {
                message.error(`上传失败: ${error.message || '未知错误'}`);
            } finally {
                setTimeout(() => {
                    setUploading(false);
                    setUploadProgress(0);
                    setUploadSpeed(0);
                }, 1000);
            }

            return false; // Prevent default upload behavior
        },
        showUploadList: false,
    };

    return (
        <div>
            <Dragger {...props} disabled={uploading}>
                <p className="ant-upload-drag-icon">
                    <InboxOutlined />
                </p>
                <p className="ant-upload-text">
                    {uploading ? '上传中...' : '点击或拖拽视频文件到此区域上传'}
                </p>
                <p className="ant-upload-hint">
                    支持常见视频格式 (MP4, AVI, MOV, MKV 等),文件大小不超过 2GB
                </p>
            </Dragger>

            {uploading && (
                <div style={{ marginTop: 16 }}>
                    <Progress
                        percent={uploadProgress}
                        status="active"
                        strokeColor={{
                            '0%': '#108ee9',
                            '100%': '#87d068',
                        }}
                    />
                    <div style={{ marginTop: 8, fontSize: 12, color: '#666', textAlign: 'center' }}>
                        上传速度: {formatSpeed(uploadSpeed)}
                    </div>
                </div>
            )}
        </div>
    );
};

export default VideoUpload;
