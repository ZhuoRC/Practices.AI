import React, { useState } from 'react';
import { Card, Tree, Empty } from 'antd';
import { FileOutlined, FolderOpenOutlined, PlayCircleOutlined } from '@ant-design/icons';
import type { DataNode } from 'antd/es/tree';
import { VideoTreeNode } from '../types';

interface VideoTreeProps {
    treeData: VideoTreeNode | null;
    onNodeClick: (node: VideoTreeNode) => void;
}

const VideoTree: React.FC<VideoTreeProps> = ({ treeData, onNodeClick }) => {
    const [expandedKeys, setExpandedKeys] = useState<React.Key[]>([]);

    if (!treeData) {
        return (
            <Card title="视频结构">
                <Empty description="暂无数据" />
            </Card>
        );
    }

    const formatDuration = (seconds: number): string => {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    const convertToTreeData = (node: VideoTreeNode): DataNode => {
        const title = (
            <span onClick={() => onNodeClick(node)} style={{ cursor: 'pointer' }}>
                <PlayCircleOutlined style={{ marginRight: 8, color: '#1890ff' }} />
                <strong>{node.title}</strong>
                <span style={{ marginLeft: 8, color: '#666', fontSize: 12 }}>
                    ({formatDuration(node.duration)})
                </span>
            </span>
        );

        return {
            key: node.video_id,
            title,
            icon: node.is_parent ? <FolderOpenOutlined /> : <FileOutlined />,
            children: node.children.map(convertToTreeData),
        };
    };

    const treeDataNodes = [convertToTreeData(treeData)];

    // Auto-expand root node
    if (expandedKeys.length === 0 && treeData) {
        setExpandedKeys([treeData.video_id]);
    }

    return (
        <Card title="视频结构" style={{ marginTop: 24 }}>
            <Tree
                showIcon
                defaultExpandAll
                expandedKeys={expandedKeys}
                onExpand={(keys) => setExpandedKeys(keys)}
                treeData={treeDataNodes}
                style={{ fontSize: 14 }}
            />
        </Card>
    );
};

export default VideoTree;
