export interface VideoMetadata {
    video_id: string;
    filename: string;
    duration: number;
    file_size: number;
    upload_path: string;
    created_at: string;
}

export interface ChapterInfo {
    chapter_id: string;
    title: string;
    start_time: number;
    end_time: number;
    duration: number;
    subtitle_text: string;
    video_path?: string;
    subtitle_path?: string;
}

export enum ProcessingStatus {
    PENDING = 'pending',
    UPLOADING = 'uploading',
    EXTRACTING_SUBTITLES = 'extracting_subtitles',
    ANALYZING_CONTENT = 'analyzing_content',
    SPLITTING_VIDEO = 'splitting_video',
    COMPLETED = 'completed',
    FAILED = 'failed',
}

export interface ProcessingTask {
    task_id: string;
    video_id: string;
    status: ProcessingStatus;
    progress: number;
    current_step: string;
    error_message?: string;
    video_metadata?: VideoMetadata;
    chapters: ChapterInfo[];
}

export interface VideoTreeNode {
    video_id: string;
    title: string;
    duration: number;
    is_parent: boolean;
    video_path: string;
    subtitle_path?: string;
    children: VideoTreeNode[];
}

export interface UploadResponse {
    task_id: string;
    video_id: string;
    message: string;
}

export interface StatusResponse {
    task: ProcessingTask;
}

export interface TreeResponse {
    tree: VideoTreeNode;
}
