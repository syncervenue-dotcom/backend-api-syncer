# Halls Booking API Documentation

## Base URL
- **Development**: `http://localhost:5000`
- **Production**: `https://your-halls-booking-api.herokuapp.com`

## Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Response Format
All responses follow this format:
```json
{
  "ok": true,
  "data": { ... }
}
```

Error responses:
```json
{
  "ok": false,
  "error": "Error message"
}
```

## Endpoints

### Health Check
**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "ok": true,
  "data": {
    "status": "up"
  }
}
```

---

### Authentication

#### Sign Up
**POST** `/auth/signup`

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "contact_number": "+92300123456",
  "is_venue_owner": false
}
```

**Response:**
```json
{
  "ok": true,
  "data": {
    "token": "jwt-token-here",
    "profile": {
      "id": "user-id",
      "email": "user@example.com",
      "full_name": "John Doe",
      "contact_number": "+92300123456",
      "is_venue_owner": false,
      "role": "user",
      "auth_provider": "password"
    }
  }
}
```

#### Sign In
**POST** `/auth/login`

Authenticate user with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:** Same as signup

#### Google Sign In
**POST** `/auth/google`

Authenticate user with Google ID token.

**Request Body:**
```json
{
  "id_token": "google-id-token",
  "is_venue_owner": false,
  "contact_number": "+92300123456"
}
```

**Response:** Same as signup

#### Get Profile
**GET** `/auth/me`

Get current user profile. Requires authentication.

**Response:**
```json
{
  "ok": true,
  "data": {
    "profile": {
      "id": "user-id",
      "email": "user@example.com",
      "full_name": "John Doe",
      "contact_number": "+92300123456",
      "is_venue_owner": false,
      "role": "user",
      "auth_provider": "password"
    }
  }
}
```

#### Forgot Password
**POST** `/auth/forgot-password`

