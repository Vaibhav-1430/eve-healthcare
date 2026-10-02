import { apiClient } from './client';
import { DiagnosticTest, PaginatedResponse } from '../types';

export const testsApi = {
  getCentreTests: async (
    centreId: string,
    page = 1,
    pageSize = 20
  ): Promise<PaginatedResponse<DiagnosticTest>> => {
    const response = await apiClient.get<PaginatedResponse<DiagnosticTest>>(
      `/centres/${centreId}/tests`,
      {
        params: { page, page_size: pageSize },
      }
    );
    return response.data;
  },

  getTest: async (id: string): Promise<DiagnosticTest> => {
    const response = await apiClient.get<DiagnosticTest>(`/tests/${id}`);
    return response.data;
  },
};
