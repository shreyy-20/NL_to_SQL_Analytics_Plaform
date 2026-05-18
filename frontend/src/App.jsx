import React, { useState } from 'react';

import Dashboard from './components/Dashboard';
import FarmerSearch from './components/FarmerSearch';
import QueryInterface from './components/QueryInterface';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');

  return (
    <div style={{ fontFamily: 'Arial, sans-serif' }}>
      <div style={{ background: '#2e7d32', padding: '15px 20px', color: 'white', display: 'flex', alignItems: 'center' }}>
        <h1 style={{ margin: 0, fontSize: '24px' }}>KrishiQuery</h1>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: '20px' }}>
          <button 
            onClick={() => setCurrentPage('dashboard')} 
            style={{ background: currentPage === 'dashboard' ? '#1b5e20' : 'none', border: 'none', color: 'white', cursor: 'pointer', fontSize: '16px', padding: '8px 16px', borderRadius: '4px' }}
          >
            Dashboard
          </button>
          <button 
            onClick={() => setCurrentPage('farmers')} 
            style={{ background: currentPage === 'farmers' ? '#1b5e20' : 'none', border: 'none', color: 'white', cursor: 'pointer', fontSize: '16px', padding: '8px 16px', borderRadius: '4px' }}
          >
            Farmer Search
          </button>
          <button 
            onClick={() => setCurrentPage('query')} 
            style={{ background: currentPage === 'query' ? '#1b5e20' : 'none', border: 'none', color: 'white', cursor: 'pointer', fontSize: '16px', padding: '8px 16px', borderRadius: '4px' }}
          >
            Query
          </button>
        </div>
      </div>

      <div style={{ padding: '20px' }}>
        {currentPage === 'dashboard' && <Dashboard />}
        {currentPage === 'farmers' && <FarmerSearch />}
        {currentPage === 'query' && <QueryInterface />}
      </div>
    </div>
  );
}

export default App;
