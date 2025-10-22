'use client';

import { useRouter, useParams } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import useSWR from 'swr';
import api from '@/lib/api';
import { Task, TaskStatus } from '@/types/task';

const fetcher = (url: string) => api.get(url).then(res => res.data);

export default function TaskDetailPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const params = useParams();
  const taskId = params.taskId as string;
  
  // Fetch task details with polling
  const { data: task, error, isLoading, mutate } = useSWR<Task>(
    user && taskId ? `/api/v1/tasks/${taskId}` : null,
    fetcher,
    {
      refreshInterval: 10000, // Poll every 10 seconds
      revalidateOnFocus: true,
    }
  );

  const getStatusBadgeClass = (status: TaskStatus) => {
    switch (status) {
      case TaskStatus.COMPLETED:
        return 'status-badge status-completed';
      case TaskStatus.FAILED:
        return 'status-badge status-failed';
      case TaskStatus.PROCESSING:
      case TaskStatus.IN_PROGRESS:
        return 'status-badge status-processing';
      case TaskStatus.PENDING:
        return 'status-badge status-pending';
      case TaskStatus.CANCELLED:
        return 'status-badge status-cancelled';
      default:
        return 'status-badge';
    }
  };

  const getStatusText = (status: TaskStatus) => {
    switch (status) {
      case TaskStatus.PENDING:
        return 'در انتظار';
      case TaskStatus.PROCESSING:
      case TaskStatus.IN_PROGRESS:
        return 'در حال پردازش';
      case TaskStatus.COMPLETED:
        return 'تکمیل شده';
      case TaskStatus.FAILED:
        return 'ناموفق';
      case TaskStatus.CANCELLED:
        return 'لغو شده';
      default:
        return status;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('fa-IR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    }).format(date);
  };

  if (loading) {
    return (
      <div className="loading">
        <p>در حال بارگذاری...</p>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="container">
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <button 
              onClick={() => router.push('/dashboard')} 
              className="btn-back"
            >
              ← بازگشت
            </button>
            <h1>جزئیات وظیفه</h1>
          </div>
        </div>
      </header>

      <div className="dashboard-content">
        <div className="container">
          {error && (
            <div className="card">
              <div className="error-message">
                {error.response?.status === 404 
                  ? 'وظیفه مورد نظر یافت نشد.'
                  : 'خطا در بارگذاری جزئیات وظیفه. لطفاً دوباره تلاش کنید.'}
              </div>
              <button 
                onClick={() => router.push('/dashboard')} 
                className="btn btn-secondary"
                style={{ marginTop: '1rem' }}
              >
                بازگشت به داشبورد
              </button>
            </div>
          )}

          {isLoading && !task && (
            <div className="card">
              <div style={{ textAlign: 'center', padding: '2rem', color: '#718096' }}>
                در حال بارگذاری جزئیات...
              </div>
            </div>
          )}

          {task && (
            <div className="card">
              <div className="task-detail-header">
                <div>
                  <h2 style={{ marginBottom: '0.5rem' }}>{task.title}</h2>
                  <span className={getStatusBadgeClass(task.status)}>
                    {getStatusText(task.status)}
                  </span>
                </div>
                <button 
                  onClick={() => mutate()} 
                  className="btn-refresh"
                  disabled={isLoading}
                >
                  🔄 {isLoading ? 'در حال بروزرسانی...' : 'بروزرسانی'}
                </button>
              </div>

              {task.description && (
                <div className="task-detail-section">
                  <h3>توضیحات</h3>
                  <p>{task.description}</p>
                </div>
              )}

              <div className="task-detail-section">
                <h3>اطلاعات زمانی</h3>
                <div className="detail-grid">
                  <div className="detail-item">
                    <span className="detail-label">ایجاد شده:</span>
                    <span className="detail-value">{formatDate(task.created_at)}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">آخرین بروزرسانی:</span>
                    <span className="detail-value">{formatDate(task.updated_at)}</span>
                  </div>
                  {task.due_date && (
                    <div className="detail-item">
                      <span className="detail-label">موعد مقرر:</span>
                      <span className="detail-value">{formatDate(task.due_date)}</span>
                    </div>
                  )}
                  {task.completed_at && (
                    <div className="detail-item">
                      <span className="detail-label">تکمیل شده:</span>
                      <span className="detail-value">{formatDate(task.completed_at)}</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="task-detail-section">
                <h3>فایل‌ها</h3>
                <div className="detail-grid">
                  <div className="detail-item">
                    <span className="detail-label">فایل ورودی:</span>
                    <span className="detail-value">
                      {task.file_path ? (
                        <span className="file-badge">📎 موجود</span>
                      ) : (
                        <span style={{ color: '#a0aec0' }}>ندارد</span>
                      )}
                    </span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">فایل نتیجه:</span>
                    <span className="detail-value">
                      {task.result_path ? (
                        <span className="file-badge success">✅ آماده دانلود</span>
                      ) : (
                        <span style={{ color: '#a0aec0' }}>در انتظار پردازش</span>
                      )}
                    </span>
                  </div>
                </div>
              </div>

              {task.file_path && (
                <div className="task-detail-section">
                  <h3>مسیر فایل</h3>
                  <div className="code-block">
                    {task.file_path}
                  </div>
                </div>
              )}

              {task.result_path && (
                <div className="task-detail-section">
                  <h3>مسیر نتیجه</h3>
                  <div className="code-block">
                    {task.result_path}
                  </div>
                </div>
              )}

              <div className="task-detail-section">
                <h3>شناسه‌ها</h3>
                <div className="detail-grid">
                  <div className="detail-item">
                    <span className="detail-label">شناسه وظیفه:</span>
                    <span className="detail-value code-text">{task.id}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">شناسه کاربر:</span>
                    <span className="detail-value code-text">{task.user_id}</span>
                  </div>
                </div>
              </div>

              <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem' }}>
                <button 
                  onClick={() => router.push('/dashboard')} 
                  className="btn btn-secondary"
                  style={{ flex: 1 }}
                >
                  بازگشت به داشبورد
                </button>
                {task.status === TaskStatus.COMPLETED && task.result_path && (
                  <button 
                    className="btn btn-primary"
                    style={{ flex: 1 }}
                    onClick={() => {
                      // Download functionality can be implemented here
                      alert('قابلیت دانلود به زودی اضافه خواهد شد');
                    }}
                  >
                    دانلود نتیجه
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
