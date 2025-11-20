import { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  Box, Card, CardContent, Typography, Chip, IconButton, 
  Dialog, TextField, MenuItem, Stack, Grid, Button, Link as MuiLink,
  FormControl, InputLabel, Select, CircularProgress, Checkbox
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import EditIcon from '@mui/icons-material/Edit';
import PlaylistAddCheckIcon from '@mui/icons-material/PlaylistAddCheck';
import { 
    getTasks, createTask, deleteTask, uploadAttachment, Task, updateTask, deleteAttachment,
    createChecklist, deleteChecklist, addChecklistItem, updateChecklistItem, deleteChecklistItem, Checklist, ChecklistItem
} from './api';
import { useForm } from 'react-hook-form';
import { motion, AnimatePresence } from 'framer-motion';
import { format } from 'date-fns';
import { useTaskFilters } from '../../lib/store';

const EditTaskDialog = ({ open, onClose, task: initialTask }: { open: boolean; onClose: () => void; task: Task | null }) => {
    const queryClient = useQueryClient();
    const { register, handleSubmit, reset, setValue } = useForm();
    const [newChecklistTitle, setNewChecklistTitle] = useState('');
    const [currentTask, setCurrentTask] = useState<Task | null>(initialTask);

    // Get fresh task data from query cache
    const updateTaskFromCache = async () => {
        if (!initialTask) return;
        
        // Refetch all task queries to get latest data
        await queryClient.refetchQueries({ 
            predicate: (query) => query.queryKey[0] === 'tasks'
        });
        
        // Get updated task from any task query in cache
        const allTaskQueries = queryClient.getQueriesData({ 
            predicate: (query) => query.queryKey[0] === 'tasks' 
        });
        
        for (const [, data] of allTaskQueries) {
            const tasks = data as Task[] | undefined;
            if (tasks) {
                const updated = tasks.find(t => t.id === initialTask.id);
                if (updated) {
                    setCurrentTask(updated);
                    break;
                }
            }
        }
    };

    // Optimistic update helper
    const optimisticallyUpdateTask = (updater: (task: Task) => Task) => {
        if (!currentTask) return;
        setCurrentTask(updater({ ...currentTask }));
    };

    // Checklist mutations with optimistic updates
    const createChecklistMutation = useMutation({
        mutationFn: createChecklist,
        onMutate: async (variables) => {
            // Optimistically add the checklist
            optimisticallyUpdateTask((task) => ({
                ...task,
                checklists: [
                    ...task.checklists,
                    {
                        id: `temp-${Date.now()}`,
                        task_id: task.id,
                        title: variables.title,
                        items: []
                    }
                ]
            }));
        },
        onSuccess: async (data) => {
            // Replace temp checklist with real one
            optimisticallyUpdateTask((task) => ({
                ...task,
                checklists: task.checklists.map(c => 
                    c.id.startsWith('temp-') ? data : c
                )
            }));
            await updateTaskFromCache();
        },
        onError: async () => {
            // Revert on error
            await updateTaskFromCache();
        }
    });

    const deleteChecklistMutation = useMutation({
        mutationFn: deleteChecklist,
        onMutate: async (checklistId) => {
            // Optimistically remove the checklist
            optimisticallyUpdateTask((task) => ({
                ...task,
                checklists: task.checklists.filter(c => c.id !== checklistId)
            }));
        },
        onSuccess: async () => {
            await updateTaskFromCache();
        },
        onError: async () => {
            await updateTaskFromCache();
        }
    });

    const addItemMutation = useMutation({
        mutationFn: addChecklistItem,
        onMutate: async (variables) => {
            // Optimistically add the item
            optimisticallyUpdateTask((task) => ({
                ...task,
                checklists: task.checklists.map(checklist =>
                    checklist.id === variables.checklistId
                        ? {
                            ...checklist,
                            items: [
                                ...checklist.items,
                                {
                                    id: `temp-${Date.now()}`,
                                    checklist_id: variables.checklistId,
                                    content: variables.content,
                                    is_completed: false,
                                    position: variables.position !== undefined ? variables.position : checklist.items.length
                                }
                            ].sort((a, b) => a.position - b.position)
                        }
                        : checklist
                )
            }));
        },
        onSuccess: async (data, variables) => {
            // Replace temp item with real one
            optimisticallyUpdateTask((task) => ({
                ...task,
                checklists: task.checklists.map(checklist =>
                    checklist.id === variables.checklistId
                        ? {
                            ...checklist,
                            items: checklist.items.map(item =>
                                item.id.startsWith('temp-') ? data : item
                            )
                        }
                        : checklist
                )
            }));
            await updateTaskFromCache();
        },
        onError: async () => {
            await updateTaskFromCache();
        }
    });

    const updateItemMutation = useMutation({
        mutationFn: updateChecklistItem,
        onMutate: async (variables) => {
            // Optimistically update the item
            optimisticallyUpdateTask((task) => ({
                ...task,
                checklists: task.checklists.map(checklist => ({
                    ...checklist,
                    items: checklist.items.map(item =>
                        item.id === variables.itemId
                            ? { ...item, ...variables.data }
                            : item
                    )
                }))
            }));
        },
        onSuccess: async () => {
            await updateTaskFromCache();
        },
        onError: async () => {
            await updateTaskFromCache();
        }
    });

    const deleteItemMutation = useMutation({
        mutationFn: deleteChecklistItem,
        onMutate: async (itemId) => {
            // Optimistically remove the item
            optimisticallyUpdateTask((task) => ({
                ...task,
                checklists: task.checklists.map(checklist => ({
                    ...checklist,
                    items: checklist.items.filter(item => item.id !== itemId)
                }))
            }));
        },
        onSuccess: async () => {
            await updateTaskFromCache();
        },
        onError: async () => {
            await updateTaskFromCache();
        }
    });

    // Update currentTask when initialTask prop changes
    useEffect(() => {
        setCurrentTask(initialTask);
    }, [initialTask]);

    useEffect(() => {
        if (currentTask) {
            setValue('title', currentTask.title);
            setValue('description', currentTask.description);
            setValue('priority', currentTask.priority);
            setValue('status', currentTask.status);
            const dueDate = currentTask.due_date ? format(new Date(currentTask.due_date), "yyyy-MM-dd'T'HH:mm") : '';
            setValue('due_date', dueDate);
        }
    }, [currentTask, setValue]);

    const mutation = useMutation({
        mutationFn: (data: any) => updateTask({ id: currentTask!.id, data }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['tasks'] });
            reset();
            onClose();
        },
    });

    const handleAddChecklist = () => {
        if (newChecklistTitle.trim() && currentTask) {
            createChecklistMutation.mutate({ taskId: currentTask.id, title: newChecklistTitle });
            setNewChecklistTitle('');
        }
    };

    const handleAddItem = (checklistId: string, content: string) => {
        if (content.trim() && currentTask) {
            const checklist = currentTask.checklists.find((c: Checklist) => c.id === checklistId);
            if (!checklist || !checklist.items) return;
            
            const maxPosition = checklist.items.length > 0 
                ? Math.max(...checklist.items.map((i: ChecklistItem) => i.position))
                : -1;
            addItemMutation.mutate({ 
                checklistId, 
                content,
                position: maxPosition + 1
            });
        }
    };

    return (
        <Dialog open={open} onClose={onClose} fullWidth maxWidth="md" PaperProps={{ sx: { backdropFilter: 'blur(20px)', backgroundColor: 'rgba(255, 255, 255, 0.9)', borderRadius: 4 } }}>
            <Grid container>
                <Grid item xs={12} md={7} sx={{ p: 4, borderRight: '1px solid rgba(0,0,0,0.1)' }}>
                    <Box component="form" onSubmit={handleSubmit((data: any) => mutation.mutate(data))}>
                        <Typography variant="h5" mb={3} fontWeight="bold">Edit Task</Typography>
                        <Stack spacing={3}>
                            <TextField label="Title" fullWidth {...register('title', { required: true })} variant="outlined" />
                            <TextField label="Description" fullWidth multiline rows={3} {...register('description')} variant="outlined" />
                            <Box>
                                <Grid container spacing={2}>
                                    <Grid item xs={6}>
                                        <TextField 
                                            select 
                                            label="Status" 
                                            value={currentTask?.status || 'todo'}
                                            fullWidth 
                                            {...register('status')} 
                                            variant="outlined"
                                            onChange={(e) => {
                                                setValue('status', e.target.value);
                                                if (currentTask) {
                                                    setCurrentTask({ ...currentTask, status: e.target.value as any });
                                                }
                                            }}
                                        >
                                            {['todo', 'in_progress', 'done'].map(p => (
                                            <MenuItem key={p} value={p}>{p.replace('_', ' ')}</MenuItem>
                                        ))}
                                        </TextField>
                                    </Grid>
                                    <Grid item xs={6}>
                                        <TextField 
                                            select 
                                            label="Priority" 
                                            value={currentTask?.priority || 'medium'}
                                            fullWidth 
                                            {...register('priority')} 
                                            variant="outlined"
                                            onChange={(e) => {
                                                setValue('priority', e.target.value);
                                                if (currentTask) {
                                                    setCurrentTask({ ...currentTask, priority: e.target.value as any });
                                                }
                                            }}
                                        >
                                            {['low', 'medium', 'high', 'urgent'].map(p => (
                                            <MenuItem key={p} value={p}>{p}</MenuItem>
                                        ))}
                                        </TextField>
                                    </Grid>
                                </Grid>
                            </Box>
                            <TextField label="Due Date" type="datetime-local" fullWidth InputLabelProps={{ shrink: true }} {...register('due_date')} variant="outlined" />
                            <Button type="submit" variant="contained" size="large" disabled={mutation.isPending} sx={{ mt: 2 }}>
                                Save Changes
                            </Button>
                        </Stack>
                    </Box>
                </Grid>
                
                <Grid item xs={12} md={5} sx={{ p: 4, bgcolor: 'rgba(0,0,0,0.02)' }}>
                    <Typography variant="h6" mb={2} fontWeight="bold">Checklists</Typography>
                    
                    <Stack direction="row" spacing={1} mb={3}>
                        <TextField 
                            size="small" 
                            placeholder="New Checklist Title" 
                            fullWidth 
                            value={newChecklistTitle}
                            onChange={(e: any) => setNewChecklistTitle(e.target.value)}
                            onKeyDown={(e: any) => {
                                if (e.key === 'Enter' && newChecklistTitle.trim()) {
                                    e.preventDefault();
                                    handleAddChecklist();
                                }
                            }}
                        />
                        <IconButton onClick={handleAddChecklist} color="primary" disabled={!newChecklistTitle.trim()}>
                            <AddIcon />
                        </IconButton>
                    </Stack>

                    <Stack spacing={3} sx={{ maxHeight: '60vh', overflowY: 'auto' }}>
                        {currentTask?.checklists?.map((checklist: Checklist) => (
                            <Box key={checklist.id} sx={{ bgcolor: 'white', p: 2, borderRadius: 2, boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                                <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1}>
                                    <Typography fontWeight="600">{checklist.title}</Typography>
                                    <IconButton size="small" color="error" onClick={() => deleteChecklistMutation.mutate(checklist.id)}>
                                        <DeleteIcon fontSize="small" />
                                    </IconButton>
                                </Stack>
                                
                                <Stack spacing={1}>
                                    {[...checklist.items].sort((a, b) => a.position - b.position).map(item => (
                                        <Stack key={item.id} direction="row" alignItems="center" spacing={1}>
                                            <Checkbox 
                                                checked={item.is_completed} 
                                                onChange={(e: any) => updateItemMutation.mutate({ itemId: item.id, data: { is_completed: e.target.checked } })}
                                                size="small"
                                            />
                                            <Typography 
                                                variant="body2" 
                                                sx={{ 
                                                    flexGrow: 1, 
                                                    textDecoration: item.is_completed ? 'line-through' : 'none',
                                                    color: item.is_completed ? 'text.disabled' : 'text.primary'
                                                }}
                                            >
                                                {item.content}
                                            </Typography>
                                            <IconButton size="small" onClick={() => deleteItemMutation.mutate(item.id)}>
                                                <DeleteIcon fontSize="small" />
                                            </IconButton>
                                        </Stack>
                                    ))}
                                    
                                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                                        <AddIcon fontSize="small" color="action" sx={{ mr: 1 }} />
                                        <TextField 
                                            placeholder="Add item..." 
                                            variant="standard" 
                                            fullWidth 
                                            size="small"
                                            onKeyDown={(e: any) => {
                                                if (e.key === 'Enter') {
                                                    e.preventDefault();
                                                    const target = e.target as HTMLInputElement;
                                                    handleAddItem(checklist.id, target.value);
                                                    target.value = '';
                                                }
                                            }}
                                        />
                                    </Box>
                                </Stack>
                            </Box>
                        ))}
                    </Stack>
                </Grid>
            </Grid>
        </Dialog>
    );
};

