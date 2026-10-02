import { apiClient } from './client';
import { Payment, PaymentStatus } from '../types';

export interface SimulatePaymentPayload {
  booking_id: string;
  simulated_status: PaymentStatus;
}

export const paymentsApi = {
  simulatePayment: async (payload: SimulatePaymentPayload): Promise<Payment> => {
    const response = await apiClient.post<Payment>('/payments/', payload);
    return response.data;
  },
};
