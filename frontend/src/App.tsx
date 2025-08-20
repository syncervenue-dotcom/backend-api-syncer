import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { Layout } from './components/Layout';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Home } from './pages/Home';
import { Login } from './pages/Login';
import { Signup } from './pages/Signup';
import { VenueSearch } from './pages/VenueSearch';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/search" element={<VenueSearch />} />
            
            {/* Protected Routes */}
            <Route 
              path="/bookings" 
              element={
                <ProtectedRoute>
                  <div className="text-center py-12">
                    <h2 className="text-2xl font-bold text-gray-900">My Bookings</h2>
                    <p className="mt-4 text-gray-600">Bookings page coming soon...</p>
                  </div>
                </ProtectedRoute>
              } 
            />
            
            {/* Owner Routes */}
            <Route 
              path="/owner/venues" 
              element={
                <ProtectedRoute requireOwner>
                  <div className="text-center py-12">
                    <h2 className="text-2xl font-bold text-gray-900">My Venues</h2>
                    <p className="mt-4 text-gray-600">Venue management page coming soon...</p>
                  </div>
                </ProtectedRoute>
              } 
            />
            
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Layout>
      </Router>
    </AuthProvider>
  );
}

export default App;