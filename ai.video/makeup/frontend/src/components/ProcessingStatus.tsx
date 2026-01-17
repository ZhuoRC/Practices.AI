import React from 'react';
import { TaskResponse } from '../services/api';

interface ProcessingStatusProps {
  task: TaskResponse | null;
  isProcessing: boolean;
}

export const ProcessingStatus: React.FC<ProcessingStatusProps> = ({
  task,
  isProcessing,
}) => {
  if (!task && !isProcessing) {
    return null;
  }

  const getStatusClass = (status: string) => {
    switch (status) {
      case 'pending':
        return 'status-pending';
      case 'processing':
        return 'status-processing';
      case 'completed':
        return 'status-completed';
      case 'failed':
        return 'status-failed';
      default:
        return '';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending':
        return 'Pending';
      case 'processing':
        return 'Processing';
      case 'completed':
        return 'Completed';
      case 'failed':
        return 'Failed';
      default:
        return status;
    }
  };

  return (
    <div className="card">
      <h2>Processing Status</h2>

      {isProcessing && !task && (
        <div className="progress-container">
          <p>Starting face swap process...</p>
        </div>
      )}

      {task && (
        <>
          <div style={{ marginBottom: '16px' }}>
            <span className={`status ${getStatusClass(task.status)}`}>
              {getStatusText(task.status)}
            </span>
          </div>

          {(task.status === 'processing' || task.status === 'pending') && (
            <div className="progress-container">
              <div className="progress-bar">
                <div
                  className="progress-bar-fill"
                  style={{ width: `${task.progress}%` }}
                >
                  {task.progress > 5 && `${task.progress}%`}
                </div>
              </div>
              <p style={{ marginTop: '8px', color: '#666' }}>
                Progress: {task.progress}%
              </p>
            </div>
          )}

          {task.status === 'failed' && task.error_message && (
            <div className="error-message">
              <strong>Error:</strong> {task.error_message}
            </div>
          )}

          <div style={{ marginTop: '16px', fontSize: '14px', color: '#666' }}>
            <p>Task ID: {task.task_id}</p>
            <p>Created: {new Date(task.created_at).toLocaleString()}</p>
            <p>Updated: {new Date(task.updated_at).toLocaleString()}</p>
          </div>
        </>
      )}
    </div>
  );
};
