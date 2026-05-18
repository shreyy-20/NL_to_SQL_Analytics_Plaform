import React, { useState } from 'react';

const FarmerSearch = () => {
  const [phone, setPhone] = useState('');
  const [farmer, setFarmer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const searchFarmer = async () => {
    if (!phone || phone.length !== 10) {
      setError('Please enter a valid 10-digit phone number');
      return;
    }

    setLoading(true);
    setError('');
    setFarmer(null);

    try {
      const response = await fetch(`/api/farmers/${phone}`);
      if (!response.ok) throw new Error('Farmer not found');
      const data = await response.json();
      setFarmer(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Farmer Search</h1>
      <div>
        <input
          type="text"
          placeholder="Enter 10-digit phone number"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          style={{ padding: '10px', width: '250px', marginRight: '10px', border: '1px solid #ccc', borderRadius: '4px' }}
        />
        <button onClick={searchFarmer} disabled={loading} style={{ padding: '10px 20px', background: '#2e7d32', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>
      {error && <p style={{ color: 'red', marginTop: '10px' }}>{error}</p>}
      {farmer && (
        <div style={{ marginTop: '20px', padding: '15px', border: '1px solid #ddd', borderRadius: '8px', background: '#f9f9f9' }}>
          <h3 style={{ marginTop: 0 }}>Farmer Details</h3>
          <p><strong>Name:</strong> {farmer.name}</p>
          <p><strong>Phone:</strong> {farmer.phone}</p>
          <p><strong>Village:</strong> {farmer.village}</p>
          <p><strong>District:</strong> {farmer.district}</p>
          <p><strong>Land Size:</strong> {farmer.land_size || 'N/A'} hectares</p>
        </div>
      )}
    </div>
  );
};

export default FarmerSearch;
