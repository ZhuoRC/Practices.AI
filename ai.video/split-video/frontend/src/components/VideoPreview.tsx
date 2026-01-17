import React, { useState, useEffect } from 'react';
import { Modal, Tabs, Spin } from 'antd';
import { VideoTreeNode } from '../types';
import { getVideoUrl, getSubtitle } from '../services/api';

interface VideoPreviewProps {
    node: VideoTreeNode | null;
    visible: boolean;
    onClose: () => void;
}

const VideoPreview: React.FC<VideoPreviewProps> = ({ node, visible, onClose }) => {
    const [subtitle, setSubtitle] = useState<string>('');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (visible && node) {
            loadSubtitle();
        }
    }, [visible, node]);

    const loadSubtitle = async () => {
        if (!node) return;

        setLoading(true);
        try {
            const subtitleText = await getSubtitle(node.video_id);
            setSubtitle(subtitleText);
        } catch (error) {
            console.error('Failed to load subtitle:', error);
            setSubtitle('字幕加载失败');
        } finally {
            setLoading(false);
        }
    };

    if (!node) return null;

    const videoUrl = getVideoUrl(node.video_id);

    const items = [
        {
            key: 'video',
            label: '视频预览',
            children: (
                <div style={{ textAlign: 'center' }}>
                    <video
                        controls
                        style={{ width: '100%', maxHeight: '500px' }}
                        src={videoUrl}
                    >
                        您的浏览器不支持视频播放
                    </video>
                </div>
            ),
        },
        {
            key: 'subtitle',
            label: '字幕内容',
            children: loading ? (
                <div style={{ textAlign: 'center', padding: 40 }}>
                    <Spin />
                </div>
            ) : (
                <div
                    style={{
                        maxHeight: '500px',
                        overflow: 'auto',
                        whiteSpace: 'pre-wrap',
                        fontFamily: 'monospace',
                        fontSize: 12,
                        padding: 16,
                        backgroundColor: '#f5f5f5',
                        borderRadius: 4,
                    }}
                >
                    {subtitle}
                </div>
            ),
        },
    ];

    return (
        <Modal
            title={node.title}
            open={visible}
            onCancel={onClose}
            footer={null}
            width={800}
            destroyOnClose
        >
            <Tabs defaultActiveKey="video" items={items} />
        </Modal>
    );
};

export default VideoPreview;
