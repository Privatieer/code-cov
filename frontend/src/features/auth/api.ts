import { api } from '../../lib/axios';

export const login = async (data: any) => {
  const params = new URLSearchParams();
  params.append('username', data.email);
  params.append('password', data.password);

  const response = await api.post('/auth/token', params, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  });
  return response.data;
};

export const register = async (data: any) => {
  const response = await api.post('/auth/register', data);
  return response.data;
};
