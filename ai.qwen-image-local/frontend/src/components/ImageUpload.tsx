import React from 'react';
import { Upload, message } from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';

interface ImageUploadProps {
    onFileSelect: (file: File) => void;
    imageUrl?: string;
}

const ImageUpload: React.FC<ImageUploadProps> = ({ onFileSelect, imageUrl }) => {
    const beforeUpload = (file: File) => {
        const isImage = file.type.startsWith('image/');
        if (!isImage) {
            message.error('只能上传图片文件！');
            return false;
        }

        const isLt10M = file.size / 1024 / 1024 < 10;
        if (!isLt10M) {
            message.error('图片大小不能超过 10MB！');
            return false;
        }

        onFileSelect(file);
        return false; // 阻止自动上传
    };

    const uploadProps: UploadProps = {
        name: 'file',
        multiple: false,
        accept: 'image/*',
        beforeUpload,
        showUploadList: false,
    };

    return (
        <div style={{
            width: '100%',
            height: '100%',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            border: '1px dashed #d9d9d9',
            borderRadius: '8px',
            backgroundColor: '#fafafa'
        }}>
            {imageUrl ? (
                <img
                    src={imageUrl}
                    alt="上传的图片"
                    style={{
                        maxWidth: '100%',
                        maxHeight: '100%',
                        objectFit: 'contain'
                    }}
                />
            ) : (
                <Upload {...uploadProps} style={{ width: '100%' }}>
                    <div style={{ textAlign: 'center', padding: '40px' }}>
                        <InboxOutlined style={{ fontSize: '64px', color: '#1890ff' }} />
                        <p style={{ marginTop: '16px', fontSize: '16px', color: '#666' }}>
                            点击或拖拽图片到此处上传
                        </p>
                        <p style={{ fontSize: '12px', color: '#999' }}>
                            支持 JPG、PNG 等格式，最大 10MB
                        </p>
                    </div>
                </Upload>
            )}
        </div>
    );
};

export default ImageUpload;