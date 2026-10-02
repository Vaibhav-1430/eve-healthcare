import { apiClient } from './client';
import { DiagnosticCentre, PaginatedResponse } from '../types';

export const centresApi = {
  getCentres: async (page = 1, pageSize = 20): Promise<PaginatedResponse<DiagnosticCentre>> => {
    const response = await apiClient.get<PaginatedResponse<DiagnosticCentre>>('/centres/', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  getCentre: async (id: string): Promise<DiagnosticCentre> => {
    const response = await apiClient.get<DiagnosticCentre>(`/centres/${id}`);
    return response.data;
  },
};
