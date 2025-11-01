import React, { useState, useRef, useEffect } from 'react';
import { Card, Input, Button, List, Avatar, Space, Collapse, Spin, Empty } from 'antd';
import { SendOutlined, UserOutlined, RobotOutlined } from '@ant-design/icons';
import { queryAPI, QueryResponse } from '../services/api';

const { TextArea } = Input;

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: QueryResponse['sources'];
  retrievedChunks?: number;
  timeConsumed?: number;
  totalTokens?: number;
  promptTokens?: number;
  completionTokens?: number;
  reformulationTokens?: number;
  reformulationPromptTokens?: number;
  reformulationCompletionTokens?: number;
}

interface ChatInterfaceProps {
  selectedDocIds: string[];
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ selectedDocIds }) => {
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

    // Create a temporary message ID for updates
    const retrievalMessageId = (Date.now() + 1).toString();

    try {
      // Show processing message
      const processingMessageId = retrievalMessageId;
      const processingMessage: Message = {
        id: processingMessageId,
        type: 'assistant',
        content: '💭 Processing...',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, processingMessage]);

      // Make the query (with selected document IDs if any)
      const response = await queryAPI.query(
        input,
        true,
        selectedDocIds.length > 0 ? selectedDocIds : undefined
      );

      // Show final answer with metadata
      const answerMessage: Message = {
        id: processingMessageId,
        type: 'assistant',
        content: response.answer,
        timestamp: new Date(),
        sources: response.sources,
        retrievedChunks: response.retrieved_chunks,
        timeConsumed: response.time_consumed,
        totalTokens: response.total_tokens,
        promptTokens: response.prompt_tokens,
        completionTokens: response.completion_tokens,
        reformulationTokens: response.reformulation_tokens,
        reformulationPromptTokens: response.reformulation_prompt_tokens,
        reformulationCompletionTokens: response.reformulation_completion_tokens,
      };
      setMessages((prev) => prev.map(msg => msg.id === processingMessageId ? answerMessage : msg));

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
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span>Intelligent Q&A</span>
          {selectedDocIds.length > 0 ? (
            <span style={{ fontSize: 12, color: '#1890ff' }}>
              ({selectedDocIds.length} doc{selectedDocIds.length > 1 ? 's' : ''})
            </span>
          ) : (
            <span style={{ fontSize: 12, color: '#999' }}>
              (all docs)
            </span>
          )}
        </div>
      }
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
                    {/* Show retrieval info for assistant messages with sources */}
                    {message.type === 'assistant' && message.retrievedChunks !== undefined && message.retrievedChunks > 0 && (
                      <div style={{ fontSize: 11, color: '#999', marginBottom: 8 }}>
                        📚 Retrieved {message.retrievedChunks} chunks
                      </div>
                    )}

                    <div style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                      {message.content}
                    </div>

                    {message.type === 'assistant' && message.sources && message.sources.length > 0 && (
                      <Collapse
                        ghost
                        size="small"
                        style={{ marginTop: 6 }}
                        items={[
                          {
                            key: '1',
                            label: (
                              <span style={{ fontSize: 11, color: '#1890ff', cursor: 'pointer' }}>
                                📄 View Sources ({message.sources.length})
                              </span>
                            ),
                            children: (
                              <div>
                                {message.sources.map((source, idx) => (
                                  <div
                                    key={idx}
                                    style={{
                                      marginBottom: 8,
                                      padding: 8,
                                      backgroundColor: '#fafafa',
                                      borderRadius: 4,
                                      borderLeft: '3px solid #1890ff',
                                    }}
                                  >
                                    <div style={{ marginBottom: 6, fontSize: 11, color: '#999' }}>
                                      #{idx + 1} • Similarity: {(source.similarity_score * 100).toFixed(0)}%
                                    </div>
                                    <div style={{ fontSize: 12, color: '#666', lineHeight: 1.5 }}>
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

                    {message.type === 'assistant' && (message.timeConsumed !== undefined || message.totalTokens !== undefined) && (
                      <div style={{ marginTop: 8, fontSize: 11, color: '#999', display: 'flex', alignItems: 'center', gap: 6 }}>
                        {message.timeConsumed !== undefined && (
                          <span>⏱️ {message.timeConsumed}s</span>
                        )}
                        {message.totalTokens !== undefined && message.totalTokens > 0 && (
                          <>
                            {message.timeConsumed !== undefined && <span>•</span>}
                            <span>🔤 {message.totalTokens} tokens</span>
                          </>
                        )}
                      </div>
                    )}
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
