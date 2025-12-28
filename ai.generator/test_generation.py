"""
测试生成流程
演示如何使用AI Generator系统从文本生成视频
"""
import asyncio
import os
from pathlib import Path
from datetime import datetime
from shared.storage import storage
from script_processor import ScriptProcessor, ScriptProcessRequest
from audio_generator import AudioGenerator, AudioGenerationRequest
from video_generator import VideoGenerator, VideoGenerationRequest
from shared.config import get_settings

settings = get_settings()

# 生成时间戳
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_session_dir = settings.OUTPUT_DIR / timestamp
output_session_dir.mkdir(parents=True, exist_ok=True)

# 创建子目录
audio_session_dir = output_session_dir / "audio"
audio_session_dir.mkdir(parents=True, exist_ok=True)
video_session_dir = output_session_dir / "video"
video_session_dir.mkdir(parents=True, exist_ok=True)
final_session_dir = output_session_dir / "final"
final_session_dir.mkdir(parents=True, exist_ok=True)

print(f"\n输出目录: {output_session_dir}")


async def test_script_processing(project_id: str, script_text: str):
    """测试脚本处理"""
    print("\n" + "="*50)
    print("1. 开始处理脚本...")
    print("="*50)
    
    processor = ScriptProcessor()
    
    # 创建处理请求
    request = ScriptProcessRequest(
        project_id=project_id,
        script_text=script_text,
        language="zh",
        enable_rewrite=False,  # 关闭AI改写，避免需要API密钥
        enable_segmentation=True,
        extract_keywords=True,
        estimate_duration=True
    )
    
    # 处理脚本
    result = await processor.process_script(request)
    
    print(f"\n✓ 脚本处理完成！")
    print(f"  - 段落数量: {len(result.segments)}")
    print(f"  - 总时长: {result.total_duration:.2f} 秒")
    print(f"  - 处理时间: {result.processing_time:.2f} 秒")
    
    # 显示前3个段落
    print("\n前3个段落预览:")
    for i, seg in enumerate(result.segments[:3], 1):
        print(f"\n段落 {i}:")
        print(f"  文本: {seg.original_text[:50]}...")
        print(f"  时长: {seg.estimated_duration:.2f} 秒")
        print(f"  关键词: {', '.join(seg.keywords[:3])}")
    
    # 保存脚本数据
    storage.save_script(project_id, [seg.model_dump() for seg in result.segments])
    print(f"\n✓ 脚本数据已保存到JSON文件")
    
    return result.segments


async def test_audio_generation(project_id: str, segments):
    """测试音频生成"""
    print("\n" + "="*50)
    print("2. 开始生成音频...")
    print("="*50)
    
    # 使用auto模式，自动选择可用的TTS提供商
    # 优先级: Windows本地 > Azure > ElevenLabs
    provider = "auto"
    print(f"\n提供商模式: auto (自动选择)")
    print("  - Windows PowerShell TTS: 已检测")
    azure_status = "已配置" if settings.AZURE_TTS_KEY else "未配置"
    print(f"  - Azure TTS: {azure_status}")
    eleven_status = "已配置" if settings.ELEVENLABS_API_KEY else "未配置"
    print(f"  - ElevenLabs: {eleven_status}")
    
    # 创建音频生成器
    audio_gen = AudioGenerator()
    
    # 处理所有段落
    test_segments = [seg.model_dump() for seg in segments]
    
    request = AudioGenerationRequest(
        project_id=project_id,
        segments=test_segments,
        provider=provider,
        language="zh",
        output_format="wav",  # 使用wav格式避免转换问题
        batch_size=3,
        output_dir=str(output_session_dir)
    )
    
    # 生成音频
    result = await audio_gen.generate_audio(request)
    
    print(f"\n✓ 音频生成完成！")
    print(f"  - 状态: {result.status}")
    print(f"  - 总时长: {result.total_duration:.2f} 秒")
    print(f"  - 处理时间: {result.processing_time:.2f} 秒")
    
    # 显示生成的音频段落
    print("\n音频段落:")
    for seg in result.segments:
        print(f"  段落 {seg.index}: {seg.status}")
        if seg.file_path:
            print(f"    文件: {Path(seg.file_path).name}")
        if seg.error_message:
            print(f"    错误: {seg.error_message}")
    
    # 保存音频数据
    storage.save_audio_segments(project_id, [seg.model_dump() for seg in result.segments])
    print(f"\n✓ 音频数据已保存")
    
    return [seg.model_dump() for seg in result.segments]


