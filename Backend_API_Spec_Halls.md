
# Halls Booking – Backend Details & API Spec (Flask + MongoDB)

**Last updated:** 2025-08-20  
**Language/Framework**: Python 3.10+, Flask 3.x  
**Database**: MongoDB 5+  
**Auth**: JWT (HS256)  
**Timezone**: UTC in tokens, app displays in PKT on frontend  
**Currency**: PKR

---

## 1) Data Models (MongoDB)

### 1.1 users
```json
{
  "_id": "ObjectId",
  "full_name": "string",
  "email": "string (unique)",
  "password_hash": "string|null",
  "contact_number": "string",
  "is_venue_owner": true,
  "role": "owner",
  "auth_provider": "password",
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```

**Indexes**
- `email` unique

### 1.2 password_resets
```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "token": "string",
  "expires_at": "ISODate",
  "created_at": "ISODate"
}
```

### 1.3 venues
```json
{
  "_id": "ObjectId",
  "owner_id": "ObjectId",
  "venue_name": "string",
  "type": "Hall|Auditorium|Banquet|Lawn",
  "address": "string",
  "maps_location": { "type": "Point", "coordinates": [lng, lat] },
  "capacity": 500,
  "dates_available": ["YYYY-MM-DD"],
  "pricing": {
    "overrides": [{ "date": "YYYY-MM-DD", "price": 150000 }]
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
  "additional_description": "string",
  "pictures": ["https://..."],
  "videos": [{"url": "https://...", "size_mb": 22.5}],
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```

**Indexes**
- `owner_id`, `type`, `capacity`
- `maps_location` (2dsphere)
- `pricing.overrides.date`

### 1.4 bookings
```json
{
  "_id": "ObjectId",
  "venue_id": "ObjectId",
  "user_id": "ObjectId",
  "date": "YYYY-MM-DD",
  "guests": 300,
  "status": "pending|confirmed|cancelled",
  "price_locked": 150000,
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```
**Indexes**
- `{ venue_id: 1, date: 1, status: 1 }`

---

## 2) Authentication & Authorization

- JWT in `Authorization: Bearer <token>`.
- Token payload includes `email` and `is_venue_owner`.
- Owner-only endpoints check `is_venue_owner=true`.

---

## 3) Endpoints

### 3.1 Health
`GET /health` → `{ "ok": true, "data": { "status": "up" } }`

### 3.2 Auth
- `POST /auth/signup` → body `{ full_name?, email, password, contact_number?, is_venue_owner }`
- `POST /auth/login` → body `{ email, password }`
- `POST /auth/google` → body `{ id_token, is_venue_owner?, contact_number? }`
- `POST /auth/forgot-password` → body `{ email }` (always returns 200)
- `POST /auth/reset-password` → body `{ token, new_password }`
- `GET /auth/me` (JWT) → current user profile

**Errors**
- `401`, `403`, `409`, `422`

### 3.3 Venues
- `POST /venues/register` (Owner) → create venue
- `PATCH /venues/:venue_id` (Owner)
- `GET /venues/search` (Public)
  - `type, capacity_min, capacity_max, date, price_min, price_max, near_lat, near_lng, near_km`
- `GET /venues/:venue_id/availability?date=YYYY-MM-DD` (Public)

### 3.4 Uploads (stubs)
- `POST /uploads/sign-s3` (Owner) → `{ upload_url, method, headers, public_url }`
- `POST /uploads/sign-cloudinary` (Owner) → `{ upload_url, unsigned_preset, params_sample }`

### 3.5 Bookings
- `POST /bookings` (JWT) → `{ venue_id, date, guests }`
- `GET /bookings` (JWT) → owner sees all his venue bookings; user sees his own
- `DELETE /bookings/:booking_id` (JWT) → cancel

**Status codes**
- `201`, `200`, `400`, `401`, `403`, `404`, `409`, `422`

---

## 4) Availability & Pricing
- Available = date is in `dates_available` **and** no `pending/confirmed` booking for that `venue/date`.
- Price on date = first match in `pricing.overrides` by date; else `null`.

---

## 5) Security
- Strong `JWT_SECRET`, password hashing, validation, rate limiting, CORS in prod.

---

## 6) Environment Variables
See `.env.example` provided in the codebase (Mongo URI, SMTP, Google Client ID, etc.).

---

## 7) Deployment
- Use Gunicorn/Uvicorn behind NGINX.
- Ensure SSL (HTTPS).
- Configure workers and timeouts; set proper CORS and rate limits.
- Ensure indexes are present on startup.

---

## 8) Testing with Postman
- Import `halls_postman_collection_v2.json`.
- Fill variables: `baseUrl`, then after login set `jwt`. After creating venue set `venue_id`. After creating booking set `booking_id`.
