import React, { useState, useRef, useEffect } from 'react';
import { useLoadScript, GoogleMap, Marker } from '@react-google-maps/api';
import usePlacesAutocomplete, {
    getGeocode,
    getLatLng,
} from 'use-places-autocomplete';
import '../pages/css/LocationPicker.css';

const libraries = ['places'];
const mapContainerStyle = {
    width: '100%',
    height: '300px',
    borderRadius: '12px'
};
const defaultCenter = {
    lat: 20.5937,  // India center
    lng: 78.9629
};

const LocationPicker = ({ onLocationSelect, initialLocation = '' }) => {
    const [selectedLocation, setSelectedLocation] = useState(initialLocation);
    const [markerPosition, setMarkerPosition] = useState(defaultCenter);
    const [mapCenter, setMapCenter] = useState(defaultCenter);
    const [mapLoaded, setMapLoaded] = useState(false);
    const mapRef = useRef(null);
    const markerRef = useRef(null);

    // Load Google Maps
    const { isLoaded, loadError } = useLoadScript({
        googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
        libraries,
    });

    // Places Autocomplete
    const {
        ready,
        value,
        suggestions: { status, data },
        setValue,
        clearSuggestions,
    } = usePlacesAutocomplete({
        requestOptions: {
            componentRestrictions: { country: 'in' }, // Restrict to India
            types: ['geocode', 'establishment'],
        },
        debounce: 300,
    });

    // Handle place selection from autocomplete
    const handlePlaceSelect = async (address) => {
        setValue(address, false);
        clearSuggestions();

        try {
            const results = await getGeocode({ address });
            const { lat, lng } = await getLatLng(results[0]);
            
            const locationString = results[0].formatted_address;
            setSelectedLocation(locationString);
            setMarkerPosition({ lat, lng });
            setMapCenter({ lat, lng });
            
            if (onLocationSelect) {
                onLocationSelect(locationString, { lat, lng });
            }
        } catch (error) {
            console.error('Error getting location:', error);
        }
    };

    // Handle map click
    const handleMapClick = async (event) => {
        const lat = event.latLng.lat();
        const lng = event.latLng.lng();
        
        setMarkerPosition({ lat, lng });
        setMapCenter({ lat, lng });

        // Reverse geocode to get address
        try {
            const geocoder = new window.google.maps.Geocoder();
            const response = await new Promise((resolve, reject) => {
                geocoder.geocode({ location: { lat, lng } }, (results, status) => {
                    if (status === 'OK' && results[0]) {
                        resolve(results[0]);
                    } else {
                        reject(new Error('Geocoding failed'));
                    }
                });
            });

            const locationString = response.formatted_address;
            setSelectedLocation(locationString);
            setValue(locationString, false);
            
            if (onLocationSelect) {
                onLocationSelect(locationString, { lat, lng });
            }
        } catch (error) {
            console.error('Reverse geocoding error:', error);
        }
    };

    // Get current location
    const getCurrentLocation = () => {
        if (!navigator.geolocation) {
            alert('Geolocation is not supported by your browser');
            return;
        }

        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const { latitude, longitude } = position.coords;
                const lat = latitude;
                const lng = longitude;
                
                setMarkerPosition({ lat, lng });
                setMapCenter({ lat, lng });

                // Reverse geocode
                try {
                    const geocoder = new window.google.maps.Geocoder();
                    const response = await new Promise((resolve, reject) => {
                        geocoder.geocode({ location: { lat, lng } }, (results, status) => {
                            if (status === 'OK' && results[0]) {
                                resolve(results[0]);
                            } else {
                                reject(new Error('Geocoding failed'));
                            }
                        });
                    });

                    const locationString = response.formatted_address;
                    setSelectedLocation(locationString);
                    setValue(locationString, false);
                    
                    if (onLocationSelect) {
                        onLocationSelect(locationString, { lat, lng });
                    }
                } catch (error) {
                    console.error('Reverse geocoding error:', error);
                    // Fallback to coordinates
                    const locationString = `${lat}, ${lng}`;
                    setSelectedLocation(locationString);
                    if (onLocationSelect) {
                        onLocationSelect(locationString, { lat, lng });
                    }
                }
            },
            (error) => {
                console.error('Error getting location:', error);
                alert('Unable to get your location. Please allow location access or enter manually.');
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    };

    if (loadError) {
        return (
            <div className="location-error">
                <p>Error loading Google Maps. Please check your API key.</p>
                <input
                    type="text"
                    placeholder="Enter location manually..."
                    value={selectedLocation}
                    onChange={(e) => {
                        setSelectedLocation(e.target.value);
                        if (onLocationSelect) {
                            onLocationSelect(e.target.value, null);
                        }
                    }}
                    className="manual-location-input"
                />
            </div>
        );
    }

    if (!isLoaded) {
        return <div className="location-loading">Loading maps...</div>;
    }

    return (
        <div className="location-picker">
            <div className="location-search">
                <div className="search-container">
                    <i className="fas fa-search search-icon"></i>
                    <input
                        value={value}
                        onChange={(e) => setValue(e.target.value)}
                        disabled={!ready}
                        placeholder="Search for a location..."
                        className="location-search-input"
                    />
                    <button
                        onClick={getCurrentLocation}
                        className="current-location-btn"
                        title="Use my current location"
                    >
                        <i className="fas fa-location-dot"></i>
                    </button>
                </div>

                {status === 'OK' && data.length > 0 && (
                    <ul className="autocomplete-dropdown">
                        {data.map(({ place_id, structured_formatting }) => (
                            <li
                                key={place_id}
                                onClick={() => handlePlaceSelect(structured_formatting.main_text)}
                                className="autocomplete-item"
                            >
                                <i className="fas fa-map-pin"></i>
                                <div>
                                    <div className="suggestion-main">
                                        {structured_formatting.main_text}
                                    </div>
                                    <div className="suggestion-secondary">
                                        {structured_formatting.secondary_text}
                                    </div>
                                </div>
                            </li>
                        ))}
                    </ul>
                )}
            </div>

            <div className="map-container">
                <GoogleMap
                    id="location-picker-map"
                    mapContainerStyle={mapContainerStyle}
                    center={mapCenter}
                    zoom={15}
                    onClick={handleMapClick}
                    onLoad={(map) => {
                        mapRef.current = map;
                        setMapLoaded(true);
                    }}
                    options={{
                        zoomControl: true,
                        streetViewControl: false,
                        mapTypeControl: false,
                        fullscreenControl: true,
                    }}
                >
                    {markerPosition && (
                        <Marker
                            position={markerPosition}
                            draggable={true}
                            onDragEnd={(event) => {
                                const lat = event.latLng.lat();
                                const lng = event.latLng.lng();
                                setMarkerPosition({ lat, lng });
                                // Update location on drag
                                // Reverse geocode would be called here
                            }}
                        />
                    )}
                </GoogleMap>
            </div>

            <div className="selected-location">
                <label>Selected Location:</label>
                <textarea
                    value={selectedLocation}
                    onChange={(e) => {
                        setSelectedLocation(e.target.value);
                        if (onLocationSelect) {
                            onLocationSelect(e.target.value, null);
                        }
                    }}
                    placeholder="Location details will appear here..."
                    rows={2}
                    className="selected-location-text"
                />
                <div className="location-hint">
                    <i className="fas fa-info-circle"></i>
                    <span>Click on the map or search to select location</span>
                </div>
            </div>

            {markerPosition && (
                <div className="location-coords">
                    <small>
                        📍 Lat: {markerPosition.lat.toFixed(6)}, 
                        Lng: {markerPosition.lng.toFixed(6)}
                    </small>
                </div>
            )}
        </div>
    );
};

export default LocationPicker;