Send password reset email.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "ok": true,
  "data": {
    "message": "If the email exists, a reset link has been sent."
  }
}
```

#### Reset Password
**POST** `/auth/reset-password`

Reset password using token from email.

**Request Body:**
```json
{
  "token": "reset-token-from-email",
  "new_password": "newpassword123"
}
```

**Response:**
```json
{
  "ok": true,
  "data": {
    "message": "Password reset successful."
  }
}
```

---

### Venues

#### Register Venue
**POST** `/venues/register`

Create a new venue. Requires owner authentication.

**Request Body:**
```json
{
  "venue_name": "Grand Hall",
  "type": "Hall",
  "address": "123 Main Street, Karachi",
  "maps_location": {
    "lat": 24.8607,
    "lng": 67.0011
  },
  "capacity": 500,
  "dates_available": ["2025-01-15", "2025-01-16"],
  "price_with_dates": [
    {
      "date": "2025-01-15",
      "price": 150000
    }
  ],
  "space": 4000.0,
  "parking_valet": true,
  "entry_package": true,
  "water": true,
  "air_conditioner": true,
  "partition_facility": false,
  "sound_system": true,
  "additional_description": "Beautiful venue for weddings",
  "pictures": ["https://example.com/image1.jpg"],
  "videos": [
    {
      "url": "https://example.com/video1.mp4",
      "size_mb": 22.5
    }
  ]
}
```

**Response:**
```json
{
  "ok": true,
  "data": {
    "venue_id": "venue-id-here"
  }
}
```

#### Update Venue
**PATCH** `/venues/<venue_id>`

Update venue details. Requires owner authentication and ownership.

**Request Body:** Same fields as register venue (all optional)

**Response:**
```json
{
  "ok": true,
  "data": {
    "venue": {
      "id": "venue-id",
      "venue_name": "Grand Hall",
      "type": "Hall",
      "address": "123 Main Street, Karachi",
      "maps_location": {
        "type": "Point",
        "coordinates": [67.0011, 24.8607]
      },
      "capacity": 500,
      "dates_available": ["2025-01-15", "2025-01-16"],
      "pricing": {
        "overrides": [
          {
            "date": "2025-01-15",
            "price": 150000
          }
        ]
      },
      "space_sqft": 4000.0,
      "amenities": {
        "parking_valet": true,
        "entry_package": true,
        "water": true,
        "air_conditioner": true,
        "partition_facility": false,
        "sound_system": true
      },
      "pictures": ["https://example.com/image1.jpg"],
      "videos": [
        {
          "url": "https://example.com/video1.mp4",
          "size_mb": 22.5
        }
      ]
    }
  }
}
```

#### Search Venues
**GET** `/venues/search`

Search for venues with filters. Public endpoint.

**Query Parameters:**
- `type`: Venue type (Hall, Auditorium, Banquet, Lawn)
- `capacity_min`: Minimum capacity
- `capacity_max`: Maximum capacity
- `date`: Available date (YYYY-MM-DD)
- `price_min`: Minimum price
- `price_max`: Maximum price
- `near_lat`: Latitude for location search
- `near_lng`: Longitude for location search
- `near_km`: Search radius in kilometers

**Example:**
```
GET /venues/search?type=Hall&capacity_min=100&capacity_max=500&date=2025-01-15
```

**Response:**
```json
{
  "ok": true,
  "data": {
    "venues": [
      {
        "id": "venue-id",
        "venue_name": "Grand Hall",
        "type": "Hall",
        "address": "123 Main Street, Karachi",
        "maps_location": {
          "type": "Point",
          "coordinates": [67.0011, 24.8607]
        },
        "capacity": 500,
        "dates_available": ["2025-01-15", "2025-01-16"],
        "pricing": {
          "overrides": [
            {
              "date": "2025-01-15",
              "price": 150000
            }
          ]
        },
        "space_sqft": 4000.0,
        "amenities": {
          "parking_valet": true,
          "entry_package": true,
          "water": true,
          "air_conditioner": true,
          "partition_facility": false,
          "sound_system": true
        },
        "pictures": ["https://example.com/image1.jpg"],
        "videos": [
          {
            "url": "https://example.com/video1.mp4",
            "size_mb": 22.5
          }
        ]
      }
    ]
  }
}
```

#### Check Venue Availability
**GET** `/venues/<venue_id>/availability`

Check if a venue is available on a specific date.

**Query Parameters:**
- `date`: Date to check (YYYY-MM-DD) - Required

**Example:**
```
GET /venues/123/availability?date=2025-01-15
```

**Response:**
```json
{
  "ok": true,
  "data": {
    "available": true,
    "price": 150000
  }
}
```

---

### Bookings

#### Create Booking
**POST** `/bookings`

Create a new booking. Requires authentication.

**Request Body:**
```json
{
  "venue_id": "venue-id",
  "date": "2025-01-15",
  "guests": 300,
  "notes": "Wedding reception"
}
```

**Response:**
```json
{
  "ok": true,
  "data": {
    "booking_id": "booking-id",
    "price": 150000,
    "status": "pending"
  }
}
```

#### Get Bookings
**GET** `/bookings`

Get bookings for current user. Requires authentication.
- Regular users see their own bookings
- Venue owners see bookings for their venues

**Response:**
```json
{
  "ok": true,
  "data": {
    "bookings": [
      {
        "id": "booking-id",
        "venue_id": "venue-id",
        "user_id": "user-id",
        "date": "2025-01-15",
        "guests": 300,
        "status": "pending",
        "price_locked": 150000,
        "created_at": "2025-01-01T10:00:00Z",
        "updated_at": "2025-01-01T10:00:00Z"
      }
    ]
  }
}
```

#### Update Booking Status
**PATCH** `/bookings/<booking_id>`

Update booking status. Requires authentication.
- Venue owners can confirm/reject pending bookings
- Users can cancel their own bookings

**Request Body:**
```json
{
  "status": "confirmed"
}
```

**Valid statuses:** `confirmed`, `rejected`, `cancelled`

**Response:**
```json
{
  "ok": true,
  "data": {
    "booking": {
      "id": "booking-id",
      "venue_id": "venue-id",
      "user_id": "user-id",
      "date": "2025-01-15",
      "guests": 300,
      "status": "confirmed",
      "price_locked": 150000,
      "notes": "Wedding reception"
    }
  }
}
```

#### Cancel Booking
**DELETE** `/bookings/<booking_id>`

Cancel a booking. Requires authentication and ownership.

**Response:**
```json
{
  "ok": true,
  "data": {
    "cancelled": true
  }
}
```

---

### File Uploads

#### Get Cloudinary Upload Signature
**POST** `/uploads/sign-cloudinary`

Get signed upload parameters for Cloudinary. Requires owner authentication.

**Request Body:**
```json
{
  "folder": "venues",
  "public_id": "venue-123-image-1",
  "resource_type": "image"
}
```

**Response:**
```json
{
  "ok": true,
  "data": {
    "mode": "signed",
    "upload_url": "https://api.cloudinary.com/v1_1/your-cloud/image/upload",
    "params": {
      "api_key": "your-api-key",
      "timestamp": 1640995200,
      "folder": "venues",
      "public_id": "venue-123-image-1",
      "signature": "generated-signature"
    }
  }
}
```

---

## Error Codes

- **400**: Bad Request - Invalid request data
- **401**: Unauthorized - Missing or invalid authentication
- **403**: Forbidden - Insufficient permissions
- **404**: Not Found - Resource not found
- **409**: Conflict - Resource already exists or conflict
- **422**: Unprocessable Entity - Validation errors
- **500**: Internal Server Error - Server error

## Rate Limiting

The API implements basic rate limiting to prevent abuse. If you exceed the rate limit, you'll receive a 429 status code.

## CORS

The API supports CORS for web applications. Make sure your frontend domain is included in the CORS configuration.

## Data Formats

- **Dates**: Use ISO format (YYYY-MM-DD) for dates
- **Coordinates**: [longitude, latitude] format for GeoJSON
- **Currency**: Prices are in PKR (Pakistani Rupees)
- **Timezone**: All timestamps are in UTC

## Example Usage

### JavaScript/TypeScript
```javascript
const API_BASE = 'https://your-api-domain.com';

// Login
const loginResponse = await fetch(`${API_BASE}/auth/login`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});

const { data } = await loginResponse.json();
const token = data.token;

// Search venues
const searchResponse = await fetch(`${API_BASE}/venues/search?type=Hall&capacity_min=100`);
const venues = await searchResponse.json();

// Create booking (authenticated)
const bookingResponse = await fetch(`${API_BASE}/bookings`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    venue_id: 'venue-id',
    date: '2025-01-15',
    guests: 300
  })
});
```

This API documentation provides comprehensive information for integrating with the Halls Booking backend service.