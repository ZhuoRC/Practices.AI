import React, { useState, useRef, useEffect } from 'react';
import { Button, Space, Slider, Typography, Card } from 'antd';
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  StepForwardOutlined,
  StepBackwardOutlined,
  SoundOutlined,
  MutedOutlined
} from '@ant-design/icons';

const { Text } = Typography;

interface AudioPlayerProps {
  audioUrl: string;
  title?: string;
  autoPlay?: boolean;
  showDownload?: boolean;
}

const AudioPlayer: React.FC<AudioPlayerProps> = ({
  audioUrl,
  title = "Audio",
  autoPlay = false,
  showDownload = true
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1.0);
  const [isMuted, setIsMuted] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);
  
  const audioRef = useRef<HTMLAudioElement>(null);
  const progressBarRef = useRef<any>(null);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const setAudioData = () => {
      setDuration(audio.duration);
      setIsLoaded(true);
    };

    const setAudioTime = () => {
      setCurrentTime(audio.currentTime);
    };

    const handleEnded = () => {
      setIsPlaying(false);
      setCurrentTime(0);
    };

    const handleLoadStart = () => {
      setIsLoaded(false);
    };

    // Add event listeners
    audio.addEventListener('loadeddata', setAudioData);
    audio.addEventListener('timeupdate', setAudioTime);
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('loadstart', handleLoadStart);

    // Auto-play if requested
    if (autoPlay) {
      audio.play().catch(e => console.error('Auto-play failed:', e));
    }

    // Cleanup
    return () => {
      audio.removeEventListener('loadeddata', setAudioData);
      audio.removeEventListener('timeupdate', setAudioTime);
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('loadstart', handleLoadStart);
    };
  }, [audioUrl, autoPlay]);

  const togglePlayPause = () => {
    const audio = audioRef.current;
    if (!audio || !isLoaded) return;

    if (isPlaying) {
      audio.pause();
    } else {
      audio.play().catch(e => console.error('Play failed:', e));
    }
    setIsPlaying(!isPlaying);
  };

  const handleSeek = (value: number) => {
    const audio = audioRef.current;
    if (!audio) return;
    
    const seekTime = (value / 100) * duration;
    audio.currentTime = seekTime;
    setCurrentTime(seekTime);
  };

  const handleVolumeChange = (value: number) => {
    const audio = audioRef.current;
    if (!audio) return;
    
    audio.volume = value;
    setVolume(value);
    setIsMuted(value === 0);
  };

  const toggleMute = () => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isMuted) {
      audio.volume = volume;
      setIsMuted(false);
    } else {
      audio.volume = 0;
      setIsMuted(true);
    }
  };

  const skipForward = () => {
    const audio = audioRef.current;
    if (!audio) return;
    
    audio.currentTime = Math.min(audio.currentTime + 10, duration);
  };

  const skipBackward = () => {
    const audio = audioRef.current;
    if (!audio) return;
    
    audio.currentTime = Math.max(audio.currentTime - 10, 0);
  };

  const formatTime = (time: number) => {
    if (isNaN(time)) return '0:00';
    
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = audioUrl;
    link.download = `${title}.${audioUrl.split('.').pop() || 'mp3'}`;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const progressPercentage = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <Card size="small" className="audio-player">
      <div style={{ textAlign: 'center', marginBottom: '16px' }}>
        <Text strong>{title}</Text>
      </div>
      
      <audio
        ref={audioRef}
        src={audioUrl}
        preload="metadata"
        style={{ display: 'none' }}
      />

      <div style={{ marginBottom: '16px' }}>
        <Slider
          ref={progressBarRef}
          min={0}
          max={100}
          value={progressPercentage}
          onChange={handleSeek}
          tooltip={{
            formatter: (value) => value !== undefined ? formatTime((value / 100) * duration) : '0:00'
          }}
          disabled={!isLoaded}
        />
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between',
          marginTop: '4px',
          fontSize: '12px',
          color: '#666'
        }}>
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', marginBottom: '16px' }}>
        <Button
          icon={<StepBackwardOutlined />}
          onClick={skipBackward}
          disabled={!isLoaded}
          size="small"
        />
        
        <Button
          type="primary"
          icon={isPlaying ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
          onClick={togglePlayPause}
          disabled={!isLoaded}
          size="large"
        />
        
        <Button
          icon={<StepForwardOutlined />}
          onClick={skipForward}
          disabled={!isLoaded}
          size="small"
        />
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1 }}>
          <Button
            icon={isMuted ? <MutedOutlined /> : <SoundOutlined />}
            onClick={toggleMute}
            size="small"
          />
          <Slider
            min={0}
            max={1}
            step={0.05}
            value={isMuted ? 0 : volume}
            onChange={handleVolumeChange}
            style={{ flex: 1, margin: 0 }}
            tooltip={{
              formatter: (value) => `${Math.round((value || 0) * 100)}%`
            }}
          />
        </div>

        {showDownload && (
          <Button
            icon={<SoundOutlined />}
            onClick={handleDownload}
            size="small"
          >
            下载
          </Button>
        )}
      </div>
    </Card>
  );
};

export default AudioPlayer;
