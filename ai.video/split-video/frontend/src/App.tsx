import React, { useState, useEffect } from 'react';
import { Layout, Typography, Card, Row, Col } from 'antd';
import { VideoCameraOutlined } from '@ant-design/icons';
import VideoUpload from './components/VideoUpload';
import ProcessingProgress from './components/ProcessingProgress';
import VideoTree from './components/VideoTree';
import VideoPreview from './components/VideoPreview';
import { getProcessingStatus, getVideoTree } from './services/api';
import { ProcessingTask, ProcessingStatus, VideoTreeNode } from './types';
import './App.css';

const { Header, Content } = Layout;
const { Title } = Typography;

const App: React.FC = () => {
    const [currentTask, setCurrentTask] = useState<ProcessingTask | null>(null);
    const [videoTree, setVideoTree] = useState<VideoTreeNode | null>(null);
    const [previewNode, setPreviewNode] = useState<VideoTreeNode | null>(null);
    const [previewVisible, setPreviewVisible] = useState(false);
    const [pollingInterval, setPollingInterval] = useState<number | null>(null);

    useEffect(() => {
        return () => {
            if (pollingInterval) {
                clearInterval(pollingInterval);
            }
        };
    }, [pollingInterval]);

    const handleUploadSuccess = (taskId: string, videoId: string) => {
        // Start polling for status
        const interval = setInterval(async () => {
            try {
                const response = await getProcessingStatus(taskId);
                setCurrentTask(response.task);

                // If completed or failed, stop polling and load tree
                if (
                    response.task.status === ProcessingStatus.COMPLETED ||
                    response.task.status === ProcessingStatus.FAILED
                ) {
                    clearInterval(interval);
                    setPollingInterval(null);

                    if (response.task.status === ProcessingStatus.COMPLETED) {
                        loadVideoTree(videoId);
                    }
                }
            } catch (error: any) {
                console.error('Error polling status:', error);

                // If task not found (404), stop polling and clear task
                if (error.response?.status === 404) {
                    clearInterval(interval);
                    setPollingInterval(null);
                    setCurrentTask(null);
                    console.warn('Task not found - server may have been restarted');
                }
            }
        }, 2000); // Poll every 2 seconds

        setPollingInterval(interval);
    };

    const loadVideoTree = async (videoId: string) => {
        try {
            const response = await getVideoTree(videoId);
            setVideoTree(response.tree);
        } catch (error) {
            console.error('Error loading video tree:', error);
        }
    };

    const handleNodeClick = (node: VideoTreeNode) => {
        setPreviewNode(node);
        setPreviewVisible(true);
    };

    const handlePreviewClose = () => {
        setPreviewVisible(false);
        setPreviewNode(null);
    };

    return (
        <Layout style={{ minHeight: '100vh' }}>
            <Header style={{ background: '#1890ff', padding: '0 24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', height: '100%' }}>
                    <VideoCameraOutlined style={{ fontSize: 32, color: 'white', marginRight: 16 }} />
                    <Title level={3} style={{ color: 'white', margin: 0 }}>
                        AI 视频智能分割系统
                    </Title>
                </div>
            </Header>

            <Content style={{ padding: '24px' }}>
                <div style={{ maxWidth: 1200, margin: '0 auto' }}>
                    <Card style={{ marginBottom: 24 }}>
                        <Title level={4}>上传视频</Title>
                        <p style={{ color: '#666', marginBottom: 16 }}>
                            上传视频后,系统将自动提取字幕、智能分析内容并分割成约 10 分钟的章节
                        </p>
                        <VideoUpload onUploadSuccess={handleUploadSuccess} />
                    </Card>

                    <Row gutter={24}>
                        <Col xs={24} lg={12}>
                            <ProcessingProgress task={currentTask} />
                        </Col>
                        <Col xs={24} lg={12}>
                            <VideoTree treeData={videoTree} onNodeClick={handleNodeClick} />
                        </Col>
                    </Row>
                </div>
            </Content>

            <VideoPreview
                node={previewNode}
                visible={previewVisible}
                onClose={handlePreviewClose}
            />
        </Layout>
    );
};

export default App;
