import React, { useState } from 'react';
import { Card, Input, Button, Space, Slider, InputNumber, message, Modal, Collapse, Spin } from 'antd';
import { EditOutlined, DownloadOutlined, ReloadOutlined } from '@ant-design/icons';
import { editImage } from '../services/imageEditApi';
import { ImageEditParams } from '../types';
import ImageUpload from './ImageUpload';

const { TextArea } = Input;
const { Panel } = Collapse;

interface ImageEditorProps {
    onImageEdited: (imageUrl: string) => void;
}

const ImageEditor: React.FC<ImageEditorProps> = ({ onImageEdited }) => {
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [imageUrl, setImageUrl] = useState<string>('');
    const [prompt, setPrompt] = useState<string>('');
    const [negativePrompt, setNegativePrompt] = useState<string>('');
    const [numInferenceSteps, setNumInferenceSteps] = useState<number>(50);
    const [guidanceScale, setGuidanceScale] = useState<number>(7.5);
    const [seed, setSeed] = useState<number | undefined>(undefined);
    const [width, setWidth] = useState<number | undefined>(undefined);
    const [height, setHeight] = useState<number | undefined>(undefined);
    const [loading, setLoading] = useState<boolean>(false);

    const handleFileSelect = (file: File) => {
        setSelectedFile(file);
        const reader = new FileReader();
        reader.onload = (e) => {
            setImageUrl(e.target?.result as string);
        };
        reader.readAsDataURL(file);
    };

    const handleEdit = async () => {
        if (!selectedFile) {
            message.warning('请先上传图片！');
            return;
        }

        if (!prompt.trim()) {
            message.warning('请输入编辑提示词！');
            return;
        }

        setLoading(true);

        try {
            const params: ImageEditParams = {
                prompt: prompt.trim(),
                negative_prompt: negativePrompt.trim() || undefined,
                num_inference_steps: numInferenceSteps,
                guidance_scale: guidanceScale,
                seed: seed,
                width: width,
                height: height,
            };

            const resultBlob = await editImage(selectedFile, params);

            // 将 Blob 转换为 URL
            const resultUrl = URL.createObjectURL(resultBlob);
            onImageEdited(resultUrl);

            message.success('图片编辑成功！');
        } catch (error) {
            console.error('编辑失败:', error);
            message.error('图片编辑失败，请稍后重试！');
        } finally {
            setLoading(false);
        }
    };

    const handleReset = () => {
        setSelectedFile(null);
        setImageUrl('');
        setPrompt('');
        setNegativePrompt('');
        setNumInferenceSteps(50);
        setGuidanceScale(7.5);
        setSeed(undefined);
        setWidth(undefined);
        setHeight(undefined);
        message.info('已重置所有设置');
    };

    return (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
            {/* 上传区域 */}
            <Card title="上传图片" style={{ marginTop: '16px' }}>
                <div style={{ height: '400px' }}>
                    <ImageUpload
                        onFileSelect={handleFileSelect}
                        imageUrl={imageUrl}
                    />
                </div>
            </Card>

            {/* 编辑参数 */}
            <Card
                title="编辑参数"
                extra={
                    <Button
                        type="text"
                        icon={<ReloadOutlined />}
                        onClick={handleReset}
                    >
                        重置
                    </Button>
                }
                style={{ marginTop: '16px' }}
            >
                <Space direction="vertical" style={{ width: '100%' }} size="large">
                    {/* 提示词 */}
                    <div>
                        <label style={{ fontWeight: 'bold', display: 'block', marginBottom: '8px' }}>
                            编辑提示词 <span style={{ color: 'red' }}>*</span>
                        </label>
                        <TextArea
                            placeholder="描述您想要的编辑效果，例如：添加一个红色的帽子"
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            rows={4}
                            maxLength={500}
                            showCount
                        />
                    </div>

                    {/* 高级参数 */}
                    <Collapse defaultActiveKey={[]} ghost>
                        <Panel header="高级参数" key="1">
                            <Space direction="vertical" style={{ width: '100%' }} size="middle">
                                {/* 负面提示词 */}
                                <div>
                                    <label style={{ fontWeight: 'bold', display: 'block', marginBottom: '8px' }}>
                                        负面提示词
                                    </label>
                                    <TextArea
                                        placeholder="描述不想要的内容，例如：模糊、低质量"
                                        value={negativePrompt}
                                        onChange={(e) => setNegativePrompt(e.target.value)}
                                        rows={2}
                                        maxLength={200}
                                        showCount
                                    />
                                </div>

                                {/* 推理步数 */}
                                <div>
                                    <label style={{ fontWeight: 'bold', display: 'block', marginBottom: '8px' }}>
                                        推理步数: {numInferenceSteps}
                                    </label>
                                    <Slider
                                        min={10}
                                        max={100}
                                        value={numInferenceSteps}
                                        onChange={setNumInferenceSteps}
                                        marks={{ 10: '10', 50: '50', 100: '100' }}
                                    />
                                    <p style={{ fontSize: '12px', color: '#999' }}>
                                        步数越多质量越好，但速度越慢。推荐值：50
                                    </p>
                                </div>

                                {/* 引导系数 */}
                                <div>
                                    <label style={{ fontWeight: 'bold', display: 'block', marginBottom: '8px' }}>
                                        引导系数: {guidanceScale}
                                    </label>
                                    <Slider
                                        min={1.0}
                                        max={20.0}
                                        step={0.5}
                                        value={guidanceScale}
                                        onChange={setGuidanceScale}
                                        marks={{ 1: '1', 7.5: '7.5', 20: '20' }}
                                    />
                                    <p style={{ fontSize: '12px', color: '#999' }}>
                                        控制模型对提示词的遵循程度。推荐值：7.5
                                    </p>
                                </div>

                                {/* 随机种子 */}
                                <div>
                                    <label style={{ fontWeight: 'bold', display: 'block', marginBottom: '8px' }}>
                                        随机种子（可选）
                                    </label>
                                    <InputNumber
                                        placeholder="留空表示随机"
                                        value={seed}
                                        onChange={(value) => setSeed(value || undefined)}
                                        min={0}
                                        max={2147483647}
                                        style={{ width: '100%' }}
                                    />
                                    <p style={{ fontSize: '12px', color: '#999' }}>
                                        固定种子可以重现相同的结果
                                    </p>
                                </div>

                                {/* 输出尺寸 */}
                                <div>
                                    <label style={{ fontWeight: 'bold', display: 'block', marginBottom: '8px' }}>
                                        输出尺寸（可选，留空则保持原图尺寸）
                                    </label>
                                    <Space>
                                        <InputNumber
                                            placeholder="宽度"
                                            value={width}
                                            onChange={(value) => setWidth(value || undefined)}
                                            min={256}
                                            max={2048}
                                            style={{ width: '120px' }}
                                        />
                                        <span>×</span>
                                        <InputNumber
                                            placeholder="高度"
                                            value={height}
                                            onChange={(value) => setHeight(value || undefined)}
                                            min={256}
                                            max={2048}
                                            style={{ width: '120px' }}
                                        />
                                    </Space>
                                </div>
                            </Space>
                        </Panel>
                    </Collapse>

                    {/* 操作按钮 */}
                    <Button
                        type="primary"
                        size="large"
                        icon={<EditOutlined />}
                        onClick={handleEdit}
                        loading={loading}
                        disabled={!selectedFile || !prompt.trim()}
                        block
                        style={{ height: '50px', fontSize: '16px' }}
                    >
                        {loading ? '编辑中...' : '开始编辑'}
                    </Button>
                </Space>
            </Card>
        </Space>
    );
};

export default ImageEditor;