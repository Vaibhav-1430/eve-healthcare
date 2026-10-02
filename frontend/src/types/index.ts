export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface DiagnosticCentre {
  id: string;
  name: string;
  location: string;
  created_at: string;
}

export interface DiagnosticTest {
  id: string;
  centre_id: string;
  name: string;
  description?: string | null;
  price: string | number;
  created_at: string;
}

export type BookingStatus = 'PENDING' | 'CONFIRMED' | 'FAILED' | 'CANCELLED';

export interface Booking {
  id: string;
  user_id: string;
  diagnostic_centre_id: string;
  diagnostic_test_id: string;
  appointment_datetime: string;
  status: BookingStatus;
  amount: string | number;
  created_at: string;
  updated_at?: string;
}

export type PaymentStatus = 'PENDING' | 'SUCCESS' | 'FAILED';

export interface Payment {
  id: string;
  booking_id: string;
  amount: string | number;
  status: PaymentStatus;
  provider_reference?: string | null;
  created_at: string;
  updated_at?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface ApiError {
  message: string;
  detail?: string | Array<{ msg: string; loc?: string[] }>;
  status?: number;
}
