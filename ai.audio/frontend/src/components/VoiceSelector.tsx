import React from 'react';
import { Select, Spin, Tag, Avatar, Space, Tooltip, Button } from 'antd';
import { PlayCircleOutlined, UserOutlined } from '@ant-design/icons';
import { VoiceInfo } from '../types/tts';

const { Option } = Select;

interface VoiceSelectorProps {
  voices: VoiceInfo[];
  loading: boolean;
  onPreview?: (voiceId: string) => void;
  selectedProvider: string;
  value?: string;
  onChange?: (value: string) => void;
}

const VoiceSelector: React.FC<VoiceSelectorProps> = ({
  voices,
  loading,
  onPreview,
  selectedProvider,
  value,
  onChange
}) => {
  const getGenderIcon = (gender?: string) => {
    switch (gender?.toLowerCase()) {
      case 'male':
        return '👨';
      case 'female':
        return '👩';
      case 'neutral':
        return '🤖';
      default:
        return '🎤';
    }
  };

  const getLanguageFlag = (language: string) => {
    const flags: Record<string, string> = {
      'en-US': '🇺🇸',
      'en-GB': '🇬🇧',
      'zh-CN': '🇨🇳',
      'zh-TW': '🇹🇼',
      'ja-JP': '🇯🇵',
      'ko-KR': '🇰🇷',
      'es-ES': '🇪🇸',
      'fr-FR': '🇫🇷',
      'de-DE': '🇩🇪',
      'it-IT': '🇮🇹',
      'pt-BR': '🇧🇷',
      'ru-RU': '🇷🇺'
    };
    return flags[language] || '🌐';
  };

  const getProviderColor = (provider: string) => {
    const colors: Record<string, string> = {
      'azure': '#0078D4',
      'google': '#4285F4',
      'elevenlabs': '#FF6B35',
      'local': '#52C41A'
    };
    return colors[provider] || '#1890ff';
  };

  const renderVoiceOption = (voice: VoiceInfo) => (
    <Option key={voice.voice_id} value={voice.voice_id}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Avatar 
          size="small" 
          style={{ 
            backgroundColor: getProviderColor(selectedProvider),
            flexShrink: 0
          }}
          icon={<UserOutlined />}
        />
        
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ 
            fontWeight: 500, 
            display: 'flex', 
            alignItems: 'center', 
            gap: '4px',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap'
          }}>
            {getGenderIcon(voice.gender)} {voice.name}
            {voice.is_neural && (
              <Tag color="blue">Neural</Tag>
            )}
          </div>
          
          <div style={{ 
            fontSize: '12px', 
            color: '#666',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap'
          }}>
            {getLanguageFlag(voice.language)} {voice.language}
            {voice.sample_rate && (
              <span style={{ marginLeft: '4px' }}>
                {voice.sample_rate}Hz
              </span>
            )}
          </div>
          
          {voice.description && (
            <div style={{ 
              fontSize: '11px', 
              color: '#999',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              marginTop: '2px'
            }}>
              {voice.description}
            </div>
          )}
        </div>
        
        {onPreview && (
          <Button
            type="text"
            size="small"
            icon={<PlayCircleOutlined />}
            onClick={(e) => {
              e.stopPropagation();
              onPreview(voice.voice_id);
            }}
            style={{ flexShrink: 0 }}
            title="预览语音"
          />
        )}
      </div>
    </Option>
  );

  const renderDropdownRender = (menu: React.ReactElement) => (
    <div style={{ padding: '4px 0' }}>
      {voices.length === 0 && !loading && (
        <div style={{ 
          padding: '16px', 
          textAlign: 'center', 
          color: '#999' 
        }}>
          暂无可用语音
        </div>
      )}
      {loading && (
        <div style={{ 
          padding: '16px', 
          textAlign: 'center' 
        }}>
          <Spin size="small" />
          <span style={{ marginLeft: '8px' }}>加载中...</span>
        </div>
      )}
      {!loading && voices.length > 0 && menu}
    </div>
  );

  const filterOption = (input: string, option: any) => {
    const voice = voices.find(v => v.voice_id === option.value);
    if (!voice) return false;
    
    const searchText = input.toLowerCase();
    const voiceText = `${voice.name} ${voice.language} ${voice.description || ''}`.toLowerCase();
    return voiceText.includes(searchText);
  };

  return (
    <Select
      value={value}
      onChange={onChange}
      loading={loading}
      placeholder={loading ? "加载语音中..." : "选择语音"}
      showSearch
      filterOption={filterOption}
      dropdownRender={renderDropdownRender}
      style={{ width: '100%' }}
      size="large"
    >
      {voices.map(renderVoiceOption)}
    </Select>
  );
};

export default VoiceSelector;
