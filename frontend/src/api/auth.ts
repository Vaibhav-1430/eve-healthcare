import { apiClient } from './client';
import { User, TokenResponse } from '../types';

export interface SignupPayload {
  email: string;
  password: string;
  full_name: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export const authApi = {
  signup: async (payload: SignupPayload): Promise<User> => {
    const response = await apiClient.post<User>('/auth/signup', payload);
    return response.data;
  },

  login: async (payload: LoginPayload): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/auth/login', payload);
    return response.data;
  },
};
