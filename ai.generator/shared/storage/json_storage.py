"""
JSON文件存储
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

from ..config import get_settings

settings = get_settings()


class JSONStorage:
    """JSON文件存储类"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        初始化存储
        
        Args:
            base_dir: 存储基础目录，默认使用配置中的DATA_DIR
        """
        self.base_dir = base_dir or settings.DATA_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        self.projects_dir = self.base_dir / "projects"
        self.projects_dir.mkdir(exist_ok=True)
        
        self.segments_dir = self.base_dir / "segments"
        self.segments_dir.mkdir(exist_ok=True)
    
    def generate_id(self) -> str:
        """生成唯一ID"""
        return str(uuid.uuid4())
    
    # ==================== 项目管理 ====================
    
    def create_project(self, name: str, description: str = "", metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        创建项目
        
        Args:
            name: 项目名称
            description: 项目描述
            metadata: 额外元数据
            
        Returns:
            项目信息字典
        """
        project_id = self.generate_id()
        
        project = {
            "id": project_id,
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "created",
            "metadata": metadata or {},
            "scripts": [],
            "audio_segments": [],
            "video_segments": [],
            "final_video": None
        }
        
        # 保存到文件
        project_file = self.projects_dir / f"{project_id}.json"
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project, f, ensure_ascii=False, indent=2)
        
        return project
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        获取项目信息
        
        Args:
            project_id: 项目ID
            
        Returns:
            项目信息字典，不存在则返回None
        """
        project_file = self.projects_dir / f"{project_id}.json"
        
        if not project_file.exists():
            return None
        
        with open(project_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def update_project(self, project_id: str, **updates) -> bool:
        """
        更新项目信息
        
        Args:
            project_id: 项目ID
            **updates: 要更新的字段
            
        Returns:
            是否成功
        """
        project = self.get_project(project_id)
        if not project:
            return False
        
        # 更新字段
        for key, value in updates.items():
            project[key] = value
        
        # 更新时间戳
        project["updated_at"] = datetime.now().isoformat()
        
        # 保存
        project_file = self.projects_dir / f"{project_id}.json"
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project, f, ensure_ascii=False, indent=2)
        
        return True
    
    def delete_project(self, project_id: str) -> bool:
        """
        删除项目
        
        Args:
            project_id: 项目ID
            
        Returns:
            是否成功
        """
        project_file = self.projects_dir / f"{project_id}.json"
        
        if not project_file.exists():
            return False
        
        # 删除项目文件
        os.remove(project_file)
        
        # 删除相关的段落文件
        segment_files = list(self.segments_dir.glob(f"{project_id}_*.json"))
        for f in segment_files:
            os.remove(f)
        
        return True
    
    def list_projects(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        列出所有项目
        
        Args:
            status: 状态过滤
            
        Returns:
            项目列表
        """
        projects = []
        
        for project_file in self.projects_dir.glob("*.json"):
            with open(project_file, 'r', encoding='utf-8') as f:
                project = json.load(f)
                
                if status is None or project.get("status") == status:
                    projects.append(project)
        
        # 按创建时间排序（最新的在前）
        projects.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return projects
    
    # ==================== 脚本管理 ====================
    
    def save_script(self, project_id: str, script_data: List[Dict[str, Any]]) -> bool:
        """
        保存脚本数据
        
        Args:
            project_id: 项目ID
            script_data: 脚本数据列表
            
        Returns:
            是否成功
        """
        project = self.get_project(project_id)
        if not project:
            return False
        
        project["scripts"] = script_data
        project["status"] = "script_processed"
        
        return self.update_project(project_id, scripts=script_data, status="script_processed")
    
    def get_script(self, project_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        获取脚本数据
        
        Args:
            project_id: 项目ID
            
        Returns:
            脚本数据列表
        """
        project = self.get_project(project_id)
        if not project:
            return None
        
        return project.get("scripts", [])
    
    # ==================== 音频段落管理 ====================
    
    def save_audio_segments(self, project_id: str, segments: List[Dict[str, Any]]) -> bool:
        """
        保存音频段落
        
        Args:
            project_id: 项目ID
            segments: 音频段落列表
            
        Returns:
            是否成功
        """
        project = self.get_project(project_id)
        if not project:
            return False
        
        # 保存到项目
        project["audio_segments"] = segments
        project["status"] = "audio_generated"
        
        return self.update_project(project_id, audio_segments=segments, status="audio_generated")
    
    def get_audio_segments(self, project_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        获取音频段落
        
        Args:
            project_id: 项目ID
            
        Returns:
            音频段落列表
        """
        project = self.get_project(project_id)
        if not project:
            return None
        
        return project.get("audio_segments", [])
    
    # ==================== 视频段落管理 ====================
    
    def save_video_segments(self, project_id: str, segments: List[Dict[str, Any]]) -> bool:
        """
        保存视频段落
        
        Args:
            project_id: 项目ID
            segments: 视频段落列表
            
        Returns:
            是否成功
        """
        project = self.get_project(project_id)
        if not project:
            return False
        
        project["video_segments"] = segments
        project["status"] = "video_generated"
        
        return self.update_project(project_id, video_segments=segments, status="video_generated")
    
    def get_video_segments(self, project_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        获取视频段落
        
        Args:
            project_id: 项目ID
            
        Returns:
            视频段落列表
        """
        project = self.get_project(project_id)
        if not project:
            return None
        
        return project.get("video_segments", [])
    
    # ==================== 最终视频管理 ====================
    
    def save_final_video(self, project_id: str, video_path: str, metadata: Optional[Dict] = None) -> bool:
        """
        保存最终视频
        
        Args:
            project_id: 项目ID
            video_path: 视频文件路径
            metadata: 额外元数据
            
        Returns:
            是否成功
        """
        project = self.get_project(project_id)
        if not project:
            return False
        
        project["final_video"] = {
            "path": video_path,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        project["status"] = "completed"
        
        return self.update_project(
            project_id,
            final_video=project["final_video"],
            status="completed"
        )
    
    def get_final_video(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        获取最终视频信息
        
        Args:
            project_id: 项目ID
            
        Returns:
            视频信息字典
        """
        project = self.get_project(project_id)
        if not project:
            return None
        
        return project.get("final_video")
    
    # ==================== 通用数据存储 ====================
    
    def save_data(self, key: str, data: Any) -> bool:
        """
        保存通用数据
        
        Args:
            key: 数据键
            data: 数据
            
        Returns:
            是否成功
        """
        data_file = self.base_dir / f"{key}.json"
        
        try:
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
    
    def load_data(self, key: str) -> Optional[Any]:
        """
        加载通用数据
        
        Args:
            key: 数据键
            
        Returns:
            数据，不存在则返回None
        """
        data_file = self.base_dir / f"{key}.json"
        
        if not data_file.exists():
            return None
        
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    # ==================== 工具方法 ====================
    
    def export_project(self, project_id: str, export_path: Path) -> bool:
        """
        导出项目数据
        
        Args:
            project_id: 项目ID
            export_path: 导出路径
            
        Returns:
            是否成功
        """
        project = self.get_project(project_id)
        if not project:
            return False
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(project, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
    
    def import_project(self, import_path: Path) -> Optional[str]:
        """
        导入项目数据
        
        Args:
            import_path: 导入文件路径
            
        Returns:
            项目ID，失败则返回None
        """
        if not import_path.exists():
            return None
        
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                project = json.load(f)
            
            # 生成新的项目ID
            old_id = project.get("id")
            new_id = self.generate_id()
            project["id"] = new_id
            project["imported_from"] = old_id
            project["imported_at"] = datetime.now().isoformat()
            
            # 保存项目
            project_file = self.projects_dir / f"{new_id}.json"
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project, f, ensure_ascii=False, indent=2)
            
            return new_id
        except Exception:
            return None
    
    def cleanup_old_projects(self, days: int = 30) -> int:
        """
        清理旧项目
        
        Args:
            days: 天数阈值
            
        Returns:
            删除的项目数量
        """
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        for project_file in self.projects_dir.glob("*.json"):
            try:
                with open(project_file, 'r', encoding='utf-8') as f:
                    project = json.load(f)
                
                created_at = datetime.fromisoformat(project.get("created_at", ""))
                
                if created_at < cutoff and project.get("status") == "completed":
                    if self.delete_project(project["id"]):
                        deleted_count += 1
            except Exception:
                continue
        
        return deleted_count


# 创建全局存储实例
storage = JSONStorage()
