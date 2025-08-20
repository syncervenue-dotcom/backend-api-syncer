import { 
  User, 
  Venue, 
  Booking, 
  ApiResponse, 
  AuthResponse, 
  VenueSearchParams, 
  AvailabilityResponse 
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

class ApiClient {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('auth_token');
  }

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }

  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      const data = await response.json();
      
      if (!response.ok) {
        return { ok: false, error: data.error || 'Request failed' };
      }

      return data;
    } catch (error) {
      return { 
        ok: false, 
        error: error instanceof Error ? error.message : 'Network error' 
      };
    }
  }

  // Auth endpoints
  async signup(userData: {
    email: string;
    password: string;
    full_name?: string;
    contact_number?: string;
    is_venue_owner: boolean;
  }): Promise<ApiResponse<AuthResponse>> {
    return this.request<AuthResponse>('/auth/signup', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async login(credentials: {
    email: string;
    password: string;
  }): Promise<ApiResponse<AuthResponse>> {
    return this.request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async googleLogin(data: {
    id_token: string;
    is_venue_owner?: boolean;
    contact_number?: string;
  }): Promise<ApiResponse<AuthResponse>> {
    return this.request<AuthResponse>('/auth/google', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getProfile(): Promise<ApiResponse<{ profile: User }>> {
    return this.request<{ profile: User }>('/auth/me');
  }

  async forgotPassword(email: string): Promise<ApiResponse<{ message: string }>> {
    return this.request<{ message: string }>('/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  }

  async resetPassword(token: string, newPassword: string): Promise<ApiResponse<{ message: string }>> {
    return this.request<{ message: string }>('/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify({ token, new_password: newPassword }),
    });
  }

  // Venue endpoints
  async registerVenue(venueData: Partial<Venue>): Promise<ApiResponse<{ venue_id: string }>> {
    return this.request<{ venue_id: string }>('/venues/register', {
      method: 'POST',
      body: JSON.stringify(venueData),
    });
  }

  async updateVenue(venueId: string, venueData: Partial<Venue>): Promise<ApiResponse<{ venue: Venue }>> {
    return this.request<{ venue: Venue }>(`/venues/${venueId}`, {
      method: 'PATCH',
      body: JSON.stringify(venueData),
    });
  }

  async searchVenues(params: VenueSearchParams): Promise<ApiResponse<{ venues: Venue[] }>> {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value.toString());
      }
    });
    
    return this.request<{ venues: Venue[] }>(`/venues/search?${searchParams}`);
  }

  async getVenueAvailability(venueId: string, date: string): Promise<ApiResponse<AvailabilityResponse>> {
    return this.request<AvailabilityResponse>(`/venues/${venueId}/availability?date=${date}`);
  }

  // Booking endpoints
  async createBooking(bookingData: {
    venue_id: string;
    date: string;
    guests_count: number;
    notes?: string;
  }): Promise<ApiResponse<{ booking_id: string; price: number | null; status: string }>> {
    return this.request<{ booking_id: string; price: number | null; status: string }>('/bookings', {
      method: 'POST',
      body: JSON.stringify(bookingData),
    });
  }

  async getBookings(): Promise<ApiResponse<{ bookings: Booking[] }>> {
    return this.request<{ bookings: Booking[] }>('/bookings');
  }

  async cancelBooking(bookingId: string): Promise<ApiResponse<{ cancelled: boolean }>> {
    return this.request<{ cancelled: boolean }>(`/bookings/${bookingId}`, {
      method: 'DELETE',
    });
  }

  async updateBookingStatus(bookingId: string, status: string): Promise<ApiResponse<{ booking: Booking }>> {
    return this.request<{ booking: Booking }>(`/bookings/${bookingId}`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
  }

  // Upload endpoints
  async getCloudinarySignature(params: {
    folder?: string;
    public_id?: string;
    resource_type?: string;
  }): Promise<ApiResponse<any>> {
    return this.request<any>('/uploads/sign-cloudinary', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }
}

export const apiClient = new ApiClient(API_BASE_URL);