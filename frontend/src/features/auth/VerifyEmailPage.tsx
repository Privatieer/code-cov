import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { Box, CircularProgress, Button, Alert } from '@mui/material';
import { api } from '../../lib/axios';

export const VerifyEmailPage = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const navigate = useNavigate();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');

  useEffect(() => {
    if (!token) {
      setStatus('error');
      return;
    }

    api.get(`/auth/verify?token=${token}`)
      .then(() => setStatus('success'))
      .catch(() => setStatus('error'));
  }, [token]);

  return (
    <Box sx={{ mt: 8, display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
      {status === 'loading' && <CircularProgress />}
      {status === 'success' && (
        <>
          <Alert severity="success" sx={{ mb: 2 }}>Email Verified Successfully!</Alert>
          <Button variant="contained" onClick={() => navigate('/login')}>
            Go to Login
          </Button>
        </>
      )}
      {status === 'error' && (
        <>
          <Alert severity="error" sx={{ mb: 2 }}>Invalid or Expired Verification Token.</Alert>
          <Link to="/login">Back to Login</Link>
        </>
      )}
    </Box>
  );
};

