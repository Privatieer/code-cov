import { api } from '../../lib/axios';

export interface Attachment {
  id: string;
  filename: string;
  file_url: string;
  file_size_bytes: number;
}

export interface ChecklistItem {
    id: string;
    checklist_id: string;
    content: string;
    is_completed: boolean;
    position: number;
}

export interface Checklist {
    id: string;
    task_id: string;
    title: string;
    items: ChecklistItem[];
}

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: 'todo' | 'in_progress' | 'done';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  due_date?: string;
  tags: string[];
  attachments: Attachment[];
  checklists: Checklist[];
}

export const getTasks = async (filters?: any) => {
  const params = new URLSearchParams();
  if (filters?.status) params.append('status', filters.status);
  if (filters?.priority) params.append('priority', filters.priority);
  
  const response = await api.get('/tasks/', { params });
  return response.data;
};

export const createTask = async (data: any) => {
  const response = await api.post('/tasks/', data);
  return response.data;
};

export const updateTask = async ({ id, data }: { id: string, data: any }) => {
  const response = await api.put(`/tasks/${id}`, data);
  return response.data;
};

export const deleteTask = async (id: string) => {
  const response = await api.delete(`/tasks/${id}`);
  return response.data;
};

// --- Attachment API ---

export const uploadAttachment = async ({ taskId, file }: { taskId: string, file: File }) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post(`/tasks/${taskId}/attachments`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const deleteAttachment = async ({ attachmentId }: { attachmentId: string }) => {
  const response = await api.delete(`/tasks/attachments/${attachmentId}`);
  return response.data;
};

// --- Checklist API ---

export const createChecklist = async ({ taskId, title }: { taskId: string; title: string }) => {
    const response = await api.post(`/tasks/${taskId}/checklists`, { title });
    return response.data;
};

export const deleteChecklist = async (checklistId: string) => {
    const response = await api.delete(`/checklists/${checklistId}`);
    return response.data;
};

export const addChecklistItem = async ({ checklistId, content, position }: { checklistId: string; content: string; position?: number }) => {
    const response = await api.post(`/checklists/${checklistId}/items`, { content, position });
    return response.data;
};

export const updateChecklistItem = async ({ itemId, data }: { itemId: string; data: any }) => {
    const response = await api.put(`/checklist-items/${itemId}`, data);
    return response.data;
};

export const deleteChecklistItem = async (itemId: string) => {
    const response = await api.delete(`/checklist-items/${itemId}`);
    return response.data;
};
