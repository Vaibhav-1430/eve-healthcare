import { apiClient } from './client';
import { Booking, PaginatedResponse } from '../types';

export interface CreateBookingPayload {
  diagnostic_centre_id: string;
  diagnostic_test_id: string;
  appointment_datetime: string;
}

export const bookingsApi = {
  createBooking: async (payload: CreateBookingPayload): Promise<Booking> => {
    const response = await apiClient.post<Booking>('/bookings/', payload);
    return response.data;
  },

  getBookings: async (page = 1, pageSize = 20): Promise<PaginatedResponse<Booking>> => {
    const response = await apiClient.get<PaginatedResponse<Booking>>('/bookings/', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  getBooking: async (id: string): Promise<Booking> => {
    const response = await apiClient.get<Booking>(`/bookings/${id}`);
    return response.data;
  },

  cancelBooking: async (id: string): Promise<Booking> => {
    const response = await apiClient.post<Booking>(`/bookings/${id}/cancel`);
    return response.data;
  },
};
