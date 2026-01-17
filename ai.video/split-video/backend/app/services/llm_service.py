from openai import OpenAI
from typing import List, Dict
import json
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM-based subtitle segmentation using Qwen or Ollama"""
    
    def __init__(self, provider: str = "qwen", api_key: str = "", api_base: str = "", model: str = "qwen3-vl-32b-instruct"):
        """
        Initialize LLM service
        
        Args:
            provider: LLM provider ("qwen" or "ollama")
            api_key: API key (for Qwen API)
            api_base: API base URL
            model: Model name
        """
        self.provider = provider
        self.model = model
        
        if provider == "qwen":
            # Qwen API using OpenAI-compatible interface
            self.client = OpenAI(
                api_key=api_key,
                base_url=api_base
            )
            logger.info(f"LLMService initialized with Qwen API: {model}")
        else:
            # Local Ollama
            self.client = OpenAI(
                api_key="ollama",  # Ollama doesn't need real API key
                base_url=api_base
            )
            logger.info(f"LLMService initialized with Ollama: {model}")
    
    def segment_into_chapters(
        self,
        segments: List[Dict],
        target_duration: int = 600,
        min_duration: int = 300,
        max_duration: int = 900
    ) -> List[Dict]:
        """
        Segment subtitles into chapters using LLM
        
        Args:
            segments: List of subtitle segments with start, end, text
            target_duration: Target chapter duration in seconds (default 10 min)
            min_duration: Minimum chapter duration in seconds (default 5 min)
            max_duration: Maximum chapter duration in seconds (default 15 min)
            
        Returns:
            List of chapters with title, start_time, end_time, segments
        """
        logger.info(f"Segmenting {len(segments)} subtitle segments into chapters")
        
        # Prepare subtitle text with timestamps
        subtitle_text = self._format_segments_for_llm(segments)
        
        # Create prompt for LLM
        prompt = self._create_segmentation_prompt(
            subtitle_text,
            target_duration,
            min_duration,
            max_duration
        )
        
        # Call LLM
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert video editor who segments video content into coherent chapters based on subtitle analysis."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
        )
        
        # Parse response
        chapters = self._parse_llm_response(response.choices[0].message.content, segments)
        
        logger.info(f"Created {len(chapters)} chapters")
        return chapters
    
    def _format_segments_for_llm(self, segments: List[Dict]) -> str:
        """Format segments for LLM input"""
        lines = []
        for seg in segments:
            start_min = int(seg['start'] // 60)
            start_sec = int(seg['start'] % 60)
            lines.append(f"[{start_min:02d}:{start_sec:02d}] {seg['text']}")
        return '\n'.join(lines)
    
    def _create_segmentation_prompt(
        self,
        subtitle_text: str,
        target_duration: int,
        min_duration: int,
        max_duration: int
    ) -> str:
        """Create prompt for chapter segmentation"""
        target_min = target_duration // 60
        min_min = min_duration // 60
        max_min = max_duration // 60
        
        return f"""请分析以下视频字幕内容,根据语义将其分割成多个章节。

要求:
1. **核心原则**: 按照内容的主题和语义进行分割,每个章节应该是一个完整的话题或主题
2. 章节分割点必须在语义完整的地方,不能在句子中间截断
3. 当话题发生明显转换时才创建新章节
4. 为每个章节生成一个简洁、描述性的标题(中文,10-20字)
5. 返回JSON格式,包含章节列表

参考信息:
- 建议章节时长范围: {min_min}-{max_min} 分钟
- 理想章节时长: 约 {target_min} 分钟
- 注意: 这只是参考,请优先考虑语义完整性

字幕内容:
{subtitle_text}

请返回以下JSON格式:
{{
  "chapters": [
    {{
      "title": "章节标题",
      "start_timestamp": "MM:SS",
      "end_timestamp": "MM:SS"
    }}
  ]
}}

