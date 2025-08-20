export interface User {
  id: string;
  email: string;
  full_name: string;
  contact_number: string;
  is_venue_owner: boolean;
  role: string;
  auth_provider: string;
}

export interface Venue {
  id: string;
  venue_name: string;
  type: 'Hall' | 'Auditorium' | 'Banquet' | 'Lawn';
  address: string;
  maps_location: {
    type: 'Point';
    coordinates: [number, number]; // [lng, lat]
  };
  capacity: number;
  dates_available: string[];
  pricing: {
    overrides: Array<{
      date: string;
      price: number;
    }>;
  };
  space_sqft?: number;
  amenities: {
    parking_valet: boolean;
    entry_package: boolean;
    water: boolean;
    air_conditioner: boolean;
    partition_facility: boolean;
    sound_system: boolean;
  };
  additional_description?: string;
  pictures: string[];
  videos: Array<{
    url: string;
    size_mb: number;
  }>;
}

export interface Booking {
  id: string;
  venue_id: string;
  user_id: string;
  date: string;
  guests: number;
  status: 'pending' | 'confirmed' | 'cancelled';
  price_locked?: number;
  created_at: string;
  updated_at: string;
}

export interface ApiResponse<T = any> {
  ok: boolean;
  data?: T;
  error?: string;
}

export interface AuthResponse {
  token: string;
  profile: User;
}

export interface VenueSearchParams {
  type?: string;
  capacity_min?: number;
  capacity_max?: number;
  date?: string;
  price_min?: number;
  price_max?: number;
  near_lat?: number;
  near_lng?: number;
  near_km?: number;
}

export interface AvailabilityResponse {
  available: boolean;
  price: number | null;
}