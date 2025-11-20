import { Box, Typography, Drawer, List, ListItem, ListItemButton, ListItemText, Toolbar, Divider } from '@mui/material';
import { useTaskFilters } from '../../lib/store';

const drawerWidth = 240;

export const TaskListSidebar = () => {
    const { filterStatus, setFilterStatus } = useTaskFilters();

    return (
        <Drawer
            variant="permanent"
            sx={{
                width: drawerWidth,
                flexShrink: 0,
                [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box', background: 'rgba(255, 255, 255, 0.2)', backdropFilter: 'blur(20px)', borderRight: '1px solid rgba(255, 255, 255, 0.3)' },
            }}
        >
            <Toolbar />
            <Box sx={{ overflow: 'auto', p: 1 }}>
                <Typography variant="overline" sx={{ p: 2, display: 'block' }}>Filters</Typography>
                <List>
                    <ListItem disablePadding>
                        <ListItemButton selected={filterStatus === ''} onClick={() => setFilterStatus('')}>
                            <ListItemText primary="All Tasks" />
                        </ListItemButton>
                    </ListItem>
                    <Divider sx={{ my: 1 }} />
                    <ListItem disablePadding>
                        <ListItemButton selected={filterStatus === 'todo'} onClick={() => setFilterStatus('todo')}>
                            <ListItemText primary="To Do" />
                        </ListItemButton>
                    </ListItem>
                    <ListItem disablePadding>
                        <ListItemButton selected={filterStatus === 'in_progress'} onClick={() => setFilterStatus('in_progress')}>
                            <ListItemText primary="In Progress" />
                        </ListItemButton>
                    </ListItem>
                    <ListItem disablePadding>
                        <ListItemButton selected={filterStatus === 'done'} onClick={() => setFilterStatus('done')}>
                            <ListItemText primary="Done" />
                        </ListItemButton>
                    </ListItem>
                </List>
            </Box>
        </Drawer>
    );
};
