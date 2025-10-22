'use client';

import { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await register({
        email,
        username,
        password,
        full_name: fullName || undefined,
      });
      router.push('/dashboard');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'خطا در ثبت نام. لطفا دوباره تلاش کنید.';
      setError(typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>ثبت نام</h1>
          <p>حساب کاربری جدید ایجاد کنید</p>
        </div>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">ایمیل</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
              placeholder="example@email.com"
            />
          </div>

          <div className="form-group">
            <label htmlFor="username">نام کاربری</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              disabled={loading}
              placeholder="username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="fullName">نام کامل (اختیاری)</label>
            <input
              id="fullName"
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              disabled={loading}
              placeholder="نام و نام خانوادگی"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">رمز عبور</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
              placeholder="••••••••"
              minLength={8}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'در حال ثبت نام...' : 'ثبت نام'}
          </button>
        </form>

        <div className="auth-footer">
          قبلا ثبت نام کرده‌اید؟{' '}
          <Link href="/login">وارد شوید</Link>
        </div>
      </div>
    </div>
  );
}
