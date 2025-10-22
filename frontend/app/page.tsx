'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';

export default function Home() {
  const router = useRouter();
  const { user, loading } = useAuth();

  useEffect(() => {
    if (!loading && user) {
      router.push('/dashboard');
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="loading">
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="landing-page">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <div className="hero-badge">
            <span>🚀 پلتفرم مدیریت وظایف هوشمند</span>
          </div>
          
          <h1 className="hero-title">
            مدیریت وظایف خود را
            <span className="hero-gradient"> ساده و حرفه‌ای </span>
            کنید
          </h1>
          
          <p className="hero-description">
            با استفاده از پلتفرم مدیریت وظایف ما، می‌توانید پروژه‌های خود را به صورت 
            هوشمند سازماندهی کرده، فایل‌ها را آپلود کنید و روند کارها را به صورت 
            لحظه‌ای پیگیری نمایید. یک راه‌حل کامل برای تیم‌های حرفه‌ای.
          </p>

          <div className="hero-cta">
            <Link href="/register" className="btn btn-hero-primary">
              شروع رایگان
            </Link>
            <Link href="/login" className="btn btn-hero-secondary">
              ورود به حساب کاربری
            </Link>
          </div>

          <div className="hero-stats">
            <div className="stat-item">
              <div className="stat-number">1000+</div>
              <div className="stat-label">کاربر فعال</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">10K+</div>
              <div className="stat-label">وظیفه انجام شده</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">99.9%</div>
              <div className="stat-label">آپتایم سیستم</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="features-container">
          <div className="section-header">
            <h2 className="section-title">ویژگی‌های برجسته</h2>
            <p className="section-description">
              همه چیزهایی که برای مدیریت بهتر پروژه‌هایتان نیاز دارید
            </p>
          </div>

          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">📁</div>
              <h3 className="feature-title">آپلود و مدیریت فایل</h3>
              <p className="feature-description">
                فایل‌های خود را به راحتی آپلود کرده و به صورت امن ذخیره کنید.
                پشتیبانی از انواع فرمت‌های مختلف فایل.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3 className="feature-title">پردازش سریع</h3>
              <p className="feature-description">
                وظایف شما با استفاده از سیستم صف‌بندی پیشرفته به صورت 
                موازی و با سرعت بالا پردازش می‌شوند.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">🔐</div>
              <h3 className="feature-title">امنیت بالا</h3>
              <p className="feature-description">
                احراز هویت پیشرفته، رمزگذاری داده‌ها و سطوح دسترسی 
                امنیت اطلاعات شما را تضمین می‌کند.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3 className="feature-title">پیگیری لحظه‌ای</h3>
              <p className="feature-description">
                وضعیت وظایف خود را به صورت زنده مشاهده کنید و از 
                پیشرفت کار خود مطلع شوید.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">🎯</div>
              <h3 className="feature-title">رابط کاربری ساده</h3>
              <p className="feature-description">
                طراحی مدرن و کاربرپسند که استفاده از سیستم را برای 
                همه افراد آسان می‌کند.
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">🔄</div>
              <h3 className="feature-title">همگام‌سازی خودکار</h3>
              <p className="feature-description">
                تمام تغییرات به صورت خودکار در تمام دستگاه‌ها 
                همگام‌سازی می‌شوند.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works-section">
        <div className="features-container">
          <div className="section-header">
            <h2 className="section-title">نحوه استفاده</h2>
            <p className="section-description">
              در سه مرحله ساده شروع به کار کنید
            </p>
          </div>

          <div className="steps-grid">
            <div className="step-card">
              <div className="step-number">1</div>
              <h3 className="step-title">ثبت نام کنید</h3>
              <p className="step-description">
                با چند کلیک ساده حساب کاربری خود را ایجاد کنید
              </p>
            </div>

            <div className="step-card">
              <div className="step-number">2</div>
              <h3 className="step-title">فایل آپلود کنید</h3>
              <p className="step-description">
                فایل‌های مورد نظر خود را آپلود و وظایف را تعریف کنید
              </p>
            </div>

            <div className="step-card">
              <div className="step-number">3</div>
              <h3 className="step-title">نتایج را دریافت کنید</h3>
              <p className="step-description">
                پیشرفت را پیگیری کرده و نتایج را مشاهده کنید
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-content">
          <h2 className="cta-title">آماده شروع هستید؟</h2>
          <p className="cta-description">
            همین حالا به جمع هزاران کاربر راضی ما بپیوندید و تجربه 
            مدیریت وظایف حرفه‌ای را آغاز کنید.
          </p>
          <div className="cta-buttons">
            <Link href="/register" className="btn btn-cta-primary">
              ثبت نام رایگان
            </Link>
            <Link href="/login" className="btn btn-cta-secondary">
              ورود
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="footer-content">
          <p>© 2025 سیستم مدیریت وظایف. تمامی حقوق محفوظ است.</p>
          <div className="footer-links">
            <a href="#">درباره ما</a>
            <a href="#">تماس با ما</a>
            <a href="#">حریم خصوصی</a>
            <a href="#">شرایط استفاده</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
