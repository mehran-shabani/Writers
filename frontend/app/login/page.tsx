'use client';

import { useState, FormEvent, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';

interface ValidationErrors {
  email?: string;
  password?: string;
}

function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const { login, user } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  // Redirect if already logged in
  useEffect(() => {
    if (user) {
      router.push('/dashboard');
    }
  }, [user, router]);

  const validateEmail = (email: string): string | undefined => {
    if (!email) {
      return 'ایمیل الزامی است';
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return 'فرمت ایمیل صحیح نیست';
    }
    return undefined;
  };

  const validatePassword = (password: string): string | undefined => {
    if (!password) {
      return 'رمز عبور الزامی است';
    }
    if (password.length < 6) {
      return 'رمز عبور باید حداقل 6 کاراکتر باشد';
    }
    return undefined;
  };

  const validateForm = (): boolean => {
    const errors: ValidationErrors = {
      email: validateEmail(email),
      password: validatePassword(password),
    };

    setValidationErrors(errors);
    return !errors.email && !errors.password;
  };

  const handleEmailChange = (value: string) => {
    setEmail(value);
    if (validationErrors.email) {
      setValidationErrors({ ...validationErrors, email: validateEmail(value) });
    }
  };

  const handlePasswordChange = (value: string) => {
    setPassword(value);
    if (validationErrors.password) {
      setValidationErrors({ ...validationErrors, password: validatePassword(value) });
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      await login({ email: email.trim(), password });
      
      // Check for redirect parameter
      const redirectTo = searchParams?.get('redirect') || '/dashboard';
      router.push(redirectTo);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'خطا در ورود. لطفا اطلاعات خود را بررسی کنید.';
      setError(typeof errorMessage === 'string' ? errorMessage : 'خطا در ورود به سیستم');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        {/* Back to Home Link */}
        <div className="auth-back-link">
          <Link href="/">← بازگشت به صفحه اصلی</Link>
        </div>

        <div className="auth-header">
          <div className="auth-logo">🚀</div>
          <h1>خوش آمدید</h1>
          <p>وارد حساب کاربری خود شوید</p>
        </div>

        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate>
          <div className="form-group">
            <label htmlFor="email">ایمیل *</label>
            <div className="input-wrapper">
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => handleEmailChange(e.target.value)}
                onBlur={() => validateEmail(email) && setValidationErrors({ ...validationErrors, email: validateEmail(email) })}
                disabled={loading}
                placeholder="example@email.com"
                className={validationErrors.email ? 'input-error' : ''}
                autoComplete="email"
              />
              <span className="input-icon">📧</span>
            </div>
            {validationErrors.email && (
              <div className="field-error">{validationErrors.email}</div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="password">رمز عبور *</label>
            <div className="input-wrapper">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => handlePasswordChange(e.target.value)}
                onBlur={() => validatePassword(password) && setValidationErrors({ ...validationErrors, password: validatePassword(password) })}
                disabled={loading}
                placeholder="••••••••"
                className={validationErrors.password ? 'input-error' : ''}
                autoComplete="current-password"
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                tabIndex={-1}
              >
                {showPassword ? '🙈' : '👁️'}
              </button>
            </div>
            {validationErrors.password && (
              <div className="field-error">{validationErrors.password}</div>
            )}
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-submit"
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                در حال ورود...
              </>
            ) : (
              'ورود به سیستم'
            )}
          </button>
        </form>

        <div className="auth-divider">
          <span>یا</span>
        </div>

        <div className="auth-footer">
          <p>
            حساب کاربری ندارید؟{' '}
            <Link href="/register" className="auth-link">
              ثبت نام کنید
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="auth-container">
        <div className="loading">
          <div className="spinner-large"></div>
          <p>در حال بارگذاری...</p>
        </div>
      </div>
    }>
      <LoginForm />
    </Suspense>
  );
}
