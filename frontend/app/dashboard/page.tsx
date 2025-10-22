'use client';

import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';

export default function DashboardPage() {
  const { user, loading, logout } = useAuth();
  const router = useRouter();

  const handleLogout = async () => {
    await logout();
    router.push('/login');
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
          <div className="card">
            <h2>خوش آمدید!</h2>
            <p>
              به سیستم مدیریت وظایف خوش آمدید. این صفحه محافظت شده است و تنها کاربران
              احراز هویت شده می‌توانند به آن دسترسی داشته باشند.
            </p>
            <br />
            <p>
              <strong>ایمیل:</strong> {user.email}
            </p>
            <p>
              <strong>نام کاربری:</strong> {user.username}
            </p>
            {user.full_name && (
              <p>
                <strong>نام کامل:</strong> {user.full_name}
              </p>
            )}
            <p>
              <strong>وضعیت:</strong> {user.is_active ? 'فعال' : 'غیرفعال'}
            </p>
            <p>
              <strong>نقش:</strong> {user.is_superuser ? 'مدیر' : 'کاربر عادی'}
            </p>
            <br />
            <button 
              onClick={() => router.push('/dashboard/upload')} 
              className="btn btn-primary"
              style={{ width: 'auto', padding: '0.875rem 2rem' }}
            >
              آپلود فایل صوتی
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
