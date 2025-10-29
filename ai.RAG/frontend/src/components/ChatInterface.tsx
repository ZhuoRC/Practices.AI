import React, { useState, useRef, useEffect } from 'react';
import { Card, Input, Button, List, Avatar, Space, Collapse, Tag, Spin, Empty } from 'antd';
import { SendOutlined, UserOutlined, RobotOutlined, FileTextOutlined } from '@ant-design/icons';
import { queryAPI, QueryResponse } from '../services/api';

const { TextArea } = Input;
const { Panel } = Collapse;

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: QueryResponse['sources'];
  retrievedChunks?: number;
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await queryAPI.query(input, true);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: response.answer,
        timestamp: new Date(),
        sources: response.sources,
        retrievedChunks: response.retrieved_chunks,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      console.error('Query error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Sorry, an error occurred during the query. Please check if the backend service is running properly.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Card
      title="Intelligent Q&A"
      style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
      bodyStyle={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}
    >
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          marginBottom: 16,
          padding: '16px 0',
        }}
      >
        {messages.length === 0 ? (
          <Empty
            description="Start a conversation! After uploading PDF documents, you can ask me questions about the content."
            style={{ marginTop: 60 }}
          />
        ) : (
          <List
            dataSource={messages}
            renderItem={(message) => (
              <List.Item
                style={{
                  border: 'none',
                  justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start',
                }}
              >
                <Space
                  direction="horizontal"
                  align="start"
                  style={{
                    maxWidth: '80%',
                    flexDirection: message.type === 'user' ? 'row-reverse' : 'row',
                  }}
                >
                  <Avatar
                    icon={message.type === 'user' ? <UserOutlined /> : <RobotOutlined />}
                    style={{
                      backgroundColor: message.type === 'user' ? '#1890ff' : '#52c41a',
                    }}
                  />
                  <div
                    style={{
                      backgroundColor: message.type === 'user' ? '#e6f7ff' : '#f6ffed',
                      padding: '12px 16px',
                      borderRadius: 8,
                      maxWidth: '100%',
                    }}
                  >
                    <div style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                      {message.content}
                    </div>

                    {message.type === 'assistant' && message.sources && message.sources.length > 0 && (
                      <Collapse
                        ghost
                        style={{ marginTop: 12 }}
                        items={[
                          {
                            key: '1',
                            label: (
                              <Space>
                                <FileTextOutlined />
                                <span>
                                  References ({message.retrievedChunks} chunks)
                                </span>
                              </Space>
                            ),
                            children: (
                              <div>
                                {message.sources.map((source, idx) => (
                                  <div
                                    key={idx}
                                    style={{
                                      marginBottom: 8,
                                      padding: 8,
                                      backgroundColor: '#fff',
                                      borderRadius: 4,
                                      border: '1px solid #d9d9d9',
                                    }}
                                  >
                                    <div style={{ marginBottom: 4 }}>
                                      <Tag color="blue">Chunk {idx + 1}</Tag>
                                      <Tag color="green">
                                        Similarity: {(source.similarity_score * 100).toFixed(1)}%
                                      </Tag>
                                    </div>
                                    <div style={{ fontSize: 12, color: '#666' }}>
                                      {source.text}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            ),
                          },
                        ]}
                      />
                    )}

                    <div style={{ fontSize: 12, color: '#999', marginTop: 8 }}>
                      {message.timestamp.toLocaleTimeString('en-US')}
                    </div>
                  </div>
                </Space>
              </List.Item>
            )}
          />
        )}
        <div ref={messagesEndRef} />
      </div>

      <div style={{ borderTop: '1px solid #f0f0f0', paddingTop: 16 }}>
        <Space.Compact style={{ width: '100%' }}>
          <TextArea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter your question... (Shift+Enter for new line, Enter to send)"
            autoSize={{ minRows: 2, maxRows: 4 }}
            disabled={loading}
          />
          <Button
            type="primary"
            icon={loading ? <Spin /> : <SendOutlined />}
            onClick={handleSend}
            disabled={!input.trim() || loading}
            style={{ height: 'auto' }}
          >
            Send
          </Button>
        </Space.Compact>
      </div>
    </Card>
  );
};

export default ChatInterface;
