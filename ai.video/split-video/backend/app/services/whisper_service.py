import whisper
import os
from pathlib import Path
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class WhisperService:
    """Service for extracting subtitles using Whisper"""
    
    def __init__(self, model_name: str = "base"):
        """
        Initialize Whisper service
        
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_name = model_name
        self.model = None
        logger.info(f"WhisperService initialized with model: {model_name}")
    
    def load_model(self):
        """Load Whisper model (lazy loading)"""
        if self.model is None:
            logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
            logger.info("Whisper model loaded successfully")
    
    def extract_subtitles(self, video_path: str) -> Dict:
        """
        Extract subtitles from video with timestamps
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dict containing segments with text and timestamps
        """
        self.load_model()
        
        logger.info(f"Extracting subtitles from: {video_path}")
        
        # Transcribe with word-level timestamps
        result = self.model.transcribe(
            video_path,
            word_timestamps=True,
            verbose=False
        )
        
        logger.info(f"Extracted {len(result['segments'])} segments")
        
        return result
    
    def format_as_srt(self, result: Dict, output_path: str) -> str:
        """
        Format Whisper result as SRT subtitle file
        
        Args:
            result: Whisper transcription result
            output_path: Path to save SRT file
            
        Returns:
            Path to saved SRT file
        """
        def format_timestamp(seconds: float) -> str:
            """Format seconds to SRT timestamp format (HH:MM:SS,mmm)"""
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
        
        srt_content = []
        for i, segment in enumerate(result['segments'], 1):
            start = format_timestamp(segment['start'])
            end = format_timestamp(segment['end'])
            text = segment['text'].strip()
            
            srt_content.append(f"{i}")
            srt_content.append(f"{start} --> {end}")
            srt_content.append(text)
            srt_content.append("")  # Empty line between entries
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(srt_content))
        
        logger.info(f"SRT file saved to: {output_path}")
        return output_path
    
    def get_full_text(self, result: Dict) -> str:
        """
        Get full text from Whisper result
        
        Args:
            result: Whisper transcription result
            
        Returns:
            Full text content
        """
        return result['text']
    
    def get_segments_with_timestamps(self, result: Dict) -> List[Dict]:
        """
        Get segments with timestamps
        
        Args:
            result: Whisper transcription result
            
        Returns:
            List of segments with start, end, and text
        """
        segments = []
        for segment in result['segments']:
            segments.append({
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text'].strip()
            })
        return segments


# Global instance
_whisper_service = None


def get_whisper_service(model_name: str = "base") -> WhisperService:
    """Get or create WhisperService instance"""
    global _whisper_service
    if _whisper_service is None:
        _whisper_service = WhisperService(model_name)
    return _whisper_service
