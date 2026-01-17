import ffmpeg
import os
from pathlib import Path
from typing import List, Dict
import logging
import subprocess

logger = logging.getLogger(__name__)


class VideoService:
    """Service for video processing and splitting"""
    
    def __init__(self, processed_path: Path, temp_path: Path):
        """
        Initialize video service
        
        Args:
            processed_path: Path for processed videos
            temp_path: Path for temporary files
        """
        self.processed_path = processed_path
        self.temp_path = temp_path
        logger.info("VideoService initialized")
    
    def get_video_duration(self, video_path: str) -> float:
        """
        Get video duration in seconds
        
        Args:
            video_path: Path to video file
            
        Returns:
            Duration in seconds
        """
        try:
            probe = ffmpeg.probe(video_path)
            duration = float(probe['format']['duration'])
            return duration
        except Exception as e:
            logger.error(f"Error getting video duration: {e}")
            return 0.0
    
    def get_video_info(self, video_path: str) -> Dict:
        """
        Get video information
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dict with video info
        """
        try:
            probe = ffmpeg.probe(video_path)
            video_info = {
                'duration': float(probe['format']['duration']),
                'size': int(probe['format']['size']),
                'format': probe['format']['format_name'],
                'bit_rate': int(probe['format'].get('bit_rate', 0))
            }
            
            # Get video stream info
            for stream in probe['streams']:
                if stream['codec_type'] == 'video':
                    video_info['width'] = stream['width']
                    video_info['height'] = stream['height']
                    video_info['codec'] = stream['codec_name']
                    break
            
            return video_info
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return {}
    
    def split_video(
        self,
        input_path: str,
        chapters: List[Dict],
        video_id: str
    ) -> List[Dict]:
        """
        Split video into chapters
        
        Args:
            input_path: Path to input video
            chapters: List of chapter dicts with start_time, end_time, title
            video_id: Video ID for naming
            
        Returns:
            List of chapter dicts with added video_path
        """
        logger.info(f"Splitting video into {len(chapters)} chapters")
        
        output_chapters = []
        
        for i, chapter in enumerate(chapters):
            chapter_id = f"{video_id}_chapter_{i+1:02d}"
            output_filename = f"{chapter_id}.mp4"
            output_path = self.processed_path / output_filename
            
            # Split video using ffmpeg
            success = self._split_video_segment(
                input_path,
                str(output_path),
                chapter['start_time'],
                chapter['end_time']
            )
            
            if success:
                chapter_copy = chapter.copy()
                chapter_copy['chapter_id'] = chapter_id
                chapter_copy['video_path'] = str(output_path)
                output_chapters.append(chapter_copy)
            else:
                logger.error(f"Failed to split chapter {i+1}")
        
        logger.info(f"Successfully split {len(output_chapters)} chapters")
        return output_chapters
    
    def _split_video_segment(
        self,
        input_path: str,
        output_path: str,
        start_time: float,
        end_time: float
    ) -> bool:
        """
        Split a video segment using ffmpeg
        
        Args:
            input_path: Input video path
            output_path: Output video path
            start_time: Start time in seconds
            end_time: End time in seconds
            
        Returns:
            True if successful
        """
        try:
            duration = end_time - start_time
            
            # Use ffmpeg to split video
            # -ss: start time, -t: duration, -c copy: copy codec (fast, no re-encoding)
            (
                ffmpeg
                .input(input_path, ss=start_time, t=duration)
                .output(
                    output_path,
                    c='copy',  # Copy codec for speed
                    avoid_negative_ts='make_zero'
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )
            
            logger.info(f"Created video segment: {output_path}")
            return True
            
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error splitting video: {e}")
            return False
    
    def create_subtitle_file(
        self,
        chapter: Dict,
        video_id: str,
        chapter_index: int
    ) -> str:
        """
        Create SRT subtitle file for a chapter
        
        Args:
            chapter: Chapter dict with segments
            video_id: Video ID
            chapter_index: Chapter index
            
        Returns:
            Path to subtitle file
        """
        chapter_id = f"{video_id}_chapter_{chapter_index+1:02d}"
        subtitle_filename = f"{chapter_id}.srt"
        subtitle_path = self.processed_path / subtitle_filename
        
        def format_timestamp(seconds: float) -> str:
            """Format seconds to SRT timestamp"""
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
        
        # Adjust timestamps relative to chapter start
        chapter_start = chapter['start_time']
        
        srt_content = []
        for i, segment in enumerate(chapter.get('segments', []), 1):
            # Adjust timestamps to be relative to chapter start
            start = segment['start'] - chapter_start
            end = segment['end'] - chapter_start
            
            start_ts = format_timestamp(start)
            end_ts = format_timestamp(end)
            text = segment['text'].strip()
            
            srt_content.append(f"{i}")
            srt_content.append(f"{start_ts} --> {end_ts}")
            srt_content.append(text)
            srt_content.append("")
        
        # Write to file
        with open(subtitle_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(srt_content))
        
        logger.info(f"Created subtitle file: {subtitle_path}")
        return str(subtitle_path)
    
    def generate_thumbnail(self, video_path: str, output_path: str, time: float = 1.0) -> bool:
        """
        Generate thumbnail from video
        
        Args:
            video_path: Path to video
            output_path: Path to save thumbnail
            time: Time in seconds to capture thumbnail
            
        Returns:
            True if successful
        """
        try:
            (
                ffmpeg
                .input(video_path, ss=time)
                .filter('scale', 320, -1)
                .output(output_path, vframes=1)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )
            return True
        except Exception as e:
            logger.error(f"Error generating thumbnail: {e}")
            return False
