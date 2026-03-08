import React from 'react';
import { Card, Button, Space, Empty } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';

interface ImageDisplayProps {
    imageUrl: string;
}

const ImageDisplay: React.FC<ImageDisplayProps> = ({ imageUrl }) => {
    const handleDownload = () => {
        const link = document.createElement('a');
        link.href = imageUrl;
        link.download = `edited_image_${Date.now()}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        <Card title="编辑结果" style={{ marginTop: '16px' }}>
            {imageUrl ? (
                <div style={{ textAlign: 'center' }}>
                    <img
                        src={imageUrl}
                        alt="编辑结果"
                        style={{
                            maxWidth: '100%',
                            maxHeight: '600px',
                            objectFit: 'contain',
                            borderRadius: '8px'
                        }}
                    />
                    <div style={{ marginTop: '16px' }}>
                        <Button
                            type="primary"
                            size="large"
                            icon={<DownloadOutlined />}
                            onClick={handleDownload}
                        >
                            下载图片
                        </Button>
                    </div>
                </div>
            ) : (
                <Empty
                    description="暂无编辑结果"
                    style={{ padding: '60px 0' }}
                />
            )}
        </Card>
    );
};

export default ImageDisplay;