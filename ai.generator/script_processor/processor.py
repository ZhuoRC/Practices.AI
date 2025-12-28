"""
脚本处理核心逻辑
"""
import re
import time
import uuid
from typing import List, Optional, Dict, Any
from openai import OpenAI
from anthropic import Anthropic
import jieba
import jieba.analyse

from shared.config import get_settings
from .models import (
    ScriptSegment,
    ScriptProcessRequest,
    ScriptProcessResponse,
    RewriteRequest,
    SegmentationRequest,
    KeywordExtractionRequest,
    EmotionDetectionRequest
)

settings = get_settings()


class ScriptProcessor:
    """脚本处理器"""
    
    def __init__(self):
        """初始化处理器"""
        self.openai_client = None
        self.anthropic_client = None
        
        # 初始化AI客户端
        if settings.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        if settings.ANTHROPIC_API_KEY:
            self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        
        # 初始化分词器
        jieba.setLogLevel(jieba.logging.INFO)
    
    async def process_script(self, request: ScriptProcessRequest) -> ScriptProcessResponse:
        """
        处理完整脚本
        """
        start_time = time.time()
        
        # 初始化结果
        text = request.script_text
        segments: List[ScriptSegment] = []
        
        try:
            # 步骤1: 文本改写（如果启用）
            if request.enable_rewrite:
                text = await self.rewrite_text(RewriteRequest(
                    text=text,
                    style=request.voice_style
                ))
            
            # 步骤2: 文本分段（如果启用）
            if request.enable_segmentation:
                raw_segments = await self.segment_text(SegmentationRequest(
                    text=text,
                    max_length=request.segment_length,
                    preserve_sentences=True
                ))
            else:
                raw_segments = [text]
            
            # 步骤3: 处理每个段落
            for idx, seg_text in enumerate(raw_segments):
                # 提取关键词（如果启用）
                keywords = []
                if request.enable_keyword_extraction:
                    keywords = await self.extract_keywords(KeywordExtractionRequest(
                        text=seg_text,
                        max_keywords=5,
                        language=request.language
                    ))
                
                # 检测情感
                emotion = await self.detect_emotion(EmotionDetectionRequest(
                    text=seg_text,
                    language=request.language
                ))
                
                # 估算时长
                estimated_duration = self.estimate_duration(seg_text, request.language)
                
                # 创建段落对象
                segment = ScriptSegment(
                    index=idx + 1,
                    original_text=seg_text,
                    rewritten_text=seg_text if not request.enable_rewrite else seg_text,
                    estimated_duration=estimated_duration,
                    keywords=keywords,
                    emotion=emotion
                )
                segments.append(segment)
            
            # 计算总时长
            total_duration = sum(seg.estimated_duration or 0 for seg in segments)
            
            # 计算处理时间
            processing_time = time.time() - start_time
            
            return ScriptProcessResponse(
                project_id=request.project_id,
                status="success",
                segments=segments,
                total_duration=total_duration,
                processing_time=processing_time,
                metadata={
                    "segment_count": len(segments),
                    "original_length": len(request.script_text),
                    "processed_length": len(text),
                    "language": request.language
                }
            )
            
        except Exception as e:
            return ScriptProcessResponse(
                project_id=request.project_id,
                status="error",
                segments=[],
                total_duration=0.0,
                processing_time=time.time() - start_time,
                metadata={"error": str(e)}
            )
    
    async def rewrite_text(self, request: RewriteRequest) -> str:
        """
        使用AI改写文本
        """
        try:
            # 优先使用OpenAI
            if self.openai_client:
                prompt = self._build_rewrite_prompt(request.text, request.style, request.target_length)
                
                response = self.openai_client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "你是一个专业的文本改写专家。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                
                return response.choices[0].message.content.strip()
            
            # 备用使用Anthropic
            elif self.anthropic_client:
                prompt = self._build_rewrite_prompt(request.text, request.style, request.target_length)
                
                response = self.anthropic_client.messages.create(
                    model=settings.ANTHROPIC_MODEL,
                    max_tokens=2000,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                return response.content[0].text.strip()
            
            else:
                # 没有AI服务，返回原文本
                return request.text
                
        except Exception as e:
            print(f"文本改写失败: {e}")
            return request.text
    
    async def segment_text(self, request: SegmentationRequest) -> List[str]:
        """
        智能分段文本
        """
        text = request.text
        
        # 标准化文本
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        segments = []
        current_segment = ""
        
        # 按句子分割
        sentences = re.split(r'([。！？!?])', text)
        
        # 重组句子（包含标点）
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                sentence = sentences[i] + sentences[i + 1]
            else:
                sentence = sentences[i]
            
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # 检查是否需要开始新段落
            if len(current_segment) + len(sentence) > request.max_length and current_segment:
                segments.append(current_segment.strip())
                current_segment = sentence
            else:
                current_segment += " " + sentence if current_segment else sentence
        
        # 添加最后一段
        if current_segment:
            segments.append(current_segment.strip())
        
        # 如果没有分段，将整段文本作为一段
        if not segments and text:
            segments = [text]
        
        # 确保最小长度
        final_segments = []
        for seg in segments:
            if len(seg) < request.min_length:
                # 合并到前一段
                if final_segments:
                    final_segments[-1] += " " + seg
                else:
                    final_segments.append(seg)
            else:
                final_segments.append(seg)
        
        return final_segments
    
    async def extract_keywords(self, request: KeywordExtractionRequest) -> List[str]:
        """
        提取关键词
        """
        try:
            # 使用jieba提取关键词
            if request.language == "zh":
                keywords = jieba.analyse.extract_tags(
                    request.text,
                    topK=request.max_keywords,
                    withWeight=False
                )
                return keywords
            else:
                # 英文或其他语言：简单的词频统计
                words = re.findall(r'\b\w+\b', request.text.lower())
                # 过滤停用词（简化版）
                stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                            'should', 'may', 'might', 'must', 'shall', 'can', 'to', 'of', 'in',
                            'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through',
                            'during', 'before', 'after', 'above', 'below', 'between', 'under',
                            'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where',
                            'why', 'how', 'all', 'each', 'few', 'more', 'most', 'other', 'some',
                            'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
                            'very', 'just', 'and', 'but', 'if', 'or', 'because', 'until', 'while',
                            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we',
                            'they', 'what', 'which', 'who', 'whom'}
                
                word_freq = {}
                for word in words:
                    if len(word) > 2 and word not in stop_words:
                        word_freq[word] = word_freq.get(word, 0) + 1
                
                # 返回频率最高的词
                sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
                return [word for word, freq in sorted_words[:request.max_keywords]]
                
        except Exception as e:
            print(f"关键词提取失败: {e}")
            return []
    
    async def detect_emotion(self, request: EmotionDetectionRequest) -> str:
        """
        检测文本情感
        """
        try:
            # 简单的情感检测（基于关键词）
            emotion_keywords = {
                'happy': ['开心', '快乐', '高兴', '幸福', '喜悦', '满意', 'excited', 'happy', 'joy'],
                'sad': ['难过', '悲伤', '痛苦', '失望', '沮丧', 'sad', 'sorrow', 'depressed'],
                'angry': ['生气', '愤怒', '恼火', '气愤', 'angry', 'furious', 'mad'],
                'fear': ['害怕', '恐惧', '担心', '焦虑', 'fear', 'scared', 'anxious'],
                'surprise': ['惊讶', '意外', '震惊', 'surprise', 'shocked', 'amazed'],
                'neutral': ['中性', '平静', 'normal', 'calm', 'neutral']
            }
            
            text = request.text.lower()
            emotion_scores = {}
            
            for emotion, keywords in emotion_keywords.items():
                score = 0
                for keyword in keywords:
                    if keyword.lower() in text:
                        score += 1
                emotion_scores[emotion] = score
            
            # 返回得分最高的情感
            if emotion_scores:
                max_emotion = max(emotion_scores.items(), key=lambda x: x[1])
                if max_emotion[1] > 0:
                    return max_emotion[0]
            
            return 'neutral'
            
        except Exception as e:
            print(f"情感检测失败: {e}")
            return 'neutral'
    
    def estimate_duration(self, text: str, language: str = "zh") -> float:
        """
        估算文本的语音时长（秒）
        """
        if not text:
            return 0.0
        
        # 计算字符数
        char_count = len(text)
        
        # 不同语言的语速（字符/秒）
        speed_rates = {
            'zh': 4.0,    # 中文约4字/秒
            'en': 3.5,    # 英文约3.5词/秒
            'ja': 4.5,    # 日文约4.5字/秒
            'ko': 4.2,    # 韩文约4.2字/秒
        }
        
        speed = speed_rates.get(language, 4.0)
        
        # 估算时长
        duration = char_count / speed
        
        # 添加标点符号停顿时间
        punctuation_count = len(re.findall(r'[。，！？!?]', text))
        duration += punctuation_count * 0.5
        
        return round(duration, 2)
    
    def _build_rewrite_prompt(self, text: str, style: str, target_length: Optional[int]) -> str:
        """
        构建文本改写提示词
        """
        style_descriptions = {
            'professional': '专业、正式、适合商务场合',
            'casual': '轻松、自然、适合日常交流',
            'energetic': '充满活力、积极向上',
            'serious': '严肃、稳重、适合正式内容',
            'friendly': '友好、亲切、温暖',
            'neutral': '中性、客观、平衡'
        }
        
        desc = style_descriptions.get(style, '保持原意和风格')
        
        prompt = f"请改写以下文本，使其{desc}。"
        
        if target_length:
            prompt += f"目标长度约为{target_length}字。"
        
        prompt += f"\n\n原文：\n{text}\n\n改写后的文本："
        
        return prompt
