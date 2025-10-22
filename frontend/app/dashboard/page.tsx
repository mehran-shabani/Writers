'use client';

import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import useSWR from 'swr';
import api from '@/lib/api';
import { TaskListResponse, Task, TaskStatus } from '@/types/task';

const fetcher = (url: string) => api.get(url).then(res => res.data);

export default function DashboardPage() {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  
  // Fetch tasks with 10-second polling
  const { data, error, isLoading, mutate } = useSWR<TaskListResponse>(
    user ? '/api/v1/tasks' : null,
    fetcher,
    {
      refreshInterval: 10000, // Poll every 10 seconds
      revalidateOnFocus: true,
    }
  );

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  const handleRefresh = () => {
    mutate();
  };

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
          <h1>داشبورد</h1>
          <div className="user-info">
            <span className="user-name">
              {user.full_name || user.username}
            </span>
            <button onClick={handleLogout} className="btn-logout">
              خروج
            </button>
          </div>
        </div>
      </header>

      <div className="dashboard-content">
        <div className="container">
          {/* User Info Card */}
          <div className="card" style={{ marginBottom: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h2>خوش آمدید!</h2>
              <button 
                onClick={() => router.push('/dashboard/upload')} 
                className="btn btn-primary"
                style={{ width: 'auto', padding: '0.875rem 2rem' }}
              >
                آپلود فایل جدید
              </button>
            </div>
            <p>
              <strong>ایمیل:</strong> {user.email} | <strong>نام کاربری:</strong> {user.username}
            </p>
          </div>

          {/* Tasks Section */}
          <div className="card">
            <div className="tasks-header">
              <h2>وظایف من</h2>
              <button 
                onClick={handleRefresh} 
                className="btn-refresh"
                disabled={isLoading}
              >
                🔄 {isLoading ? 'در حال بروزرسانی...' : 'بروزرسانی'}
              </button>
            </div>

            {error && (
              <div className="error-message" style={{ marginTop: '1rem' }}>
                خطا در بارگذاری وظایف. لطفاً دوباره تلاش کنید.
              </div>
            )}

            {isLoading && !data && (
              <div style={{ textAlign: 'center', padding: '2rem', color: '#718096' }}>
                در حال بارگذاری وظایف...
              </div>
            )}

            {data && data.tasks.length === 0 && (
              <div style={{ textAlign: 'center', padding: '2rem', color: '#718096' }}>
                هیچ وظیفه‌ای یافت نشد. برای شروع یک فایل آپلود کنید.
              </div>
            )}

            {data && data.tasks.length > 0 && (
              <div className="tasks-grid">
                {data.tasks.map((task: Task) => (
                  <div 
                    key={task.id} 
                    className="task-card"
                    onClick={() => router.push(`/dashboard/tasks/${task.id}`)}
                  >
                    <div className="task-card-header">
                      <h3 className="task-title">{task.title}</h3>
                      <span className={getStatusBadgeClass(task.status)}>
                        {getStatusText(task.status)}
                      </span>
                    </div>
                    
                    {task.description && (
                      <p className="task-description">{task.description}</p>
                    )}
                    
                    <div className="task-metadata">
                      <div className="metadata-item">
                        <span className="metadata-label">ایجاد شده:</span>
                        <span className="metadata-value">{formatDate(task.created_at)}</span>
                      </div>
                      
                      {task.completed_at && (
                        <div className="metadata-item">
                          <span className="metadata-label">تکمیل شده:</span>
                          <span className="metadata-value">{formatDate(task.completed_at)}</span>
                        </div>
                      )}
                      
                      {task.file_path && (
                        <div className="metadata-item">
                          <span className="metadata-label">📎 فایل:</span>
                          <span className="metadata-value">موجود</span>
                        </div>
                      )}
                      
                      {task.result_path && (
                        <div className="metadata-item">
                          <span className="metadata-label">✅ نتیجه:</span>
                          <span className="metadata-value">آماده دانلود</span>
                        </div>
                      )}
                    </div>
                    
                    <div className="task-card-footer">
                      <span className="view-details">مشاهده جزئیات ←</span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {data && data.total > 0 && (
              <div className="tasks-footer">
                <p>تعداد کل وظایف: {data.total}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
