/**
 * Unit tests for TasksPage component
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '../../../test/utils';
import { TasksPage } from '../TasksPage';
import * as api from '../api';

// Mock the API module
vi.mock('../api', () => ({
  getTasks: vi.fn(),
  createTask: vi.fn(),
  updateTask: vi.fn(),
  deleteTask: vi.fn(),
  uploadAttachment: vi.fn(),
  deleteAttachment: vi.fn(),
  createChecklist: vi.fn(),
  deleteChecklist: vi.fn(),
  addChecklistItem: vi.fn(),
  updateChecklistItem: vi.fn(),
  deleteChecklistItem: vi.fn(),
}));

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

describe('TasksPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading state initially', async () => {
    vi.mocked(api.getTasks).mockResolvedValue([]);

    render(<TasksPage />);

    // Check for loading indicator or empty state
    await waitFor(() => {
      expect(api.getTasks).toHaveBeenCalled();
    });
  });

  it('displays tasks when loaded', async () => {
    const mockTasks = [
      {
        id: '1',
        title: 'Test Task',
        description: 'Test Description',
        status: 'todo' as const,
        priority: 'medium' as const,
        tags: [],
        attachments: [],
        checklists: [],
      },
    ];

    vi.mocked(api.getTasks).mockResolvedValue(mockTasks);

    render(<TasksPage />);

    await waitFor(() => {
      expect(screen.getByText('Test Task')).toBeInTheDocument();
      expect(screen.getByText('Test Description')).toBeInTheDocument();
    });
  });

  it('displays task status and priority', async () => {
    const mockTasks = [
      {
        id: '1',
        title: 'Test Task',
        description: 'Test Description',
        status: 'in_progress' as const,
        priority: 'high' as const,
        tags: [],
        attachments: [],
        checklists: [],
      },
    ];

    vi.mocked(api.getTasks).mockResolvedValue(mockTasks);

    render(<TasksPage />);

    await waitFor(() => {
      expect(screen.getByText('in progress')).toBeInTheDocument();
      expect(screen.getByText('high')).toBeInTheDocument();
    });
  });

  it('displays checklist count when tasks have checklists', async () => {
    const mockTasks = [
      {
        id: '1',
        title: 'Test Task',
        description: 'Test Description',
        status: 'todo' as const,
        priority: 'medium' as const,
        tags: [],
        attachments: [],
        checklists: [
          {
            id: 'c1',
            task_id: '1',
            title: 'Checklist 1',
            items: [],
          },
          {
            id: 'c2',
            task_id: '1',
            title: 'Checklist 2',
            items: [],
          },
        ],
      },
    ];

    vi.mocked(api.getTasks).mockResolvedValue(mockTasks);

    render(<TasksPage />);

    await waitFor(() => {
      expect(screen.getByText(/2 checklist/i)).toBeInTheDocument();
    });
  });
});

