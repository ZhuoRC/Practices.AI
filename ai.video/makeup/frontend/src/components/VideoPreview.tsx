import React from 'react';
import { TaskResponse, getDownloadUrl } from '../services/api';

interface VideoPreviewProps {
  task: TaskResponse | null;
}

export const VideoPreview: React.FC<VideoPreviewProps> = ({ task }) => {
  if (!task || task.status !== 'completed' || !task.output_path) {
    return null;
  }

  const downloadUrl = getDownloadUrl(task.task_id);

  // Convert output path to URL for preview
  // The output files are served from /outputs directory
  const outputFilename = task.output_path.split(/[/\\]/).pop();
  const previewUrl = `/outputs/${outputFilename}`;

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `faceswap_${task.task_id}.mp4`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="card">
      <h2>Result</h2>
      <div className="preview-container">
        <video
          src={previewUrl}
          controls
          style={{ maxWidth: '100%', maxHeight: '400px' }}
        />
      </div>
      <div style={{ marginTop: '16px', textAlign: 'center' }}>
        <button className="btn btn-primary" onClick={handleDownload}>
          Download Video
        </button>
      </div>
    </div>
  );
};
