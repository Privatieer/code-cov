import { useForm } from 'react-hook-form';
import { useMutation } from '@tanstack/react-query';
import { TextField, Button, Box, Typography, Alert, Link as MuiLink } from '@mui/material';
import { Link, useNavigate } from 'react-router-dom';
import { register as registerUser } from './api';

export const RegisterPage = () => {
  const navigate = useNavigate();
  const { register, handleSubmit, formState: { errors } } = useForm();
  
  const mutation = useMutation({
    mutationFn: registerUser,
    onSuccess: () => {
      navigate('/login');
    }
  });

  const onSubmit = (data: any) => {
    mutation.mutate(data);
  };

  return (
    <Box sx={{ mt: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <Typography component="h1" variant="h5">
        Sign up
      </Typography>
      <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ mt: 1 }}>
        {mutation.isError && (
          <Alert severity="error">
            {mutation.error instanceof Error 
              ? (mutation.error as any).response?.data?.detail || mutation.error.message 
              : "Registration failed. Please try again."}
          </Alert>
        )}
        
        <TextField
          margin="normal"
          required
          fullWidth
          label="Email Address"
          autoComplete="email"
          autoFocus
          {...register('email', { required: true })}
        />
        <TextField
          margin="normal"
          required
          fullWidth
          label="Password"
          type="password"
          {...register('password', { 
            required: "Password is required", 
            minLength: { value: 8, message: "Password must be at least 8 characters" },
            pattern: {
              value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/,
              message: "Password must contain at least one uppercase letter, one lowercase letter, and one number"
            }
          })}
          error={!!errors.password}
          helperText={errors.password ? (errors.password as any).message : "Must be at least 8 characters with uppercase, lowercase, and number"}
        />
        <Button
          type="submit"
          fullWidth
          variant="contained"
          sx={{ mt: 3, mb: 2 }}
          disabled={mutation.isPending}
        >
          {mutation.isPending ? 'Registering...' : 'Sign Up'}
        </Button>
        <Link to="/login">
          <MuiLink component="span" variant="body2">
            {"Already have an account? Sign In"}
          </MuiLink>
        </Link>
      </Box>
    </Box>
  );
};