注意:
- start_timestamp 和 end_timestamp 使用 MM:SS 格式
- 确保所有章节连续,没有遗漏或重叠
- 第一个章节从 00:00 开始
- 最后一个章节到视频结束
"""
    
    def _parse_llm_response(self, response_text: str, segments: List[Dict]) -> List[Dict]:
        """Parse LLM response and create chapter objects"""
        try:
            # Extract JSON from response
            # Sometimes LLM wraps JSON in markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            data = json.loads(response_text)
            chapters = []
            
            for i, chapter_data in enumerate(data['chapters']):
                # Parse timestamps
                start_time = self._parse_timestamp(chapter_data['start_timestamp'])
                end_time = self._parse_timestamp(chapter_data['end_timestamp'])
                
                # Get segments for this chapter
                chapter_segments = [
                    seg for seg in segments
                    if seg['start'] >= start_time and seg['end'] <= end_time
                ]
                
                # Combine segment texts
                subtitle_text = ' '.join(seg['text'] for seg in chapter_segments)
                
                chapters.append({
                    'title': chapter_data['title'],
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': end_time - start_time,
                    'subtitle_text': subtitle_text,
                    'segments': chapter_segments
                })
            
            # Post-process: merge adjacent chapters to meet duration targets
            chapters = self._merge_chapters_by_duration(
                chapters, 
                target_duration, 
                min_duration, 
                max_duration
            )
            
            return chapters
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            logger.error(f"Response text: {response_text}")
            # Fallback: create chapters by duration
            return self._fallback_segmentation(segments)
    
    def _parse_timestamp(self, timestamp: str) -> float:
        """Parse MM:SS timestamp to seconds"""
        parts = timestamp.split(':')
        if len(parts) == 2:
            minutes, seconds = parts
            return int(minutes) * 60 + int(seconds)
        elif len(parts) == 3:
            hours, minutes, seconds = parts
            return int(hours) * 3600 + int(minutes) * 60 + int(seconds)
        return 0.0
    
    def _fallback_segmentation(self, segments: List[Dict], target_duration: int = 600) -> List[Dict]:
        """Fallback segmentation by duration if LLM fails"""
        logger.warning("Using fallback segmentation")
        chapters = []
        current_chapter_segments = []
        chapter_start = 0
        chapter_num = 1
        
        for seg in segments:
            current_chapter_segments.append(seg)
            
            # Check if we've reached target duration
            if seg['end'] - chapter_start >= target_duration:
                subtitle_text = ' '.join(s['text'] for s in current_chapter_segments)
                chapters.append({
                    'title': f"第 {chapter_num} 章",
                    'start_time': chapter_start,
                    'end_time': seg['end'],
                    'duration': seg['end'] - chapter_start,
                    'subtitle_text': subtitle_text,
                    'segments': current_chapter_segments
                })
                
                chapter_start = seg['end']
                current_chapter_segments = []
                chapter_num += 1
        
        # Add remaining segments as last chapter
        if current_chapter_segments:
            subtitle_text = ' '.join(s['text'] for s in current_chapter_segments)
            chapters.append({
                'title': f"第 {chapter_num} 章",
                'start_time': chapter_start,
                'end_time': current_chapter_segments[-1]['end'],
                'duration': current_chapter_segments[-1]['end'] - chapter_start,
                'subtitle_text': subtitle_text,
                'segments': current_chapter_segments
            })
        
        return chapters
    
    def _merge_chapters_by_duration(
        self,
        chapters: List[Dict],
        target_duration: int,
        min_duration: int,
        max_duration: int
    ) -> List[Dict]:
        """
        Merge adjacent chapters to meet duration targets
        
        Strategy: Greedily merge adjacent chapters until they approach target_duration
        while staying within [min_duration, max_duration] bounds
        
        Args:
            chapters: List of semantic chapters from LLM
            target_duration: Target duration in seconds (e.g., 600 = 10 min)
            min_duration: Minimum duration in seconds (e.g., 300 = 5 min)
            max_duration: Maximum duration in seconds (e.g., 900 = 15 min)
            
        Returns:
            List of merged chapters
        """
        if not chapters:
            return chapters
        
        logger.info(f"Merging {len(chapters)} semantic chapters based on duration targets")
        logger.info(f"Target: {target_duration}s, Min: {min_duration}s, Max: {max_duration}s")
        
        merged = []
        current_merged = None
        
        for chapter in chapters:
            if current_merged is None:
                # Start a new merged chapter
                current_merged = chapter.copy()
            else:
                # Check if we should merge with current or start a new one
                current_duration = current_merged['duration']
                new_duration = current_merged['duration'] + chapter['duration']
                
                # Decision logic:
                # 1. If adding this chapter would exceed max_duration, finalize current
                # 2. If current is already >= target_duration, finalize current
                # 3. Otherwise, merge to get closer to target
                
                should_finalize = False
                
                if new_duration > max_duration:
                    # Would exceed max, finalize current
                    should_finalize = True
                    logger.debug(f"Finalizing chapter (would exceed max): {current_duration}s")
                elif current_duration >= target_duration:
                    # Already at or above target, finalize
                    should_finalize = True
                    logger.debug(f"Finalizing chapter (at target): {current_duration}s")
                else:
                    # Check if merging gets us closer to target
                    distance_before = abs(current_duration - target_duration)
                    distance_after = abs(new_duration - target_duration)
                    
                    if distance_after > distance_before and current_duration >= min_duration:
                        # Merging makes us farther from target, and we're already above min
                        should_finalize = True
                        logger.debug(f"Finalizing chapter (optimal point): {current_duration}s")
                    else:
                        # Merge to get closer to target
                        should_finalize = False
                
                if should_finalize:
                    # Finalize current merged chapter
                    merged.append(current_merged)
                    # Start new merged chapter with current chapter
                    current_merged = chapter.copy()
                else:
                    # Merge current chapter into current_merged
                    current_merged['end_time'] = chapter['end_time']
                    current_merged['duration'] = current_merged['end_time'] - current_merged['start_time']
                    current_merged['segments'].extend(chapter['segments'])
                    current_merged['subtitle_text'] += ' ' + chapter['subtitle_text']
                    # Combine titles
                    current_merged['title'] = f"{current_merged['title']} + {chapter['title']}"
                    logger.debug(f"Merged chapter, new duration: {current_merged['duration']}s")
        
        # Add the last merged chapter
        if current_merged is not None:
            merged.append(current_merged)
        
        logger.info(f"After merging: {len(merged)} chapters")
        for i, ch in enumerate(merged):
            logger.info(f"  Chapter {i+1}: {ch['duration']}s ({ch['duration']/60:.1f} min) - {ch['title']}")
        
        return merged

