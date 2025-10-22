'use client';

import { useRouter, useParams } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import useSWR from 'swr';
import api from '@/lib/api';
import { Task, TaskStatus } from '@/types/task';
import { useState, useEffect } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Typography from '@tiptap/extension-typography';
import Placeholder from '@tiptap/extension-placeholder';
import jsPDF from 'jspdf';
import './editor.css';

const fetcher = (url: string) => api.get(url).then(res => res.data);

interface TranscriptionResult {
  transcription: string;
  language?: string;
  duration?: number;
  confidence?: number;
  timestamp?: string;
  source_file?: string;
  model_config?: {
    name?: string;
    device?: string;
    compute_type?: string;
  };
}

export default function TaskDetailPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const params = useParams();
  const taskId = params.taskId as string;
  
  const [transcriptionData, setTranscriptionData] = useState<TranscriptionResult | null>(null);
  const [loadingTranscription, setLoadingTranscription] = useState(false);
  const [editorContent, setEditorContent] = useState('');
  const [isEdited, setIsEdited] = useState(false);
  
  // Fetch task details with polling
  const { data: task, error, isLoading, mutate } = useSWR<Task>(
    user && taskId ? `/api/v1/tasks/${taskId}` : null,
    fetcher,
    {
      refreshInterval: 10000, // Poll every 10 seconds
      revalidateOnFocus: true,
    }
  );

  // Initialize Tiptap editor
  const editor = useEditor({
    extensions: [
      StarterKit,
      Typography,
      Placeholder.configure({
        placeholder: 'متن رونویسی در اینجا نمایش داده می‌شود...',
      }),
    ],
    content: editorContent,
    editorProps: {
      attributes: {
        class: 'prose prose-sm sm:prose lg:prose-lg xl:prose-2xl focus:outline-none',
      },
    },
    onUpdate: ({ editor }) => {
      const newContent = editor.getText();
      if (newContent !== editorContent) {
        setIsEdited(true);
      }
    },
  });

  // Fetch transcription result when task is completed
  useEffect(() => {
    const fetchTranscription = async () => {
      if (task?.status === TaskStatus.COMPLETED && task?.result_path) {
        setLoadingTranscription(true);
        try {
          // Try to fetch the transcription result file
          const response = await api.get(`/api/v1/tasks/${taskId}/result`);
          setTranscriptionData(response.data);
          const text = response.data.transcription || '';
          setEditorContent(text);
          editor?.commands.setContent(`<p>${text}</p>`);
        } catch (err) {
          console.error('Failed to fetch transcription:', err);
          // If API endpoint doesn't exist, show placeholder
          const placeholderText = 'نتیجه رونویسی در اینجا نمایش داده خواهد شد.';
          setEditorContent(placeholderText);
          editor?.commands.setContent(`<p>${placeholderText}</p>`);
        } finally {
          setLoadingTranscription(false);
        }
      }
    };

    fetchTranscription();
  }, [task, taskId, editor]);

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

  const calculateProcessingTime = () => {
    if (!task?.created_at || !task?.completed_at) return null;
    
    const start = new Date(task.created_at).getTime();
    const end = new Date(task.completed_at).getTime();
    const diffMs = end - start;
    
    const seconds = Math.floor(diffMs / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    if (hours > 0) {
      return `${hours} ساعت و ${minutes % 60} دقیقه`;
    } else if (minutes > 0) {
      return `${minutes} دقیقه و ${seconds % 60} ثانیه`;
    } else {
      return `${seconds} ثانیه`;
    }
  };

  const handleSaveLocal = () => {
    if (editor) {
      const content = editor.getText();
      setEditorContent(content);
      setIsEdited(false);
      // Here you could also save to localStorage if needed
      localStorage.setItem(`task_${taskId}_content`, content);
      alert('تغییرات به صورت محلی ذخیره شد');
    }
  };

  const handleDownloadMarkdown = () => {
    if (!editor) return;
    
    const content = editor.getText();
    const markdown = `# ${task?.title || 'رونویسی صوتی'}\n\n${content}`;
    
    const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `transcription_${taskId}.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleDownloadPDF = () => {
    if (!editor) return;
    
    const content = editor.getText();
    const doc = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4',
    });
    
    // Add Persian font support (this is a basic implementation)
    doc.setFont('helvetica');
    doc.setFontSize(16);
    doc.text(task?.title || 'رونویسی صوتی', 105, 20, { align: 'center' });
    
    doc.setFontSize(12);
    const lines = doc.splitTextToSize(content, 170);
    doc.text(lines, 20, 40);
    
    doc.save(`transcription_${taskId}.pdf`);
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
    <div className="container">
      <div className="page-header">
        <div className="page-header-content">
          <div>
            <h1 className="page-title">جزئیات وظیفه</h1>
            <p className="page-subtitle">مشاهده و ویرایش اطلاعات وظیفه</p>
          </div>
          <button 
            onClick={() => router.push('/dashboard')} 
            className="btn-back"
          >
            ← بازگشت به داشبورد
          </button>
        </div>
      </div>

      <div className="page-content">
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
            <>
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

                {/* Metadata Section */}
                <div className="task-detail-section">
                  <h3>اطلاعات پردازش</h3>
                  <div className="metadata-grid">
                    <div className="metadata-item">
                      <span className="metadata-label">وضعیت:</span>
                      <span className="metadata-value">{getStatusText(task.status)}</span>
                    </div>
                    <div className="metadata-item">
                      <span className="metadata-label">ایجاد شده:</span>
                      <span className="metadata-value">{formatDate(task.created_at)}</span>
                    </div>
                    <div className="metadata-item">
                      <span className="metadata-label">آخرین بروزرسانی:</span>
                      <span className="metadata-value">{formatDate(task.updated_at)}</span>
                    </div>
                    {task.completed_at && (
                      <>
                        <div className="metadata-item">
                          <span className="metadata-label">تکمیل شده:</span>
                          <span className="metadata-value">{formatDate(task.completed_at)}</span>
                        </div>
                        <div className="metadata-item">
                          <span className="metadata-label">زمان پردازش:</span>
                          <span className="metadata-value">{calculateProcessingTime()}</span>
                        </div>
                      </>
                    )}
                    {transcriptionData?.duration && (
                      <div className="metadata-item">
                        <span className="metadata-label">مدت زمان صوت:</span>
                        <span className="metadata-value">{transcriptionData.duration} ثانیه</span>
                      </div>
                    )}
                    {transcriptionData?.language && (
                      <div className="metadata-item">
                        <span className="metadata-label">زبان:</span>
                        <span className="metadata-value">{transcriptionData.language}</span>
                      </div>
                    )}
                    {transcriptionData?.confidence && (
                      <div className="metadata-item">
                        <span className="metadata-label">اطمینان:</span>
                        <span className="metadata-value">{(transcriptionData.confidence * 100).toFixed(1)}%</span>
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
              </div>

              {/* Editor Section */}
              {task.status === TaskStatus.COMPLETED && task.result_path && (
                <div className="card" style={{ marginTop: '1.5rem' }}>
                  <div className="task-detail-section">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                      <h3>متن رونویسی</h3>
                      {isEdited && (
                        <span style={{ color: '#f59e0b', fontSize: '0.9rem' }}>
                          ⚠️ تغییرات ذخیره نشده
                        </span>
                      )}
                    </div>

                    {loadingTranscription ? (
                      <div style={{ textAlign: 'center', padding: '2rem', color: '#718096' }}>
                        در حال بارگذاری متن رونویسی...
                      </div>
                    ) : (
                      <>
                        {/* Editor Toolbar */}
                        <div className="editor-toolbar">
                          <button
                            onClick={() => editor?.chain().focus().toggleBold().run()}
                            className={editor?.isActive('bold') ? 'is-active' : ''}
                            title="Bold"
                          >
                            <strong>B</strong>
                          </button>
                          <button
                            onClick={() => editor?.chain().focus().toggleItalic().run()}
                            className={editor?.isActive('italic') ? 'is-active' : ''}
                            title="Italic"
                          >
                            <em>I</em>
                          </button>
                          <button
                            onClick={() => editor?.chain().focus().toggleStrike().run()}
                            className={editor?.isActive('strike') ? 'is-active' : ''}
                            title="Strikethrough"
                          >
                            <s>S</s>
                          </button>
                          <span className="separator"></span>
                          <button
                            onClick={() => editor?.chain().focus().toggleHeading({ level: 1 }).run()}
                            className={editor?.isActive('heading', { level: 1 }) ? 'is-active' : ''}
                            title="Heading 1"
                          >
                            H1
                          </button>
                          <button
                            onClick={() => editor?.chain().focus().toggleHeading({ level: 2 }).run()}
                            className={editor?.isActive('heading', { level: 2 }) ? 'is-active' : ''}
                            title="Heading 2"
                          >
                            H2
                          </button>
                          <button
                            onClick={() => editor?.chain().focus().toggleBulletList().run()}
                            className={editor?.isActive('bulletList') ? 'is-active' : ''}
                            title="Bullet List"
                          >
                            •••
                          </button>
                          <button
                            onClick={() => editor?.chain().focus().toggleOrderedList().run()}
                            className={editor?.isActive('orderedList') ? 'is-active' : ''}
                            title="Ordered List"
                          >
                            123
                          </button>
                          <span className="separator"></span>
                          <button
                            onClick={() => editor?.chain().focus().undo().run()}
                            disabled={!editor?.can().undo()}
                            title="Undo"
                          >
                            ↶
                          </button>
                          <button
                            onClick={() => editor?.chain().focus().redo().run()}
                            disabled={!editor?.can().redo()}
                            title="Redo"
                          >
                            ↷
                          </button>
                        </div>

                        {/* Editor Content */}
                        <div className="editor-wrapper">
                          <EditorContent editor={editor} />
                        </div>

                        {/* Action Buttons */}
                        <div style={{ marginTop: '1rem', display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                          <button 
                            onClick={handleSaveLocal}
                            className="btn btn-primary"
                            disabled={!isEdited}
                          >
                            💾 ذخیره محلی
                          </button>
                          <button 
                            onClick={handleDownloadMarkdown}
                            className="btn btn-secondary"
                          >
                            ⬇️ دانلود Markdown
                          </button>
                          <button 
                            onClick={handleDownloadPDF}
                            className="btn btn-secondary"
                          >
                            📄 دانلود PDF
                          </button>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              )}

              {/* Existing sections */}
              <div className="card" style={{ marginTop: '1.5rem' }}>
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
                </div>
              </div>
            </>
          )}
        </div>
      </div>
  );
}
