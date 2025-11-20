import { useForm } from 'react-hook-form';
import { useMutation } from '@tanstack/react-query';
import { TextField, Button, Box, Typography, Alert, Link as MuiLink } from '@mui/material';
import { Link, useNavigate } from 'react-router-dom';
import { login } from './api';
import { useAuthStore } from '../../lib/store';

export const LoginPage = () => {
  const { register, handleSubmit } = useForm();
  const navigate = useNavigate();
  const setToken = useAuthStore((state) => state.setToken);
  
  const mutation = useMutation({
    mutationFn: login,
    onSuccess: (data) => {
      setToken(data.access_token);
      navigate('/');
    }
  });

  const onSubmit = (data: any) => {
    mutation.mutate(data);
  };

  return (
    <Box 
      sx={{ 
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }}
    >
      <Box
        sx={{
          width: '100%',
          maxWidth: 400,
          bgcolor: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(20px)',
          borderRadius: 4,
          p: 4,
          boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.37)'
        }}
      >
        <Typography component="h1" variant="h5" align="center" sx={{ mb: 3, fontWeight: 'bold' }}>
          Sign in
        </Typography>
        <Box component="form" onSubmit={handleSubmit(onSubmit)}>
          {mutation.isError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              Invalid credentials
            </Alert>
          )}
          
          <TextField
            margin="normal"
            required
            fullWidth
            label="Email Address"
            autoComplete="email"
            autoFocus
            defaultValue="admin@example.com"
            {...register('email')}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            label="Password"
            type="password"
            autoComplete="current-password"
            defaultValue="admin123"
            {...register('password')}
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2, py: 1.5 }}
            disabled={mutation.isPending}
          >
            {mutation.isPending ? 'Signing in...' : 'Sign In'}
          </Button>
          <Box sx={{ textAlign: 'center' }}>
            <Link to="/register">
              <MuiLink component="span" variant="body2">
                {"Don't have an account? Sign Up"}
              </MuiLink>
            </Link>
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