interface ChecklistWithItems {
  id: string;
  title: string;
  items: string[];
}

const CreateTaskDialog = ({ open, onClose }: { open: boolean, onClose: () => void }) => {
  const queryClient = useQueryClient();
  const { register, handleSubmit, reset } = useForm();
  const [checklists, setChecklists] = useState<ChecklistWithItems[]>([]);
  const [newChecklistTitle, setNewChecklistTitle] = useState('');
  const checklistsRef = useRef<ChecklistWithItems[]>([]);

  // Keep ref in sync with state
  useEffect(() => {
    checklistsRef.current = checklists;
  }, [checklists]);

  // Set default due date (1 hour from now) when dialog opens
  useEffect(() => {
    if (open) {
      const now = new Date();
      now.setHours(now.getHours() + 1);
      const defaultDueDate = format(now, "yyyy-MM-dd'T'HH:mm");
      reset({
        priority: 'medium',
        due_date: defaultDueDate
      });
      setChecklists([]);
      setNewChecklistTitle('');
    } else {
      reset();
      setChecklists([]);
      setNewChecklistTitle('');
    }
  }, [open, reset]);

  const mutation = useMutation({
    mutationFn: async (data: any) => {
      try {
        // First create the task
        const task = await createTask(data);
        
        // Then create all checklists with their items using the ref to get latest state
        const currentChecklists = checklistsRef.current;
        if (currentChecklists.length > 0) {
          for (const checklist of currentChecklists) {
            const createdChecklist = await createChecklist({ taskId: task.id, title: checklist.title });
            
            // Add items to the checklist
            if (checklist.items.length > 0) {
              await Promise.all(
                checklist.items.map((itemContent, index) =>
                  addChecklistItem({ 
                    checklistId: createdChecklist.id, 
                    content: itemContent,
                    position: index
                  })
                )
              );
            }
          }
        }
        
        return task;
      } catch (error) {
        console.error('Error in mutation:', error);
        throw error;
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      onClose();
    },
    onError: (error: any) => {
      console.error('Error creating task:', error);
      alert(`Failed to create task: ${error?.response?.data?.detail || error?.message || 'Unknown error'}`);
    }
  });

  const handleAddChecklistTitle = () => {
    const trimmed = newChecklistTitle.trim();
    if (trimmed) {
      setChecklists([...checklists, { id: `temp-${Date.now()}`, title: trimmed, items: [] }]);
      setNewChecklistTitle('');
    }
  };

  const handleRemoveChecklist = (checklistId: string) => {
    setChecklists(checklists.filter(c => c.id !== checklistId));
  };

  const handleAddItem = (checklistId: string, content: string) => {
    if (content.trim()) {
      setChecklists(checklists.map(c =>
        c.id === checklistId
          ? { ...c, items: [...c.items, content.trim()] }
          : c
      ));
    }
  };

  const handleRemoveItem = (checklistId: string, itemIndex: number) => {
    setChecklists(checklists.map(c =>
      c.id === checklistId
        ? { ...c, items: c.items.filter((_, i) => i !== itemIndex) }
        : c
    ));
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      fullWidth 
      maxWidth="md"
      PaperProps={{
        sx: {
          backdropFilter: 'blur(20px)',
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          borderRadius: 4
        }
      }}
    >
      <Grid container>
        <Grid item xs={12} md={7} sx={{ p: 4, borderRight: '1px solid rgba(0,0,0,0.1)' }}>
          <Box component="form" onSubmit={handleSubmit((data: any) => mutation.mutate(data))}>
            <Typography variant="h5" mb={3} fontWeight="bold">New Task</Typography>
            <Stack spacing={3}>
              <TextField label="Title" fullWidth {...register('title', { required: true })} variant="outlined" />
              <TextField label="Description" fullWidth multiline rows={3} {...register('description')} variant="outlined" />
              <TextField select label="Priority" defaultValue="medium" fullWidth {...register('priority')} variant="outlined">
                {['low', 'medium', 'high', 'urgent'].map(p => (
                  <MenuItem key={p} value={p}>{p}</MenuItem>
                ))}
              </TextField>
              <TextField 
                label="Due Date" 
                type="datetime-local" 
                fullWidth 
                InputLabelProps={{ shrink: true }} 
                {...register('due_date')} 
                variant="outlined"
              />
              <Button 
                type="submit" 
                variant="contained" 
                size="large"
                disabled={mutation.isPending}
                sx={{ mt: 2 }}
              >
                Create Task
              </Button>
            </Stack>
          </Box>
        </Grid>
        
        <Grid item xs={12} md={5} sx={{ p: 4, bgcolor: 'rgba(0,0,0,0.02)' }}>
          <Typography variant="h6" mb={2} fontWeight="bold">Checklists</Typography>
          
          <Stack direction="row" spacing={1} mb={3}>
            <TextField 
              size="small" 
              placeholder="New Checklist Title" 
              fullWidth 
              value={newChecklistTitle}
              onChange={(e: any) => setNewChecklistTitle(e.target.value)}
              onKeyDown={(e: any) => {
                if (e.key === 'Enter' && newChecklistTitle.trim()) {
                  e.preventDefault();
                  handleAddChecklistTitle();
                }
              }}
            />
            <IconButton onClick={handleAddChecklistTitle} color="primary" disabled={!newChecklistTitle.trim()}>
              <AddIcon />
            </IconButton>
          </Stack>

          <Stack spacing={3} sx={{ maxHeight: '50vh', overflowY: 'auto' }}>
            {checklists.length === 0 ? (
              <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic', p: 1 }}>
                No checklists added yet
              </Typography>
            ) : (
              checklists.map((checklist) => (
                <Box key={checklist.id} sx={{ bgcolor: 'white', p: 2, borderRadius: 2, boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                  <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1}>
                    <Typography fontWeight="600">{checklist.title}</Typography>
                    <IconButton size="small" color="error" onClick={() => handleRemoveChecklist(checklist.id)}>
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Stack>
                  
                  <Stack spacing={1}>
                    {checklist.items.map((item, itemIndex) => (
                      <Stack key={itemIndex} direction="row" alignItems="center" spacing={1}>
                        <Typography variant="body2" sx={{ flexGrow: 1, p: 0.5 }}>
                          • {item}
                        </Typography>
                        <IconButton size="small" onClick={() => handleRemoveItem(checklist.id, itemIndex)}>
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Stack>
                    ))}
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                      <AddIcon fontSize="small" color="action" sx={{ mr: 1 }} />
                      <TextField 
                        placeholder="Add item..." 
                        variant="standard" 
                        fullWidth 
                        size="small"
                        onKeyDown={(e: any) => {
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            const target = e.target as HTMLInputElement;
                            handleAddItem(checklist.id, target.value);
                            target.value = '';
                          }
                        }}
                      />
                    </Box>
                  </Stack>
                </Box>
              ))
            )}
          </Stack>
        </Grid>
      </Grid>
    </Dialog>
  );
};

const TaskCard = ({ task }: { task: Task }) => {
  const queryClient = useQueryClient();
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  const deleteMutation = useMutation({
    mutationFn: deleteTask,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['tasks'] })
  });

  const uploadMutation = useMutation({
    mutationFn: uploadAttachment,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['tasks'] })
  });

  const removeAttachmentMutation = useMutation({
    mutationFn: deleteAttachment,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['tasks'] }),
  });

  const updateStatusMutation = useMutation({
    mutationFn: (status: string) => updateTask({ id: task.id, data: { status } }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['tasks'] })
  });

  const updatePriorityMutation = useMutation({
    mutationFn: (priority: string) => updateTask({ id: task.id, data: { priority } }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['tasks'] })
  });

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      uploadMutation.mutate({ taskId: task.id, file: event.target.files[0] });
    }
  };
  
  // Calculate checklist progress
  const totalItems = task.checklists?.reduce((acc, list) => acc + list.items.length, 0) || 0;
  const completedItems = task.checklists?.reduce((acc, list) => acc + list.items.filter(i => i.is_completed).length, 0) || 0;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ duration: 0.3 }}
    >
      <Card sx={{ mb: 2, overflow: 'visible' }}>
        <CardContent>
          <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
            <Box sx={{ width: '100%' }}>
              <Typography variant="h6" fontWeight="600">{task.title}</Typography>
              <Typography color="text.secondary" gutterBottom sx={{ mt: 1, mb: 2 }}>{task.description}</Typography>
              
              <Stack direction="row" spacing={1} mb={2} flexWrap="wrap" useFlexGap>
                <FormControl size="small" sx={{ minWidth: 100 }}>
                  <Select
                    value={task.status}
                    onChange={(e) => updateStatusMutation.mutate(e.target.value)}
                    sx={{
                      height: 24,
                      fontSize: '0.75rem',
                      '& .MuiSelect-select': {
                        py: 0.5,
                        px: 1
                      }
                    }}
                  >
                    {['todo', 'in_progress', 'done'].map(s => (
                      <MenuItem key={s} value={s} sx={{ fontSize: '0.75rem' }}>
                        {s.replace('_', ' ')}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                <FormControl size="small" sx={{ minWidth: 100 }}>
                  <Select
                    value={task.priority}
                    onChange={(e) => updatePriorityMutation.mutate(e.target.value)}
                    sx={{
                      height: 24,
                      fontSize: '0.75rem',
                      backgroundColor: task.priority === 'urgent' ? '#d32f2f' : 
                                    task.priority === 'high' ? '#ed6c02' : 
                                    task.priority === 'medium' ? '#edb02a' : '#66bb6a',
                      color: 'white',
                      fontWeight: 600,
                      '& .MuiSelect-select': {
                        py: 0.5,
                        px: 1,
                        color: 'white'
                      },
                      '& .MuiOutlinedInput-notchedOutline': {
                        borderColor: 'transparent'
                      },
                      '&:hover .MuiOutlinedInput-notchedOutline': {
                        borderColor: 'rgba(255,255,255,0.5)'
                      },
                      '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                        borderColor: 'white'
                      },
                      '& .MuiSvgIcon-root': {
                        color: 'white'
                      }
                    }}
                  >
                    {['low', 'medium', 'high', 'urgent'].map(p => (
                      <MenuItem key={p} value={p} sx={{ fontSize: '0.75rem' }}>
                        {p}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                {task.checklists && task.checklists.length > 0 && (
                    <Chip 
                        icon={<PlaylistAddCheckIcon />} 
                        label={`${task.checklists.length} checklist${task.checklists.length > 1 ? 's' : ''}`}
                        size="small" 
                        variant="outlined" 
                    />
                )}
                {totalItems > 0 && (
                    <Chip 
                        icon={<PlaylistAddCheckIcon />} 
                        label={`${completedItems}/${totalItems}`} 
                        size="small" 
                        variant="outlined" 
                    />
                )}
              </Stack>

              {/* Attachments Section */}
              <AnimatePresence>
                {task.attachments?.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                  >
                    <Box sx={{ mt: 2, p: 1.5, bgcolor: 'rgba(255,255,255,0.3)', borderRadius: 2 }}>
                      <Typography variant="caption" color="text.secondary" fontWeight="bold">ATTACHMENTS</Typography>
                      <Stack spacing={0.5} mt={1}>
                        {task.attachments.map(att => (
                           <Stack key={att.id} direction="row" alignItems="center" justifyContent="space-between">
                             <MuiLink href={att.file_url} target="_blank" rel="noopener" underline="hover" color="primary" sx={{ display: 'block', flexGrow: 1 }}>
                               📎 {att.filename} ({(att.file_size_bytes / 1024).toFixed(1)} KB)
                             </MuiLink>
                             <IconButton size="small" onClick={() => removeAttachmentMutation.mutate({ attachmentId: att.id })}>
                               <DeleteIcon fontSize="inherit" />
                             </IconButton>
                           </Stack>
                        ))}
                      </Stack>
                    </Box>
                  </motion.div>
                )}
              </AnimatePresence>
            </Box>
            
            <Stack direction="row" spacing={1}>
               <IconButton component="label" size="small" color="primary" sx={{ bgcolor: 'rgba(255,255,255,0.5)' }}>
                  <AttachFileIcon fontSize="small" />
                  <input type="file" hidden onChange={handleFileChange} />
               </IconButton>
               <IconButton onClick={() => setEditingTask(task)} size="small" color="secondary" sx={{ bgcolor: 'rgba(255,255,255,0.5)' }}>
                  <EditIcon fontSize="small" />
               </IconButton>
              <IconButton onClick={() => deleteMutation.mutate(task.id)} size="small" color="error" sx={{ bgcolor: 'rgba(255,0,0,0.1)' }}>
                <DeleteIcon fontSize="small" />
              </IconButton>
            </Stack>
          </Stack>
        </CardContent>
        <EditTaskDialog open={!!editingTask} onClose={() => setEditingTask(null)} task={editingTask} />
      </Card>
    </motion.div>
  );
};

export const TasksPage = () => {
  const [isCreateOpen, setCreateOpen] = useState(false);
  const { filterStatus, filterPriority, setFilterPriority, setFilterStatus } = useTaskFilters();

  const { data: tasks, isLoading, isError } = useQuery({
    queryKey: ['tasks', filterStatus, filterPriority],
    queryFn: () => getTasks({ status: filterStatus || undefined, priority: filterPriority || undefined }),
  });

  if (isLoading) return (
    <Box display="flex" justifyContent="center" mt={10}>
      <CircularProgress />
    </Box>
  );

  if (isError) return <Typography color="error">Failed to load tasks.</Typography>;

  return (
    <Box sx={{ mt: 6, pb: 8 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={5}>
        <Box>
          <Typography variant="h3" fontWeight="800" sx={{ background: 'linear-gradient(45deg, #212121, #424242)', backgroundClip: 'text', color: 'transparent' }}>
            My Tasks
          </Typography>
          <Typography color="text.secondary" mt={1}>Manage your daily goals with focus.</Typography>
        </Box>
        <Button 
          variant="contained" 
          size="large"
          startIcon={<AddIcon />} 
          onClick={() => setCreateOpen(true)}
          sx={{ px: 3, py: 1.5 }}
        >
          New Task
        </Button>
      </Stack>

      {/* Filters */}
      <Stack direction="row" spacing={2} mb={4}>
        <FormControl sx={{ minWidth: 140 }} size="small">
          <InputLabel>Status</InputLabel>
          <Select value={filterStatus} label="Status" onChange={(e: any) => setFilterStatus(e.target.value)}>
            <MenuItem value="">All Statuses</MenuItem>
            <MenuItem value="todo">To Do</MenuItem>
            <MenuItem value="in_progress">In Progress</MenuItem>
            <MenuItem value="done">Done</MenuItem>
          </Select>
        </FormControl>

        <FormControl sx={{ minWidth: 140 }} size="small">
          <InputLabel>Priority</InputLabel>
          <Select value={filterPriority} label="Priority" onChange={(e: any) => setFilterPriority(e.target.value)}>
            <MenuItem value="">All Priorities</MenuItem>
            <MenuItem value="low">Low</MenuItem>
            <MenuItem value="medium">Medium</MenuItem>
            <MenuItem value="high">High</MenuItem>
            <MenuItem value="urgent">Urgent</MenuItem>
          </Select>
        </FormControl>
      </Stack>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <AnimatePresence mode="popLayout">
            {tasks?.map((task: Task) => (
              <TaskCard key={task.id} task={task} />
            ))}
          </AnimatePresence>
          
          {tasks?.length === 0 && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <Typography color="text.secondary" align="center" mt={4} sx={{ fontStyle: 'italic' }}>
                No tasks found. Time to create one! 🚀
              </Typography>
            </motion.div>
          )}
        </Grid>
      </Grid>

      <CreateTaskDialog open={isCreateOpen} onClose={() => setCreateOpen(false)} />
    </Box>
  );
};
