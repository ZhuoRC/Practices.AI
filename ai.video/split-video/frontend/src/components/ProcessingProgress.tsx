import React from 'react';
import { Card, Progress, Steps, Alert, Space, Typography } from 'antd';
import { LoadingOutlined, CheckCircleOutlined, CloseCircleOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { ProcessingTask, ProcessingStatus } from '../types';

const { Text } = Typography;

interface ProcessingProgressProps {
    task: ProcessingTask | null;
}

const ProcessingProgress: React.FC<ProcessingProgressProps> = ({ task }) => {
    if (!task) {
        return null;
    }

    const getStepStatus = (status: ProcessingStatus) => {
        switch (status) {
            case ProcessingStatus.PENDING:
                return -1;
            case ProcessingStatus.EXTRACTING_SUBTITLES:
                return 0;
            case ProcessingStatus.ANALYZING_CONTENT:
                return 1;
            case ProcessingStatus.SPLITTING_VIDEO:
                return 2;
            case ProcessingStatus.COMPLETED:
                return 3;
            case ProcessingStatus.FAILED:
                return -1;
            default:
                return 0;
        }
    };

    const currentStep = getStepStatus(task.status);

    const steps = [
        {
            title: '提取字幕',
            description: 'Whisper 字幕提取',
            icon: currentStep > 0 ? <CheckCircleOutlined /> : currentStep === 0 ? <LoadingOutlined /> : undefined,
        },
        {
            title: '内容分析',
            description: 'LLM 章节分割',
            icon: currentStep > 1 ? <CheckCircleOutlined /> : currentStep === 1 ? <LoadingOutlined /> : undefined,
        },
        {
            title: '视频分割',
            description: '生成章节视频',
            icon: currentStep > 2 ? <CheckCircleOutlined /> : currentStep === 2 ? <LoadingOutlined /> : undefined,
        },
    ];

    const getProgressColor = () => {
        if (task.status === ProcessingStatus.FAILED) return '#ff4d4f';
        if (task.status === ProcessingStatus.COMPLETED) return '#52c41a';
        return '#1890ff';
    };

    return (
        <Card
            title={
                <Space>
                    <span>处理进度</span>
                    {task.status === ProcessingStatus.COMPLETED && <CheckCircleOutlined style={{ color: '#52c41a' }} />}
                    {task.status === ProcessingStatus.FAILED && <CloseCircleOutlined style={{ color: '#ff4d4f' }} />}
                    {![ProcessingStatus.COMPLETED, ProcessingStatus.FAILED].includes(task.status) && (
                        <LoadingOutlined style={{ color: '#1890ff' }} />
                    )}
                </Space>
            }
            style={{ marginTop: 24 }}
        >
            {task.status === ProcessingStatus.FAILED && (
                <Alert
                    message="处理失败"
                    description={task.error_message || '未知错误'}
                    type="error"
                    showIcon
                    icon={<CloseCircleOutlined />}
                    style={{ marginBottom: 16 }}
                />
            )}

            <Steps current={currentStep} items={steps} style={{ marginBottom: 24 }} />

            <div style={{ marginBottom: 16 }}>
                <div style={{ marginBottom: 8, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Text strong>当前步骤:</Text>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                        {task.status === ProcessingStatus.COMPLETED
                            ? '已完成'
                            : task.status === ProcessingStatus.FAILED
                                ? '失败'
                                : '处理中...'}
                    </Text>
                </div>
                <Text style={{ fontSize: 13, color: '#666' }}>{task.current_step}</Text>

                <Progress
                    percent={Math.round(task.progress)}
                    status={
                        task.status === ProcessingStatus.FAILED
                            ? 'exception'
                            : task.status === ProcessingStatus.COMPLETED
                                ? 'success'
                                : 'active'
                    }
                    strokeColor={getProgressColor()}
                    style={{ marginTop: 12 }}
                />
            </div>

            {task.video_metadata && (
                <div style={{
                    fontSize: 12,
                    color: '#666',
                    background: '#f5f5f5',
                    padding: 12,
                    borderRadius: 4,
                    marginTop: 16
                }}>
                    <div style={{ marginBottom: 4 }}>
                        <ClockCircleOutlined style={{ marginRight: 6 }} />
                        <strong>视频信息</strong>
                    </div>
                    <div style={{ paddingLeft: 20 }}>
                        <div>文件名: {task.video_metadata.filename}</div>
                        <div>时长: {Math.floor(task.video_metadata.duration / 60)} 分 {Math.round(task.video_metadata.duration % 60)} 秒</div>
                        <div>大小: {(task.video_metadata.file_size / 1024 / 1024).toFixed(2)} MB</div>
                    </div>
                </div>
            )}

            {task.status === ProcessingStatus.COMPLETED && task.chapters.length > 0 && (
                <Alert
                    message="处理完成!"
                    description={`成功创建 ${task.chapters.length} 个章节,平均时长 ${Math.round(task.video_metadata!.duration / task.chapters.length / 60)} 分钟`}
                    type="success"
                    showIcon
                    style={{ marginTop: 16 }}
                />
            )}
        </Card>
    );
};

export default ProcessingProgress;
