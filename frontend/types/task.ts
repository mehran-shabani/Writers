/**
 * @enum {string}
 * @description Represents the status of a task.
 */
export enum TaskStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

/**
 * @interface Task
 * @description Represents a task object.
 */
export interface Task {
  id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  user_id: string;
  file_path: string | null;
  result_path: string | null;
  due_date: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

/**
 * @interface TaskListResponse
 * @description Represents the response for a list of tasks.
 */
export interface TaskListResponse {
  tasks: Task[];
  total: number;
}
