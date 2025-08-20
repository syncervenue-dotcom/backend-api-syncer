
# Halls Booking – Frontend Requirements (Web & Mobile)

**Last updated:** 2025-08-20
**Timezone:** Asia/Karachi (PKT, UTC+5)  
**Currency:** PKR  
**Primary date format:** `YYYY-MM-DD`  
**API base URL:** configurable (e.g., `https://api.example.com`), default `http://localhost:5000`

---

## 1) Target Platforms
- **Web**: React (recommended), Vite/Next.js + TailwindCSS.
- **Mobile**: React Native/Expo (recommended) to share code and UI logic.
- **Shared**: JWT auth layer, API client, model/DTO types, form schemas, validation helpers.

---

## 2) Global Functional Requirements
1. **Authentication**
   - Email/Password login & signup.
   - Google Sign-In (One-tap or button).
   - Remember session: persist JWT securely.
   - Forgot/Reset password via email link.
   - `GET /auth/me` to hydrate user on app load.
2. **Venue Management (Owners only)**
   - Create venue.
   - Update venue fields.
   - Attach media: image URLs and short videos (≤ 25 MB each). Upload via presigned URL (stub).
3. **Search & Browse (Public)**
   - Filter by type, capacity, date, price range, and near a geo point.
   - View venue details; show amenities, photos, map.
4. **Bookings**
   - Check availability for a date.
   - Create booking with guest count.
   - See my bookings (user) / all my venue bookings (owner).
   - Cancel booking.
5. **Quality**
   - Accessible (WCAG AA), responsive, fast (Core Web Vitals), robust error handling.
   - Localized time/date display for PKT; price display in PKR.

---

## 3) UX Flows

### 3.1 Auth Flow
- **Signup**: email, password, full name (optional), contact number, toggle “I’m a Venue Owner”.
- **Login**: email + password **or** Google button.
- **Google Sign-In**: obtain `id_token` from client SDK; call `POST /auth/google`.
- **Hydrate session**: on app start, if JWT exists → call `GET /auth/me`; logout if 401.
- **Forgot Password**: request email → success toast (no user enumeration). Link opens reset page asking for new password.

### 3.2 Owner Dashboard
- **Create Venue** form with: 
  - Basic: name, type (Hall/Auditorium/Banquet/Lawn), address, Google Map picker (lat/lng).
  - Capacity, space (sq-ft), dates available (calendar multi-select).
  - Pricing overrides table: date & price rows.
  - Amenities (checkboxes): valet, entry package, water, AC, partition, sound.
  - Media: upload photos/videos via presigned URL → store returned public URLs; show 25 MB limit for each video.
  - Save → success toast → navigate to venue detail.
- **Edit Venue**: same fields; PATCH only changed values.
- **Bookings**: list by venue and date; status chips (pending/confirmed/cancelled).

### 3.3 User Journey (non-owner)
- **Search screen**: filters (type, capacity range, date, price range, optional location radius). Show results with cards, distance, lowest price for date if provided.
- **Venue detail**: photo gallery, amenities, map, description, availability widget with date picker.
- **Booking**: pick date → check availability → if available, show price → guest count → confirm → booking created (pending).

---

## 4) UI Components (key)
- **Auth**: LoginForm, SignupForm, GoogleButton, ForgotPasswordForm, ResetPasswordForm.
- **Venue**: VenueForm (create/edit), PricingTable, DatesMultiSelect, MapPicker (Google Maps), MediaUploader (presigned), AmenitiesChecklist.
- **Search**: FiltersBar, ResultsList (virtualized), SortDropdown, EmptyState.
- **Booking**: AvailabilityChecker, BookingForm, BookingsTable.
- **Shared**: Toast, Modal, Spinner/Skeleton, ErrorBoundary, ProtectedRoute.

---

## 5) Validation (client-side)
Use a schema library (Zod/Yup) mirroring backend:
- **Email**: RFC-like (simple pattern is fine).
- **Password**: min 6 chars.
- **Contact number**: allow `+92` and local formats.
- **Maps location**: require lat/lng numbers.
- **Capacity**: positive integer.
- **Dates**: `YYYY-MM-DD` strings.
- **Price overrides**: each row: valid date + numeric price.
- **Videos**: show 25 MB max per file (also validated server-side).

---

## 6) State Management
- Keep JWT in memory (React context) + **secure storage**:
  - Web: `localStorage` is acceptable for MVP; avoid storing refresh tokens; clear on logout.
  - Mobile: use SecureStore/Keychain.
- Query caching: React Query/TanStack Query recommended.
- Feature flags for future modules.

---

## 7) API Client Conventions
- `Authorization: Bearer <JWT>` for protected routes.
- JSON only. Handle `{ ok: false, error }` consistently.
- Retry logic only for idempotent GETs.
- Central error mapping: 401→logout, 403→show “owner required”, 422→form errors.

---

## 8) Maps Integration
- Google Maps JS/Places SDK
  - Autocomplete address; capture `lat/lng` on pin drop.
  - Show venue location on detail screen and list cards (optional mini-map).

---

## 9) Performance & UX
- Skeletons while loading, debounce search inputs, virtualize long lists.
- Image optimization: lazy load, responsive sizes.
- Avoid blocking main thread; split code; use web workers for map heavy operations if needed.

---

## 10) Accessibility
- Keyboard navigable forms and dialogs.
- Color contrast ≥ 4.5:1; aria labels for icons and media buttons.
- Focus management for modals and toasts.

---

## 11) Internationalization & Formatting
- Locale: `en-PK` default; allow future Urdu.
- Dates displayed in PKT but transmitted as `YYYY-MM-DD` (no time).

---

## 12) Security (frontend)
- Don’t store passwords or tokens in logs.
- Use HTTPS everywhere in production.
- Validate file sizes before upload; show warnings.

---

## 13) Screens Checklist
- Auth: Login, Signup, Forgot, Reset, Profile (from /auth/me)
- Owner: Venue Create, Venue Edit, My Venues, Venue Bookings
- Public: Search, Venue Detail, Booking Confirmation, My Bookings

---

## 14) Edge Cases
- Booking a date that just became unavailable → show error and refresh availability.
- Venue edit removes a date with existing bookings → block or require confirmation flow.
- Invalid Google token → fallback to email/password.
- Large media upload or network drops → resume/retry logic; show upload progress.

---

## 15) Test Scenarios (high level)
- Auth happy paths + token expiration.
- Venue creation with minimal and full payloads.
- Search with combined filters and no results.
- Availability and booking on boundary dates.
- Media upload size rejection (>25 MB).
- Unauthorized/Forbidden checks for owner-only screens.

---

## 16) Deliverables for Frontend Team
- Environment config template (API base URL, Google client ID).
- Typed API client and DTOs.
- Reusable form components with validation.
- E2E test plan covering critical flows.
