'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    }
  }, [user, loading, router]);

  const handleLogout = async () => {
    try {
      await logout();
      router.push('/');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner-large"></div>
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
          <div className="header-left">
            <div className="logo">
              <span className="logo-icon">🚀</span>
              <span className="logo-text">مدیریت وظایف</span>
            </div>
            <nav className="nav-menu">
              <a href="/dashboard" className="nav-link">
                داشبورد
              </a>
              <a href="/dashboard/upload" className="nav-link">
                آپلود جدید
              </a>
            </nav>
          </div>

          <div className="user-info">
            <div className="user-profile">
              <div className="user-avatar">
                {user.full_name?.[0] || user.username[0].toUpperCase()}
              </div>
              <div className="user-details">
                <div className="user-name">{user.full_name || user.username}</div>
                <div className="user-email">{user.email}</div>
              </div>
            </div>
            <button onClick={handleLogout} className="btn-logout">
              خروج
            </button>
          </div>
        </div>
      </header>

      <main className="dashboard-content">
        {children}
      </main>

      <footer className="dashboard-footer">
        <div className="container">
          <p>© 2025 سیستم مدیریت وظایف. تمامی حقوق محفوظ است.</p>
        </div>
      </footer>
    </div>
  );
}
