import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Container, AppBar, Toolbar, Typography, Button, Box } from '@mui/material';

import { LoginPage } from './features/auth/LoginPage';
import { RegisterPage } from './features/auth/RegisterPage';
import { VerifyEmailPage } from './features/auth/VerifyEmailPage';
import { TasksPage } from './features/tasks/TasksPage';
import { TaskListSidebar } from './features/tasks/TaskListSidebar';

function App() {
  const isAuthenticated = !!localStorage.getItem('token');

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/verify" element={<VerifyEmailPage />} />
        <Route 
          path="/*" 
          element={isAuthenticated ? <MainApp /> : <Navigate to="/login" />} 
        />
      </Routes>
    </BrowserRouter>
  );
}

const MainApp = () => (
  <Box sx={{ display: 'flex' }}>
    <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Task Tracker
        </Typography>
        <Button color="inherit" onClick={() => {
          localStorage.removeItem('token');
          window.location.href = '/login';
        }}>Logout</Button>
      </Toolbar>
    </AppBar>
    <TaskListSidebar />
    <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
      <Toolbar />
      <Container maxWidth="lg">
        <Routes>
          <Route path="/" element={<TasksPage />} />
          {/* Add other main app routes here */}
        </Routes>
      </Container>
    </Box>
  </Box>
);

export default App;

