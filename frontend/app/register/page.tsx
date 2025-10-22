'use client';

import { useState, FormEvent, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';

interface ValidationErrors {
  email?: string;
  username?: string;
  password?: string;
  confirmPassword?: string;
}

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(0);
  const { register, user } = useAuth();
  const router = useRouter();

  // Redirect if already logged in
  useEffect(() => {
    if (user) {
      router.push('/dashboard');
    }
  }, [user, router]);

  const calculatePasswordStrength = (pwd: string): number => {
    let strength = 0;
    if (pwd.length >= 8) strength += 25;
    if (pwd.length >= 12) strength += 25;
    if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) strength += 25;
    if (/[0-9]/.test(pwd)) strength += 15;
    if (/[^a-zA-Z0-9]/.test(pwd)) strength += 10;
    return Math.min(strength, 100);
  };

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

  const validateUsername = (username: string): string | undefined => {
    if (!username) {
      return 'نام کاربری الزامی است';
    }
    if (username.length < 3) {
      return 'نام کاربری باید حداقل 3 کاراکتر باشد';
    }
    if (!/^[a-zA-Z0-9_]+$/.test(username)) {
      return 'نام کاربری فقط می‌تواند شامل حروف، اعداد و _ باشد';
    }
    return undefined;
  };

  const validatePassword = (password: string): string | undefined => {
    if (!password) {
      return 'رمز عبور الزامی است';
    }
    if (password.length < 8) {
      return 'رمز عبور باید حداقل 8 کاراکتر باشد';
    }
    if (!/(?=.*[a-zA-Z])(?=.*[0-9])/.test(password)) {
      return 'رمز عبور باید شامل حروف و اعداد باشد';
    }
    return undefined;
  };

  const validateConfirmPassword = (confirmPwd: string): string | undefined => {
    if (!confirmPwd) {
      return 'تکرار رمز عبور الزامی است';
    }
    if (confirmPwd !== password) {
      return 'رمز عبور و تکرار آن مطابقت ندارند';
    }
    return undefined;
  };

  const validateForm = (): boolean => {
    const errors: ValidationErrors = {
      email: validateEmail(email),
      username: validateUsername(username),
      password: validatePassword(password),
      confirmPassword: validateConfirmPassword(confirmPassword),
    };

    setValidationErrors(errors);
    return !errors.email && !errors.username && !errors.password && !errors.confirmPassword;
  };

  const handleEmailChange = (value: string) => {
    setEmail(value);
    if (validationErrors.email) {
      setValidationErrors({ ...validationErrors, email: validateEmail(value) });
    }
  };

  const handleUsernameChange = (value: string) => {
    setUsername(value);
    if (validationErrors.username) {
      setValidationErrors({ ...validationErrors, username: validateUsername(value) });
    }
  };

  const handlePasswordChange = (value: string) => {
    setPassword(value);
    setPasswordStrength(calculatePasswordStrength(value));
    if (validationErrors.password) {
      setValidationErrors({ ...validationErrors, password: validatePassword(value) });
    }
    if (confirmPassword && validationErrors.confirmPassword) {
      setValidationErrors({ ...validationErrors, confirmPassword: value !== confirmPassword ? 'رمز عبور و تکرار آن مطابقت ندارند' : undefined });
    }
  };

  const handleConfirmPasswordChange = (value: string) => {
    setConfirmPassword(value);
    if (validationErrors.confirmPassword) {
      setValidationErrors({ ...validationErrors, confirmPassword: validateConfirmPassword(value) });
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
      await register({
        email: email.trim(),
        username: username.trim(),
        password,
        full_name: fullName.trim() || undefined,
      });
      router.push('/dashboard');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'خطا در ثبت نام. لطفا دوباره تلاش کنید.';
      setError(typeof errorMessage === 'string' ? errorMessage : 'خطا در ثبت نام');
    } finally {
      setLoading(false);
    }
  };

  const getPasswordStrengthColor = () => {
    if (passwordStrength < 40) return '#ef4444';
    if (passwordStrength < 70) return '#f59e0b';
    return '#10b981';
  };

  const getPasswordStrengthText = () => {
    if (passwordStrength < 40) return 'ضعیف';
    if (passwordStrength < 70) return 'متوسط';
    return 'قوی';
  };

  return (
    <div className="auth-container">
      <div className="auth-card auth-card-large">
        {/* Back to Home Link */}
        <div className="auth-back-link">
          <Link href="/">← بازگشت به صفحه اصلی</Link>
        </div>

        <div className="auth-header">
          <div className="auth-logo">🚀</div>
          <h1>ثبت نام</h1>
          <p>حساب کاربری جدید ایجاد کنید</p>
        </div>

        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate>
          <div className="form-row">
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
              <label htmlFor="username">نام کاربری *</label>
              <div className="input-wrapper">
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => handleUsernameChange(e.target.value)}
                  onBlur={() => validateUsername(username) && setValidationErrors({ ...validationErrors, username: validateUsername(username) })}
                  disabled={loading}
                  placeholder="username"
                  className={validationErrors.username ? 'input-error' : ''}
                  autoComplete="username"
                />
                <span className="input-icon">👤</span>
              </div>
              {validationErrors.username && (
                <div className="field-error">{validationErrors.username}</div>
              )}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="fullName">نام کامل (اختیاری)</label>
            <div className="input-wrapper">
              <input
                id="fullName"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                disabled={loading}
                placeholder="نام و نام خانوادگی"
                autoComplete="name"
              />
              <span className="input-icon">✍️</span>
            </div>
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
                placeholder="حداقل 8 کاراکتر"
                className={validationErrors.password ? 'input-error' : ''}
                autoComplete="new-password"
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
            {password && (
              <div className="password-strength">
                <div className="password-strength-bar">
                  <div 
                    className="password-strength-fill" 
                    style={{ 
                      width: `${passwordStrength}%`,
                      backgroundColor: getPasswordStrengthColor()
                    }}
                  ></div>
                </div>
                <span 
                  className="password-strength-text"
                  style={{ color: getPasswordStrengthColor() }}
                >
                  {getPasswordStrengthText()}
                </span>
              </div>
            )}
            {validationErrors.password && (
              <div className="field-error">{validationErrors.password}</div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">تکرار رمز عبور *</label>
            <div className="input-wrapper">
              <input
                id="confirmPassword"
                type={showConfirmPassword ? 'text' : 'password'}
                value={confirmPassword}
                onChange={(e) => handleConfirmPasswordChange(e.target.value)}
                onBlur={() => validateConfirmPassword(confirmPassword) && setValidationErrors({ ...validationErrors, confirmPassword: validateConfirmPassword(confirmPassword) })}
                disabled={loading}
                placeholder="تکرار رمز عبور"
                className={validationErrors.confirmPassword ? 'input-error' : ''}
                autoComplete="new-password"
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                tabIndex={-1}
              >
                {showConfirmPassword ? '🙈' : '👁️'}
              </button>
            </div>
            {validationErrors.confirmPassword && (
              <div className="field-error">{validationErrors.confirmPassword}</div>
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
                در حال ثبت نام...
              </>
            ) : (
              'ایجاد حساب کاربری'
            )}
          </button>
        </form>

        <div className="auth-divider">
          <span>یا</span>
        </div>

        <div className="auth-footer">
          <p>
            قبلا ثبت نام کرده‌اید؟{' '}
            <Link href="/login" className="auth-link">
              وارد شوید
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
