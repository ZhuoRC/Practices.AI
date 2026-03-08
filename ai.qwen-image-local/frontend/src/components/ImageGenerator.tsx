import React, { useState } from 'react';
import { Button, Input, InputNumber, Slider, Switch, Card, message, Spin, Collapse } from 'antd';
import { PictureOutlined, DownloadOutlined, SettingOutlined, ClearOutlined } from '@ant-design/icons';
import { imageGenApi, ImageGenRequest } from '../services/imageGenApi';

const { TextArea } = Input;
const { Panel } = Collapse;

const ImageGenerator: React.FC = () => {
    const [prompt, setPrompt] = useState('');
    const [negativePrompt, setNegativePrompt] = useState('');
    const [width, setWidth] = useState(768);
    const [height, setHeight] = useState(768);
    const [numInferenceSteps, setNumInferenceSteps] = useState(30);
    const [guidanceScale, setGuidanceScale] = useState(4.0);
    const [seed, setSeed] = useState<number | undefined>(undefined);
    const [enhancePrompt, setEnhancePrompt] = useState(true);
    const [generatedImage, setGeneratedImage] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const handleGenerate = async () => {
        if (!prompt.trim()) {
            message.warning('Please enter a prompt');
            return;
        }

        setLoading(true);
        setGeneratedImage(null);

        try {
            const request: ImageGenRequest = {
                prompt: prompt.trim(),
                negative_prompt: negativePrompt.trim() || ' ',
                width,
                height,
                num_inference_steps: numInferenceSteps,
                guidance_scale: guidanceScale,
                seed,
                enhance_prompt: enhancePrompt,
                return_base64: false,
            };

            const blob = await imageGenApi.generateImage(request);
            const imageUrl = URL.createObjectURL(blob);
            setGeneratedImage(imageUrl);
            message.success('Image generated successfully!');
        } catch (error: any) {
            message.error(error.message || 'Failed to generate image');
            console.error('Error generating image:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleDownload = () => {
        if (!generatedImage) return;

        const link = document.createElement('a');
        link.href = generatedImage;
        link.download = `generated_image_${Date.now()}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        message.success('Image downloaded!');
    };

    const handleClear = () => {
        setPrompt('');
        setNegativePrompt('');
        setGeneratedImage(null);
    };

    const randomSeed = () => {
        setSeed(Math.floor(Math.random() * 1000000));
    };

    return (
        <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
            <Card
                title={
                    <span>
                        <PictureOutlined style={{ marginRight: 8 }} />
                        Text to Image Generation
                    </span>
                }
                style={{ marginBottom: 24 }}
                extra={
                    <span style={{ color: '#52c41a', fontSize: '14px' }}>
                        ✨ Using Z-Image model (lighter and faster)
                    </span>
                }
            >
                <div style={{ marginBottom: 24 }}>
                    <label style={{ display: 'block', marginBottom: 8, fontWeight: 600 }}>
                        Prompt (描述您想要的图像) *
                    </label>
                    <TextArea
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        placeholder="例如：一只可爱的橘猫在花园里玩耍，阳光明媚，背景有花朵..."
                        rows={4}
                        maxLength={500}
                        showCount
                    />
                </div>

                <Collapse
                    bordered={false}
                    expandIconPosition="end"
                    style={{ marginBottom: 24 }}
                >
                    <Panel header={<span><SettingOutlined /> Advanced Parameters</span>} key="1">
                        <div style={{ padding: '0 8px' }}>
                            <div style={{ marginBottom: 16 }}>
                                <label style={{ display: 'block', marginBottom: 8, fontWeight: 600 }}>
                                    Negative Prompt (负面提示词)
                                </label>
                                <TextArea
                                    value={negativePrompt}
                                    onChange={(e) => setNegativePrompt(e.target.value)}
                                    placeholder="例如：模糊，低质量，扭曲..."
                                    rows={2}
                                    maxLength={300}
                                />
                            </div>

                            <div style={{ marginBottom: 16, display: 'flex', gap: '16px' }}>
                                <div style={{ flex: 1 }}>
                                    <label style={{ display: 'block', marginBottom: 8, fontWeight: 600 }}>
                                        Width: {width}px
                                    </label>
                                    <Slider
                                        min={256}
                                        max={2048}
                                        step={64}
                                        value={width}
                                        onChange={setWidth}
                                    />
                                </div>
                                <div style={{ flex: 1 }}>
                                    <label style={{ display: 'block', marginBottom: 8, fontWeight: 600 }}>
                                        Height: {height}px
                                    </label>
                                    <Slider
                                        min={256}
                                        max={2048}
                                        step={64}
                                        value={height}
                                        onChange={setHeight}
                                    />
                                </div>
                            </div>

                            <div style={{ marginBottom: 16 }}>
                                <label style={{ display: 'block', marginBottom: 8, fontWeight: 600 }}>
                                    Inference Steps: {numInferenceSteps}
                                </label>
                                <Slider
                                    min={10}
                                    max={100}
                                    step={1}
                                    value={numInferenceSteps}
                                    onChange={setNumInferenceSteps}
                                    tooltip={{ formatter: (value) => `${value} steps` }}
                                />
                            </div>

                            <div style={{ marginBottom: 16 }}>
                                <label style={{ display: 'block', marginBottom: 8, fontWeight: 600 }}>
                                    Guidance Scale: {guidanceScale}
                                </label>
                                <Slider
                                    min={1.0}
                                    max={20.0}
                                    step={0.5}
                                    value={guidanceScale}
                                    onChange={setGuidanceScale}
                                    tooltip={{ formatter: (value) => `${value}` }}
                                />
                            </div>

                            <div style={{ marginBottom: 16, display: 'flex', gap: '16px', alignItems: 'center' }}>
                                <div style={{ flex: 1 }}>
                                    <label style={{ display: 'block', marginBottom: 8, fontWeight: 600 }}>
                                        Seed (Optional)
                                    </label>
                                    <InputNumber
                                        style={{ width: '100%' }}
                                        value={seed}
                                        onChange={(value) => setSeed(value || undefined)}
                                        placeholder="Random"
                                        min={0}
                                        max={999999999}
                                    />
                                </div>
                                <Button onClick={randomSeed} style={{ marginTop: '24px' }}>
                                    <ClearOutlined /> Random
                                </Button>
                            </div>

                            <div>
                                <Switch
                                    checked={enhancePrompt}
                                    onChange={setEnhancePrompt}
                                    checkedChildren="On"
                                    unCheckedChildren="Off"
                                    style={{ marginRight: 8 }}
                                />
                                <label style={{ fontWeight: 600 }}>Enhance Prompt</label>
                                <div style={{ fontSize: '12px', color: '#888', marginTop: 4 }}>
                                    Automatically enhance the prompt for better results
                                </div>
                            </div>
                        </div>
                    </Panel>
                </Collapse>

                <div style={{ marginBottom: 24, display: 'flex', gap: '12px' }}>
                    <Button
                        type="primary"
                        icon={<PictureOutlined />}
                        onClick={handleGenerate}
                        loading={loading}
                        size="large"
                        disabled={!prompt.trim()}
                    >
                        Generate Image
                    </Button>
                    <Button
                        onClick={handleClear}
                        size="large"
                        icon={<ClearOutlined />}
                    >
                        Clear
                    </Button>
                </div>
            </Card>

            {loading && (
                <Card style={{ textAlign: 'center', padding: '48px' }}>
                    <Spin size="large" tip="Generating image, please wait..." />
                </Card>
            )}

            {generatedImage && !loading && (
                <Card
                    title="Generated Image"
                    extra={
                        <Button
                            type="primary"
                            icon={<DownloadOutlined />}
                            onClick={handleDownload}
                        >
                            Download
                        </Button>
                    }
                    style={{ textAlign: 'center' }}
                >
                    <img
                        src={generatedImage}
                        alt="Generated"
                        style={{
                            maxWidth: '100%',
                            maxHeight: '800px',
                            borderRadius: '8px',
                            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                        }}
                    />
                </Card>
            )}
        </div>
    );
};

export default ImageGenerator;