import React, { useState } from 'react';
import { Layout, Typography, Tabs, Card } from 'antd';
import { PictureOutlined, EditOutlined, ThunderboltOutlined } from '@ant-design/icons';
import ImageEditor from './components/ImageEditor';
import ImageDisplay from './components/ImageDisplay';
import ImageGenerator from './components/ImageGenerator';
import './App.css';

const { Header, Content, Footer } = Layout;
const { Title, Text } = Typography;
const { TabPane } = Tabs;

const App: React.FC = () => {
    const [editedImageUrl, setEditedImageUrl] = useState<string>('');
    const [activeTab, setActiveTab] = useState('edit');

    const handleImageEdited = (imageUrl: string) => {
        setEditedImageUrl(imageUrl);
        // 滚动到结果区域
        setTimeout(() => {
            const element = document.getElementById('result-section');
            if (element) {
                element.scrollIntoView({ behavior: 'smooth' });
            }
        }, 100);
    };

    return (
        <Layout style={{ minHeight: '100vh' }}>
            <Header style={{
                background: '#001529',
                padding: '0 50px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <PictureOutlined style={{ fontSize: '32px', color: '#1890ff' }} />
                    <Title
                        level={2}
                        style={{
                            margin: 0,
                            color: '#fff',
                            fontSize: '24px',
                            fontWeight: 600
                        }}
                    >
                        Qwen Image Studio
                    </Title>
                </div>
            </Header>

            <Content style={{ padding: '50px 50px', maxWidth: '1600px', margin: '0 auto', width: '100%' }}>
                <Tabs
                    activeKey={activeTab}
                    onChange={setActiveTab}
                    size="large"
                    centered
                    style={{ marginBottom: 24 }}
                >
                    <TabPane
                        tab={
                            <span>
                                <EditOutlined /> Image Editing
                            </span>
                        }
                        key="edit"
                    >
                        <Card>
                            <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
                                <div style={{ flex: '1', minWidth: '300px', maxWidth: '700px' }}>
                                    <ImageEditor onImageEdited={handleImageEdited} />
                                </div>
                                <div style={{ flex: '1', minWidth: '300px', maxWidth: '700px' }} id="result-section">
                                    <ImageDisplay imageUrl={editedImageUrl} />
                                </div>
                            </div>
                        </Card>
                    </TabPane>

                    <TabPane
                        tab={
                            <span>
                                <ThunderboltOutlined /> Text to Image
                            </span>
                        }
                        key="generate"
                    >
                        <ImageGenerator />
                    </TabPane>
                </Tabs>
            </Content>

            <Footer style={{ textAlign: 'center', background: '#f0f2f5' }}>
                <Text type="secondary">
                    Qwen Image Studio ©2024 - Powered by Qwen-VL Model
                </Text>
            </Footer>
        </Layout>
    );
};

export default App;
