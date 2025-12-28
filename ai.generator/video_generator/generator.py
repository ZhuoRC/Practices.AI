"""
视频生成核心逻辑 - 使用FFmpeg
"""
import time
import os
import subprocess
from typing import List, Dict, Any, Optional
from pathlib import Path
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio

from shared.config import get_settings
from .models import (
    VideoSegment,
    VideoGenerationRequest,
    VideoGenerationResponse,
    VideoEffect,
    RenderConfig
)

settings = get_settings()


class VideoGenerator:
    """视频生成器 - 使用FFmpeg"""
    
    def __init__(self):
        """初始化生成器"""
        self.temp_dir = settings.TEMP_DIR / "video"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取FFmpeg路径
        self.ffmpeg_path = self._get_ffmpeg_path()
    
    def _get_ffmpeg_path(self) -> str:
        """获取FFmpeg路径"""
        # 优先使用环境变量配置的路径
        if settings.FFMPEG_PATH:
            if os.path.exists(settings.FFMPEG_PATH):
                return settings.FFMPEG_PATH
        
        # 检查项目中的ffmpeg目录
        project_ffmpeg = Path(__file__).parent.parent.parent / "ffmpeg" / "win_x64" / "bin" / "ffmpeg.exe"
        if project_ffmpeg.exists():
            return str(project_ffmpeg)
        
        # 检查系统PATH
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            return 'ffmpeg'
        except:
            return None
    
    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResponse:
        """
        生成视频
        """
        start_time = time.time()
        segments: List[VideoSegment] = []
        
        try:
            if not self.ffmpeg_path:
                raise Exception("FFmpeg未找到。请安装FFmpeg或设置FFMPEG_PATH环境变量")
            
            # 解析分辨率
            width, height = map(int, request.resolution.split('x'))
            
            # 创建渲染配置
            render_config = RenderConfig(
                width=width,
                height=height,
                fps=request.fps
            )
            
            # 为每个段落生成视频
            for seg_info in request.segments:
                text = seg_info.get('original_text', seg_info.get('text', ''))
                index = seg_info.get('index', 0)
                keywords = seg_info.get('keywords', [])
                audio_file = None
                
                # 获取对应的音频文件
                if request.audio_files and index - 1 < len(request.audio_files):
                    audio_file = request.audio_files[index - 1]
                
                # 生成视频段落（带音频）
                result = await self._generate_single_video(
                    text=text,
                    keywords=keywords,
                    index=index,
                    project_id=request.project_id,
                    duration=request.duration,
                    render_config=render_config,
                    background_style=request.background_style,
                    text_animation=request.text_animation,
                    highlight_keywords=request.highlight_keywords,
                    font_family=request.font_family,
                    font_size=request.font_size,
                    font_color=request.font_color,
                    background_color=request.background_color,
                    audio_file=audio_file,  # 传入音频文件
                    output_dir=request.output_dir  # 传入自定义输出目录
                )
                
                segments.append(result)
            
            # 如果需要合并所有段落
            final_video_path = None
            if request.merge_segments and len(segments) > 1:
                final_video_path = await self._merge_video_segments(
                    project_id=request.project_id,
                    segments=segments,
                    output_dir=request.output_dir
                )
            
            # 计算总时长
            total_duration = sum(seg.duration or 0 for seg in segments)
            
            # 计算处理时间
            processing_time = time.time() - start_time
            
            metadata = {
                "resolution": request.resolution,
                "fps": request.fps,
                "segment_count": len(segments),
                "background_style": request.background_style,
                "text_animation": request.text_animation
            }
            
            if final_video_path:
                metadata["final_video_path"] = final_video_path
            
            return VideoGenerationResponse(
                project_id=request.project_id,
                status="success",
                segments=segments,
                total_duration=total_duration,
                processing_time=processing_time,
                metadata=metadata
            )
            
        except Exception as e:
            return VideoGenerationResponse(
                project_id=request.project_id,
                status="error",
                segments=segments,
                total_duration=0.0,
                processing_time=time.time() - start_time,
                metadata={"error": str(e)}
            )
    
    async def _generate_single_video(
        self,
        text: str,
        keywords: List[str],
        index: int,
        project_id: str,
        duration: float,
        render_config: RenderConfig,
        background_style: str,
        text_animation: str,
        highlight_keywords: bool,
        font_family: str,
        font_size: int,
        font_color: str,
        background_color: str,
        audio_file: Optional[str] = None,
        output_dir: Optional[str] = None
    ) -> VideoSegment:
        """
        生成单个视频段落
        """
        try:
            # 生成文件路径
            filename = f"{project_id}_video_{index:04d}.mp4"
            # 使用自定义输出目录或默认目录
            if output_dir:
                output_path = Path(output_dir) / "video" / filename
            else:
                output_path = settings.OUTPUT_DIR / "video" / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 使用FFmpeg生成视频（带音频）
            success = self._generate_video_with_ffmpeg(
                text=text,
                keywords=keywords,
                output_path=str(output_path),
                width=render_config.width,
                height=render_config.height,
                fps=render_config.fps,
                duration=duration,
                background_style=background_style,
                font_family=font_family,
                font_size=font_size,
                font_color=font_color,
                background_color=background_color,
                audio_file=audio_file  # 传入音频文件
            )
            
            if not success:
                raise Exception("FFmpeg视频生成失败")
            
            # 获取文件大小
            file_size = os.path.getsize(output_path) if output_path.exists() else 0
            
            return VideoSegment(
                index=index,
                text=text,
                keywords=keywords,
                file_path=str(output_path),
                duration=duration,
                resolution={"width": render_config.width, "height": render_config.height},
                fps=render_config.fps,
                file_size=file_size,
                status="completed"
            )
            
        except Exception as e:
            return VideoSegment(
                index=index,
                text=text,
                keywords=keywords,
                status="failed",
                error_message=str(e)
            )
    
    def _generate_video_with_ffmpeg(
        self,
        text: str,
        keywords: List[str],
        output_path: str,
        width: int,
        height: int,
        fps: int,
        duration: float,
        background_style: str,
        font_family: str,
        font_size: int,
        font_color: str,
        background_color: str,
        audio_file: Optional[str] = None
    ) -> bool:
        """
        使用FFmpeg生成视频
        """
        try:
            # 生成背景颜色
            bg_color = background_color.lstrip('#')
            
            # 解析颜色
            r = int(bg_color[0:2], 16)
            g = int(bg_color[2:4], 16)
            b = int(bg_color[4:6], 16)
            
            # 创建FFmpeg命令
            # 使用color滤镜生成背景
            # 使用drawtext滤镜添加文字
            # 添加静音音轨
            
            # 处理文本（转义特殊字符）
            escaped_text = text.replace('\\', '\\\\').replace(':', '\\:').replace("'", "\\'")
            
            # 构建FFmpeg命令
            if audio_file and os.path.exists(audio_file):
                # 使用音频文件
                cmd = [
                    self.ffmpeg_path,
                    '-y',  # 覆盖输出文件
                    '-f', 'lavfi',  # 使用libavfilter输入
                    '-i', f'color=c=0x{bg_color}:s={width}x{height}:d={int(duration)}',  # 纯色背景
                    '-i', audio_file,  # 使用音频文件
                    '-shortest',  # 使用最短的流
                    '-vf', f'drawtext=text={escaped_text}:fontfile={font_family}:fontsize={font_size}:fontcolor={font_color}:x=(w-text_w)/2:y=(h-text_h)/2',
                    '-c:v', 'libx264',
                    '-c:a', 'aac',  # 音频编码
                    '-preset', 'medium',
                    '-crf', '23',
                    '-pix_fmt', 'yuv420p',
                    '-t', str(duration),
                    output_path
                ]
            else:
                # 使用静音音轨
                cmd = [
                    self.ffmpeg_path,
                    '-y',  # 覆盖输出文件
                    '-f', 'lavfi',  # 使用libavfilter输入
                    '-i', f'color=c=0x{bg_color}:s={width}x{height}:d={int(duration)}',  # 纯色背景
                    '-f', 'lavfi',  # 添加静音音轨
                    '-i', f'anullsrc=r={fps}:cl=stereo',  # 静音源
                    '-shortest',  # 使用最短的流
                    '-vf', f'drawtext=text={escaped_text}:fontfile={font_family}:fontsize={font_size}:fontcolor={font_color}:x=(w-text_w)/2:y=(h-text_h)/2',
                    '-c:v', 'libx264',
                    '-c:a', 'aac',  # 音频编码
                    '-preset', 'medium',
                    '-crf', '23',
                    '-pix_fmt', 'yuv420p',
                    '-t', str(duration),
                    output_path
                ]
            
            # 执行FFmpeg命令
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode != 0:
                print(f"FFmpeg错误: {result.stderr}")
                return False
            
            return True
            
        except Exception as e:
            print(f"生成视频时出错: {e}")
            return False
    
    def _generate_video_with_images(
        self,
        text: str,
        keywords: List[str],
        output_path: str,
        width: int,
        height: int,
        fps: int,
        duration: float,
        background_style: str,
        font_family: str,
        font_size: int,
        font_color: str,
        background_color: str
    ) -> bool:
        """
        使用PIL生成图片，然后用imageio转换为视频
        """
        try:
            # 计算帧数
            num_frames = int(duration * fps)
            
            # 解析颜色
            bg_color = background_color.lstrip('#')
            r = int(bg_color[0:2], 16)
            g = int(bg_color[2:4], 16)
            b = int(bg_color[4:6], 16)
            font_rgb = (int(font_color[1:3], 16), int(font_color[3:5], 16), int(font_color[5:7], 16))
            
            # 准备字体
            try:
                font = ImageFont.truetype(font_family, font_size)
            except:
                try:
                    # 尝试使用系统字体
                    font = ImageFont.truetype("C:\\Windows\\Fonts\\simhei.ttf", font_size)
                except:
                    font = ImageFont.load_default()
            
            # 生成帧
            frames = []
            for frame_idx in range(num_frames):
                # 创建图像
                img = Image.new('RGB', (width, height), (r, g, b))
                draw = ImageDraw.Draw(img)
                
                # 计算文字位置（居中）
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                x = (width - text_width) // 2
                y = (height - text_height) // 2
                
                # 绘制文字
                draw.text((x, y), text, font=font, fill=font_rgb)
                
                # 转换为numpy数组
                frame = np.array(img)
                frames.append(frame)
            
            # 保存为视频
            with imageio.get_writer(output_path, fps=fps, codec='libx264', quality=8) as writer:
                for frame in frames:
                    writer.append_data(frame)
            
            return True
            
        except Exception as e:
            print(f"使用图片生成视频时出错: {e}")
            return False
    
    async def _merge_video_segments(
        self,
        project_id: str,
        segments: List[VideoSegment],
        output_dir: Optional[str] = None
    ) -> str:
        """
        合并所有视频段落为一个完整视频
        """
        try:
            # 生成最终视频文件名
            final_filename = f"{project_id}_final.mp4"
            # 使用自定义输出目录或默认目录
            if output_dir:
                final_output_path = Path(output_dir) / "final" / final_filename
            else:
                final_output_path = settings.OUTPUT_DIR / "final" / final_filename
            final_output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 收集所有视频文件路径
            video_files = []
            for seg in segments:
                if seg.file_path and os.path.exists(seg.file_path):
                    video_files.append(seg.file_path)
            
            if not video_files:
                print("没有可合并的视频文件")
                return None
            
            # 创建文件列表
            list_file = self.temp_dir / f"{project_id}_concat.txt"
            with open(list_file, 'w', encoding='utf-8') as f:
                for video_file in video_files:
                    # 使用绝对路径
                    abs_path = os.path.abspath(video_file).replace('\\', '/')
                    f.write(f"file '{abs_path}'\n")
            
            # 使用FFmpeg concat滤镜合并视频
            cmd = [
                self.ffmpeg_path,
                '-y',  # 覆盖输出文件
                '-f', 'concat',
                '-safe', '0',  # 允许任意路径
                '-i', str(list_file),
                '-c', 'copy',  # 复制流，不重新编码
                str(final_output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode != 0:
                print(f"合并视频失败: {result.stderr}")
                return None
            
            print(f"✓ 视频合并完成: {final_filename}")
            return str(final_output_path)
            
        except Exception as e:
            print(f"合并视频时出错: {e}")
            return None
    
    async def get_available_effects(self) -> List[VideoEffect]:
        """
        获取可用的视频效果
        """
        return [
            # 背景效果
            VideoEffect(
                effect_id="solid",
                name="纯色背景",
                category="background",
                description="使用纯色作为背景"
            ),
            
            # 文字效果
            VideoEffect(
                effect_id="center",
                name="居中文字",
                category="animation",
                description="文字居中显示"
            ),
            
            # 转场效果
            VideoEffect(
                effect_id="cut",
                name="直接切换",
                category="transition",
                description="段落间直接切换"
            )
        ]