async def test_video_generation(project_id: str, segments, audio_segments):
    """测试视频生成"""
    print("\n" + "="*50)
    print("3. 开始生成视频...")
    print("="*50)
    
    # 创建视频生成器
    video_gen = VideoGenerator()
    
    # 处理所有段落
    test_segments = [seg.model_dump() for seg in segments]
    
    # 收集音频文件路径
    audio_files = []
    for i, audio_seg in enumerate(audio_segments):
        if audio_seg.get('file_path') and i < len(test_segments):
            audio_files.append(audio_seg['file_path'])
        else:
            audio_files.append(None)
    
    print(f"\n音频文件: {len(audio_files)} 个")
    
    # 检查音频文件是否有效（大于1KB）
    valid_audio_files = []
    for i, audio_file in enumerate(audio_files):
        if audio_file and os.path.exists(audio_file):
            size = os.path.getsize(audio_file)
            if size > 1024:  # 大于1KB认为有效
                valid_audio_files.append(audio_file)
                print(f"  音频 {i+1}: 有效 ({size} 字节)")
            else:
                print(f"  音频 {i+1}: 无效 ({size} 字节，太小说明TTS失败)")
                valid_audio_files.append(None)
        else:
            print(f"  音频 {i+1}: 不存在")
            valid_audio_files.append(None)
    
    # 为每个段落设置5秒时长
    request = VideoGenerationRequest(
        project_id=project_id,
        segments=test_segments,
        duration=5.0,
        resolution="1920x1080",
        fps=30,
        background_style="gradient",
        text_animation="fade_in",
        highlight_keywords=True,
        font_family="SimHei",
        font_size=48,
        font_color="#FFFFFF",
        background_color="#1A1A2E",
        audio_files=valid_audio_files,  # 传入有效的音频文件
        merge_segments=True,  # 合并所有段落为一个视频
        output_dir=str(output_session_dir)
    )
    
    # 生成视频
    print("\n正在生成视频（这可能需要几分钟）...")
    result = await video_gen.generate_video(request)
    
    print(f"\n✓ 视频生成完成！")
    print(f"  - 状态: {result.status}")
    print(f"  - 总时长: {result.total_duration:.2f} 秒")
    print(f"  - 处理时间: {result.processing_time:.2f} 秒")
    
    # 显示生成的视频段落
    print("\n视频段落:")
    for seg in result.segments:
        print(f"  段落 {seg.index}: {seg.status}")
        if seg.file_path:
            print(f"    文件: {Path(seg.file_path).name}")
            print(f"    分辨率: {seg.resolution['width']}x{seg.resolution['height']}")
            print(f"    文件大小: {seg.file_size / 1024 / 1024:.2f} MB")
        if seg.error_message:
            print(f"    错误: {seg.error_message}")
    
    # 显示合并后的视频
    if result.metadata.get('final_video_path'):
        final_path = result.metadata['final_video_path']
        print(f"\n✓ 最终合并视频: {Path(final_path).name}")
    
    # 保存视频数据
    storage.save_video_segments(project_id, [seg.model_dump() for seg in result.segments])
    print(f"\n✓ 视频数据已保存")
    
    return [seg.model_dump() for seg in result.segments]


async def main():
    """主函数"""
    print("\n" + "="*60)
    print("AI Generator - 测试生成流程")
    print("="*60)
    
    # 读取脚本文件
    script_path = settings.INPUT_DIR / "scripts.txt"
    print(f"\n读取脚本文件: {script_path}")
    
    with open(script_path, 'r', encoding='utf-8') as f:
        script_text = f.read()
    
    print(f"脚本长度: {len(script_text)} 字符")
    
    # 创建项目
    print("\n创建新项目...")
    project = storage.create_project(
        name="原研药和仿制药",
        description="测试AI视频生成系统"
    )
    project_id = project["id"]
    print(f"✓ 项目已创建: {project_id}")
    print(f"  名称: {project['name']}")
    print(f"  状态: {project['status']}")
    
    try:
        # 1. 处理脚本
        segments = await test_script_processing(project_id, script_text)
        
        # 2. 生成音频
        audio_segments = await test_audio_generation(project_id, segments)
        
        # 3. 生成视频（使用音频文件）
        video_segments = await test_video_generation(project_id, segments, audio_segments)
        
        # 4. 总结
        print("\n" + "="*50)
        print("✓ 所有测试完成！")
        print("="*50)
        print(f"\n项目ID: {project_id}")
        print(f"项目数据位置: {settings.DATA_DIR / 'projects' / f'{project_id}.json'}")
        print(f"输出文件位置: {settings.OUTPUT_DIR}")
        
        print("\n下一步:")
        print("1. 检查生成的音频和视频文件")
        print("2. 使用播放器查看视频效果")
        print("3. 如需完整生成，修改脚本以处理所有段落")
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        
        # 更新项目状态为失败
        storage.update_project(project_id, status="failed")
    
    finally:
        # 显示项目信息
        print("\n" + "="*50)
        print("项目信息")
        print("="*50)
        project_info = storage.get_project(project_id)
        if project_info:
            print(f"项目ID: {project_info['id']}")
            print(f"项目名称: {project_info['name']}")
            print(f"创建时间: {project_info['created_at']}")
            print(f"状态: {project_info['status']}")
            print(f"脚本段落数: {len(project_info.get('scripts', []))}")
            print(f"音频段落数: {len(project_info.get('audio_segments', []))}")
            print(f"视频段落数: {len(project_info.get('video_segments', []))}")


if __name__ == "__main__":
    asyncio.run(main())
