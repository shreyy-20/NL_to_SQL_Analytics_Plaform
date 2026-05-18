import React, { useState } from 'react';
import { farmerService } from '../services/api';

const FarmerSearch = () => {
  const [phone, setPhone] = useState('');
  const [farmer, setFarmer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const searchFarmer = async () => {
    if (!/^[6-9]\d{9}$/.test(phone)) {
      setError('Please enter a valid 10-digit phone number');
      return;
    }

    setLoading(true);
    setError('');
    setFarmer(null);

    try {
      const response = await farmerService.getFarmerByPhone(phone);
      setFarmer(response.data);
    } catch (err) {
      const backendMessage =
        err?.response?.data?.detail ||
        err?.response?.data?.error ||
        err?.message ||
        'Unable to reach backend service.';
      setError(backendMessage);
    } finally {
      setLoading(false);
    }
  };

  const styles = {
    container: {
      padding: '24px',
      maxWidth: '1200px',
      margin: '0 auto',
      fontFamily: "'Segoe UI', 'Nirmala UI', 'Noto Sans Devanagari', 'Kalinga', sans-serif",
      background: 'linear-gradient(135deg, #f5f5dc 0%, #e8f5e9 100%)',
      minHeight: '100vh'
    },
    header: {
      marginBottom: '40px',
      textAlign: 'center'
    },
    title: {
      fontSize: '36px',
      color: '#2e7d32',
      marginBottom: '10px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '15px'
    },
    subtitle: {
      fontSize: '16px',
      color: '#666',
      marginBottom: '30px'
    },
    searchCard: {
      background: 'white',
      borderRadius: '20px',
      padding: '30px',
      boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
      marginBottom: '30px',
      transition: 'transform 0.3s ease'
    },
    searchTitle: {
      fontSize: '20px',
      fontWeight: 'bold',
      color: '#2e7d32',
      marginBottom: '20px',
      display: 'flex',
      alignItems: 'center',
      gap: '10px'
    },
    inputGroup: {
      display: 'flex',
      gap: '15px',
      flexWrap: 'wrap',
      alignItems: 'flex-start'
    },
    inputWrapper: {
      flex: 1,
      minWidth: '250px'
    },
    label: {
      display: 'block',
      marginBottom: '8px',
      fontWeight: 'bold',
      color: '#333',
      fontSize: '14px'
    },
    input: {
      width: '100%',
      padding: '14px 16px',
      border: '2px solid #e0e0e0',
      borderRadius: '12px',
      fontSize: '16px',
      transition: 'all 0.3s ease',
      outline: 'none',
      fontFamily: 'inherit'
    },
    inputFocus: {
      borderColor: '#2e7d32',
      boxShadow: '0 0 0 3px rgba(46,125,50,0.1)'
    },
    button: {
      padding: '14px 32px',
      background: 'linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '12px',
      cursor: 'pointer',
      fontSize: '16px',
      fontWeight: 'bold',
      transition: 'all 0.3s ease',
      marginTop: '28px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
    },
    buttonDisabled: {
      opacity: 0.6,
      cursor: 'not-allowed'
    },
    errorCard: {
      background: '#ffebee',
      borderLeft: '4px solid #f44336',
      padding: '15px 20px',
      borderRadius: '12px',
      marginBottom: '20px',
      display: 'flex',
      alignItems: 'center',
      gap: '12px'
    },
    errorText: {
      color: '#c62828',
      margin: 0,
      flex: 1
    },
    resultCard: {
      background: 'white',
      borderRadius: '20px',
      overflow: 'hidden',
      boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
      marginTop: '20px'
    },
    resultHeader: {
      background: 'linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%)',
      padding: '20px 25px',
      color: 'white'
    },
    resultTitle: {
      fontSize: '20px',
      fontWeight: 'bold',
      margin: 0,
      display: 'flex',
      alignItems: 'center',
      gap: '10px'
    },
    resultBadge: {
      background: 'rgba(255,255,255,0.2)',
      padding: '4px 12px',
      borderRadius: '20px',
      fontSize: '12px'
    },
    resultContent: {
      padding: '25px'
    },
    infoGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
      gap: '20px',
      marginBottom: '20px'
    },
    infoCard: {
      background: '#f9f9f9',
      padding: '18px',
      borderRadius: '12px',
      border: '1px solid #e8f5e9',
      transition: 'all 0.3s ease'
    },
    infoLabel: {
      fontSize: '12px',
      color: '#666',
      textTransform: 'uppercase',
      letterSpacing: '1px',
      marginBottom: '8px',
      display: 'flex',
      alignItems: 'center',
      gap: '6px'
    },
    infoValue: {
      fontSize: '18px',
      fontWeight: 'bold',
      color: '#2e7d32',
      wordBreak: 'break-word'
    },
    statsRow: {
      display: 'flex',
      gap: '20px',
      flexWrap: 'wrap',
      marginTop: '20px',
      paddingTop: '20px',
      borderTop: '1px solid #e0e0e0'
    },
    statItem: {
      flex: 1,
      minWidth: '120px',
      textAlign: 'center',
      padding: '12px',
      background: '#e8f5e9',
      borderRadius: '10px'
    },
    statValue: {
      fontSize: '24px',
      fontWeight: 'bold',
      color: '#2e7d32'
    },
    statLabel: {
      fontSize: '12px',
      color: '#666'
    }
  };

  const handleInputFocus = (e) => {
    e.target.style.borderColor = styles.inputFocus.borderColor;
    e.target.style.boxShadow = styles.inputFocus.boxShadow;
  };

  const handleInputBlur = (e) => {
    e.target.style.borderColor = '#e0e0e0';
    e.target.style.boxShadow = 'none';
  };

  return React.createElement('div', { style: styles.container },
    // Header
    React.createElement('div', { style: styles.header },
      React.createElement('div', { style: styles.title },
        React.createElement('span', null, '🔍'),
        React.createElement('h1', { style: { margin: 0 } }, 'Farmer Search'),
        React.createElement('span', null, '👨‍🌾')
      ),
      React.createElement('p', { style: styles.subtitle },
        'Search farmers by mobile number to view their details and payment history'
      )
    ),

    // Search Card
    React.createElement('div', { style: styles.searchCard },
      React.createElement('div', { style: styles.searchTitle },
        React.createElement('span', null, '📱'),
        React.createElement('span', null, 'Search Farmer')
      ),
      React.createElement('div', { style: styles.inputGroup },
        React.createElement('div', { style: styles.inputWrapper },
          React.createElement('label', { style: styles.label }, 'Mobile Number'),
          React.createElement('input', {
            type: 'tel',
            placeholder: 'Enter 10-digit mobile number',
            value: phone,
            onChange: (e) => setPhone(e.target.value),
            onFocus: handleInputFocus,
            onBlur: handleInputBlur,
            style: styles.input
          })
        ),
        React.createElement('button', {
          onClick: searchFarmer,
          disabled: loading,
          style: { ...styles.button, ...(loading ? styles.buttonDisabled : {}) }
        },
          loading ? 'Searching...' : '🔍 Search Farmer'
        )
      )
    ),

    // Error Display
    error && React.createElement('div', { style: styles.errorCard },
      React.createElement('span', { style: { fontSize: '24px' } }, '⚠️'),
      React.createElement('p', { style: styles.errorText }, error),
      React.createElement('span', { 
        style: { cursor: 'pointer', fontSize: '20px' },
        onClick: () => setError('')
      }, '✖')
    ),

    // Farmer Details
    farmer && React.createElement('div', { style: styles.resultCard },
      React.createElement('div', { style: styles.resultHeader },
        React.createElement('div', { style: styles.resultTitle },
          React.createElement('span', null, '👤'),
          React.createElement('span', null, farmer.name),
          React.createElement('span', { style: styles.resultBadge }, 'Verified Farmer')
        )
      ),
      React.createElement('div', { style: styles.resultContent },
        React.createElement('div', { style: styles.infoGrid },
          React.createElement('div', { style: styles.infoCard,
            onMouseEnter: (e) => e.currentTarget.style.transform = 'translateY(-2px)',
            onMouseLeave: (e) => e.currentTarget.style.transform = 'translateY(0)'
          },
            React.createElement('div', { style: styles.infoLabel }, '📞 Phone Number'),
            React.createElement('div', { style: styles.infoValue }, farmer.phone)
          ),
          React.createElement('div', { style: styles.infoCard,
            onMouseEnter: (e) => e.currentTarget.style.transform = 'translateY(-2px)',
            onMouseLeave: (e) => e.currentTarget.style.transform = 'translateY(0)'
          },
            React.createElement('div', { style: styles.infoLabel }, '📍 Village'),
            React.createElement('div', { style: styles.infoValue }, farmer.village || 'N/A')
          ),
          React.createElement('div', { style: styles.infoCard,
            onMouseEnter: (e) => e.currentTarget.style.transform = 'translateY(-2px)',
            onMouseLeave: (e) => e.currentTarget.style.transform = 'translateY(0)'
          },
            React.createElement('div', { style: styles.infoLabel }, '🏛️ District'),
            React.createElement('div', { style: styles.infoValue }, farmer.district || 'N/A')
          ),
          React.createElement('div', { style: styles.infoCard,
            onMouseEnter: (e) => e.currentTarget.style.transform = 'translateY(-2px)',
            onMouseLeave: (e) => e.currentTarget.style.transform = 'translateY(0)'
          },
            React.createElement('div', { style: styles.infoLabel }, '🌾 Land Size'),
            React.createElement('div', { style: styles.infoValue }, 
              farmer.land_size ? `${farmer.land_size} hectares` : 'N/A'
            )
          )
        ),
        React.createElement('div', { style: styles.statsRow },
          React.createElement('div', { style: styles.statItem },
            React.createElement('div', { style: styles.statValue }, '💰'),
            React.createElement('div', { style: styles.statLabel }, 'PM-KISAN Eligible')
          ),
          React.createElement('div', { style: styles.statItem },
            React.createElement('div', { style: styles.statValue }, '🤝'),
            React.createElement('div', { style: styles.statLabel }, 'KALIA Eligible')
          ),
          React.createElement('div', { style: styles.statItem },
            React.createElement('div', { style: styles.statValue }, '📋'),
            React.createElement('div', { style: styles.statLabel }, 'Soil Test Available')
          )
        )
      )
    )
  );
};

export default FarmerSearch;