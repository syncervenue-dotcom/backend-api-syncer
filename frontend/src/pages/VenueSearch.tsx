import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { apiClient } from '../services/api';
import { Venue, VenueSearchParams } from '../types/api';
import { Search, MapPin, Users, Calendar, Filter, Star } from 'lucide-react';

export const VenueSearch: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [venues, setVenues] = useState<Venue[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  
  const [filters, setFilters] = useState<VenueSearchParams>({
    type: searchParams.get('type') || '',
    capacity_min: searchParams.get('capacity_min') ? parseInt(searchParams.get('capacity_min')!) : undefined,
    capacity_max: searchParams.get('capacity_max') ? parseInt(searchParams.get('capacity_max')!) : undefined,
    date: searchParams.get('date') || '',
    price_min: searchParams.get('price_min') ? parseFloat(searchParams.get('price_min')!) : undefined,
    price_max: searchParams.get('price_max') ? parseFloat(searchParams.get('price_max')!) : undefined,
  });

  const searchVenues = async () => {
    setLoading(true);
    setError('');
    
    const response = await apiClient.searchVenues(filters);
    
    if (response.ok && response.data) {
      setVenues(response.data.venues);
    } else {
      setError(response.error || 'Failed to search venues');
    }
    
    setLoading(false);
  };

  useEffect(() => {
    searchVenues();
  }, []);

  const handleFilterChange = (key: keyof VenueSearchParams, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value || undefined
    }));
  };

  const handleSearch = () => {
    // Update URL params
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== '') {
        params.set(key, value.toString());
      }
    });
    setSearchParams(params);
    
    searchVenues();
  };

  const clearFilters = () => {
    setFilters({});
    setSearchParams({});
    searchVenues();
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-PK', {
      style: 'currency',
      currency: 'PKR',
      minimumFractionDigits: 0,
    }).format(price);
  };

  const getPriceForDate = (venue: Venue, date?: string) => {
    if (!date) return null;
    const override = venue.pricing.overrides.find(o => o.date === date);
    return override ? override.price : null;
  };

  return (
    <div className="space-y-6">
      {/* Search Header */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold text-gray-900">Search Venues</h1>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            <Filter className="h-4 w-4" />
            <span>Filters</span>
          </button>
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Venue Type
              </label>
              <select
                value={filters.type || ''}
                onChange={(e) => handleFilterChange('type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="">All Types</option>
                <option value="Hall">Hall</option>
                <option value="Auditorium">Auditorium</option>
                <option value="Banquet">Banquet</option>
                <option value="Lawn">Lawn</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Date
              </label>
              <input
                type="date"
                value={filters.date || ''}
                onChange={(e) => handleFilterChange('date', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Min Capacity
              </label>
              <input
                type="number"
                value={filters.capacity_min || ''}
                onChange={(e) => handleFilterChange('capacity_min', parseInt(e.target.value))}
                placeholder="Min guests"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Capacity
              </label>
              <input
                type="number"
                value={filters.capacity_max || ''}
                onChange={(e) => handleFilterChange('capacity_max', parseInt(e.target.value))}
                placeholder="Max guests"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Min Price (PKR)
              </label>
              <input
                type="number"
                value={filters.price_min || ''}
                onChange={(e) => handleFilterChange('price_min', parseFloat(e.target.value))}
                placeholder="Min price"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Price (PKR)
              </label>
              <input
                type="number"
                value={filters.price_max || ''}
                onChange={(e) => handleFilterChange('price_max', parseFloat(e.target.value))}
                placeholder="Max price"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div className="md:col-span-2 lg:col-span-3 flex space-x-4">
              <button
                onClick={handleSearch}
                className="flex items-center space-x-2 px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
              >
                <Search className="h-4 w-4" />
                <span>Search</span>
              </button>
              <button
                onClick={clearFilters}
                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              >
                Clear Filters
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Results */}
      <div>
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Searching venues...</p>
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <p className="text-red-600">{error}</p>
          </div>
        ) : venues.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600">No venues found matching your criteria.</p>
          </div>
        ) : (
          <div className="space-y-4">
            <p className="text-gray-600">{venues.length} venues found</p>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {venues.map((venue) => (
                <div key={venue.id} className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow">
                  <div className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-xl font-semibold text-gray-900">{venue.venue_name}</h3>
                        <p className="text-sm text-gray-600">{venue.type}</p>
                      </div>
                      <div className="text-right">
                        {filters.date && getPriceForDate(venue, filters.date) && (
                          <p className="text-lg font-semibold text-indigo-600">
                            {formatPrice(getPriceForDate(venue, filters.date)!)}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="space-y-2 mb-4">
                      <div className="flex items-center text-sm text-gray-600">
                        <MapPin className="h-4 w-4 mr-2" />
                        {venue.address}
                      </div>
                      <div className="flex items-center text-sm text-gray-600">
                        <Users className="h-4 w-4 mr-2" />
                        Capacity: {venue.capacity} guests
                      </div>
                      {venue.space_sqft && (
                        <div className="flex items-center text-sm text-gray-600">
                          <span className="w-4 h-4 mr-2 text-center">□</span>
                          {venue.space_sqft} sq ft
                        </div>
                      )}
                    </div>

                    {/* Amenities */}
                    <div className="flex flex-wrap gap-2 mb-4">
                      {Object.entries(venue.amenities).map(([key, value]) => {
                        if (!value) return null;
                        const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                        return (
                          <span
                            key={key}
                            className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
                          >
                            {label}
                          </span>
                        );
                      })}
                    </div>

                    {/* Images */}
                    {venue.pictures.length > 0 && (
                      <div className="mb-4">
                        <img
                          src={venue.pictures[0]}
                          alt={venue.venue_name}
                          className="w-full h-48 object-cover rounded-md"
                        />
                      </div>
                    )}

                    <div className="flex justify-between items-center">
                      <div className="flex items-center space-x-2">
                        <Star className="h-4 w-4 text-yellow-400 fill-current" />
                        <span className="text-sm text-gray-600">4.5 (24 reviews)</span>
                      </div>
                      <button className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors">
                        View Details
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};