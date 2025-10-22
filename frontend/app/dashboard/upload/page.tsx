'use client';

import { useState, useRef, DragEvent, ChangeEvent } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import api from '@/lib/api';

interface UploadStatus {
  state: 'idle' | 'uploading' | 'success' | 'error';
  message?: string;
  progress?: number;
}

const ACCEPTED_AUDIO_TYPES = [
  'audio/mpeg',
  'audio/mp3',
  'audio/wav',
  'audio/wave',
  'audio/x-wav',
  'audio/aac',
  'audio/m4a',
  'audio/x-m4a',
  'audio/ogg',
  'audio/flac',
];

const ACCEPTED_EXTENSIONS = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac'];
const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB

export default function UploadPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>({ state: 'idle' });
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  const validateFile = (file: File): string | null => {
    // Check file type
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    const isValidType = ACCEPTED_AUDIO_TYPES.includes(file.type) || 
                        ACCEPTED_EXTENSIONS.includes(fileExtension || '');
    
    if (!isValidType) {
      return 'فقط فایل‌های صوتی (MP3, WAV, M4A, AAC, OGG, FLAC) مجاز هستند.';
    }

    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      const maxSizeMB = MAX_FILE_SIZE / (1024 * 1024);
      return `حجم فایل نباید بیشتر از ${maxSizeMB}MB باشد.`;
    }

    return null;
  };

  const handleFileSelect = (file: File) => {
    const error = validateFile(file);
    if (error) {
      setUploadStatus({ state: 'error', message: error });
      return;
    }

    setSelectedFile(file);
    setUploadStatus({ state: 'idle' });
    
    // Auto-fill title from filename if empty
    if (!title) {
      const fileName = file.name.replace(/\.[^/.]+$/, ''); // Remove extension
      setTitle(fileName);
    }
  };

  const handleDragEnter = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleFileInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus({ state: 'error', message: 'لطفاً یک فایل انتخاب کنید.' });
      return;
    }

    if (!title.trim()) {
      setUploadStatus({ state: 'error', message: 'لطفاً عنوان را وارد کنید.' });
      return;
    }

    setUploadStatus({ state: 'uploading', progress: 0 });

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('title', title.trim());
      if (description.trim()) {
        formData.append('description', description.trim());
      }

      const response = await api.post('/api/v1/tasks', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            setUploadStatus({ state: 'uploading', progress: percentCompleted });
          }
        },
      });

      setUploadStatus({
        state: 'success',
        message: 'فایل با موفقیت آپلود شد و در حال پردازش است.',
      });

      // Redirect to task details or dashboard after 2 seconds
      setTimeout(() => {
        if (response.data?.id) {
          router.push(`/dashboard`); // or `/dashboard/tasks/${response.data.id}` for details page
        } else {
          router.push('/dashboard');
        }
      }, 2000);
    } catch (error: any) {
      console.error('Upload error:', error);
      const errorMessage = error.response?.data?.detail || 'خطا در آپلود فایل. لطفاً دوباره تلاش کنید.';
      setUploadStatus({ state: 'error', message: errorMessage });
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setTitle('');
    setDescription('');
    setUploadStatus({ state: 'idle' });
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  if (authLoading) {
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
    <div className="container">
      <div className="page-header">
        <div className="page-header-content">
          <div>
            <h1 className="page-title">آپلود فایل صوتی</h1>
            <p className="page-subtitle">فایل صوتی خود را برای پردازش آپلود کنید</p>
          </div>
          <button onClick={() => router.push('/dashboard')} className="btn-back">
            ← بازگشت به داشبورد
          </button>
        </div>
      </div>

      <div className="page-content">
          <div className="upload-card">
            {/* Dropzone */}
            <div
              className={`dropzone ${isDragging ? 'dragging' : ''} ${
                selectedFile ? 'has-file' : ''
              }`}
              onDragEnter={handleDragEnter}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept={ACCEPTED_EXTENSIONS.join(',')}
                onChange={handleFileInputChange}
                style={{ display: 'none' }}
                disabled={uploadStatus.state === 'uploading'}
              />

              {!selectedFile ? (
                <div className="dropzone-content">
                  <div className="dropzone-icon">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      width="48"
                      height="48"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                      />
                    </svg>
                  </div>
                  <p className="dropzone-title">
                    فایل صوتی را اینجا بکشید و رها کنید
                  </p>
                  <p className="dropzone-subtitle">یا کلیک کنید تا فایل را انتخاب کنید</p>
                  <p className="dropzone-info">
                    فرمت‌های مجاز: MP3, WAV, M4A, AAC, OGG, FLAC (حداکثر 100MB)
                  </p>
                </div>
              ) : (
                <div className="file-info">
                  <div className="file-icon">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      width="40"
                      height="40"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"
                      />
                    </svg>
                  </div>
                  <div className="file-details">
                    <p className="file-name">{selectedFile.name}</p>
                    <p className="file-size">
                      {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                  </div>
                  {uploadStatus.state !== 'uploading' && (
                    <button
                      className="btn-remove"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleReset();
                      }}
                    >
                      حذف
                    </button>
                  )}
                </div>
              )}
            </div>

            {/* Status Messages */}
            {uploadStatus.state === 'error' && uploadStatus.message && (
              <div className="error-message">{uploadStatus.message}</div>
            )}

            {uploadStatus.state === 'success' && uploadStatus.message && (
              <div className="success-message">{uploadStatus.message}</div>
            )}

            {uploadStatus.state === 'uploading' && (
              <div className="upload-progress">
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${uploadStatus.progress || 0}%` }}
                  />
                </div>
                <p className="progress-text">
                  در حال آپلود... {uploadStatus.progress || 0}%
                </p>
              </div>
            )}

            {/* Form Fields */}
            {selectedFile && uploadStatus.state !== 'success' && (
              <div className="upload-form">
                <div className="form-group">
                  <label htmlFor="title">عنوان *</label>
                  <input
                    id="title"
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="عنوان فایل صوتی"
                    disabled={uploadStatus.state === 'uploading'}
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="description">توضیحات (اختیاری)</label>
                  <textarea
                    id="description"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="توضیحات اضافی در مورد فایل صوتی"
                    disabled={uploadStatus.state === 'uploading'}
                    rows={4}
                  />
                </div>

                <div className="upload-actions">
                  <button
                    className="btn btn-primary"
                    onClick={handleUpload}
                    disabled={uploadStatus.state === 'uploading' || !title.trim()}
                  >
                    {uploadStatus.state === 'uploading' ? 'در حال آپلود...' : 'آپلود فایل'}
                  </button>
                  <button
                    className="btn btn-secondary"
                    onClick={handleReset}
                    disabled={uploadStatus.state === 'uploading'}
                  >
                    لغو
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
  );
}
