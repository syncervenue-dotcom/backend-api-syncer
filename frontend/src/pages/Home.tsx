import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Search, Building2, Calendar, Users, MapPin, Star } from 'lucide-react';

export const Home: React.FC = () => {
  const { user } = useAuth();

  const features = [
    {
      icon: Search,
      title: 'Easy Search',
      description: 'Find the perfect venue with our advanced search filters'
    },
    {
      icon: Calendar,
      title: 'Real-time Availability',
      description: 'Check availability and book instantly'
    },
    {
      icon: Users,
      title: 'Capacity Management',
      description: 'Filter venues by guest capacity'
    },
    {
      icon: MapPin,
      title: 'Location-based',
      description: 'Find venues near your preferred location'
    }
  ];

  const venueTypes = [
    { name: 'Halls', count: '150+', image: 'https://images.pexels.com/photos/1395967/pexels-photo-1395967.jpeg?auto=compress&cs=tinysrgb&w=400' },
    { name: 'Auditoriums', count: '80+', image: 'https://images.pexels.com/photos/2747449/pexels-photo-2747449.jpeg?auto=compress&cs=tinysrgb&w=400' },
    { name: 'Banquets', count: '200+', image: 'https://images.pexels.com/photos/1395964/pexels-photo-1395964.jpeg?auto=compress&cs=tinysrgb&w=400' },
    { name: 'Lawns', count: '120+', image: 'https://images.pexels.com/photos/1395966/pexels-photo-1395966.jpeg?auto=compress&cs=tinysrgb&w=400' }
  ];

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <div className="text-center space-y-8">
        <div className="space-y-4">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900">
            Find Your Perfect
            <span className="text-indigo-600"> Venue</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Discover and book amazing venues for your events. From elegant halls to spacious lawns, 
            we have the perfect space for every occasion.
          </p>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/search"
            className="inline-flex items-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 transition-colors"
          >
            <Search className="mr-2 h-5 w-5" />
            Search Venues
          </Link>
          
          {user?.is_venue_owner && (
            <Link
              to="/owner/venues/new"
              className="inline-flex items-center px-8 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 transition-colors"
            >
              <Building2 className="mr-2 h-5 w-5" />
              List Your Venue
            </Link>
          )}
        </div>
      </div>

      {/* Features Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
        {features.map((feature, index) => (
          <div key={index} className="text-center space-y-4">
            <div className="mx-auto w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center">
              <feature.icon className="h-8 w-8 text-indigo-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900">{feature.title}</h3>
            <p className="text-gray-600">{feature.description}</p>
          </div>
        ))}
      </div>

      {/* Venue Types Section */}
      <div className="space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900">Popular Venue Types</h2>
          <p className="mt-4 text-lg text-gray-600">
            Choose from our wide variety of venues
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {venueTypes.map((type, index) => (
            <Link
              key={index}
              to={`/search?type=${type.name.slice(0, -1)}`}
              className="group relative overflow-hidden rounded-lg shadow-lg hover:shadow-xl transition-shadow"
            >
              <div className="aspect-w-16 aspect-h-12">
                <img
                  src={type.image}
                  alt={type.name}
                  className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
                />
              </div>
              <div className="absolute inset-0 bg-black bg-opacity-40 flex items-end">
                <div className="p-6 text-white">
                  <h3 className="text-xl font-semibold">{type.name}</h3>
                  <p className="text-sm opacity-90">{type.count} venues</p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-indigo-600 rounded-2xl p-8 text-white">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
          <div>
            <div className="text-4xl font-bold">500+</div>
            <div className="text-indigo-200">Venues Listed</div>
          </div>
          <div>
            <div className="text-4xl font-bold">10K+</div>
            <div className="text-indigo-200">Events Hosted</div>
          </div>
          <div>
            <div className="text-4xl font-bold">4.8</div>
            <div className="flex items-center justify-center space-x-1 text-indigo-200">
              <Star className="h-5 w-5 fill-current" />
              <span>Average Rating</span>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      {!user && (
        <div className="text-center space-y-6 bg-gray-100 rounded-2xl p-8">
          <h2 className="text-3xl font-bold text-gray-900">Ready to Get Started?</h2>
          <p className="text-lg text-gray-600">
            Join thousands of users who trust us with their events
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/signup"
              className="inline-flex items-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 transition-colors"
            >
              Sign Up Now
            </Link>
            <Link
              to="/login"
              className="inline-flex items-center px-8 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 transition-colors"
            >
              Already have an account?
            </Link>
          </div>
        </div>
      )}
    </div>
  );
};