import React from 'react';

const Dashboard = () => {
  // Styles object for better organization
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
      textAlign: 'center',
      marginBottom: '40px',
      padding: '20px',
      background: 'linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%)',
      borderRadius: '20px',
      color: 'white',
      boxShadow: '0 10px 30px rgba(0,0,0,0.2)'
    },
    title: {
      fontSize: '42px',
      marginBottom: '10px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '15px'
    },
    subtitle: {
      fontSize: '18px',
      opacity: 0.95
    },
    statsGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
      gap: '20px',
      marginBottom: '40px'
    },
    statCard: {
      background: 'white',
      padding: '25px',
      borderRadius: '15px',
      textAlign: 'center',
      boxShadow: '0 4px 15px rgba(0,0,0,0.1)',
      transition: 'transform 0.3s ease',
      cursor: 'pointer'
    },
    statNumber: {
      fontSize: '36px',
      fontWeight: 'bold',
      color: '#2e7d32',
      marginBottom: '10px'
    },
    statLabel: {
      fontSize: '14px',
      color: '#666',
      textTransform: 'uppercase',
      letterSpacing: '1px'
    },
    quickActions: {
      marginBottom: '40px'
    },
    sectionTitle: {
      fontSize: '24px',
      color: '#2e7d32',
      marginBottom: '20px',
      paddingBottom: '10px',
      borderBottom: '3px solid #ff8f00',
      display: 'inline-block'
    },
    queryGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
      gap: '15px',
      marginTop: '20px'
    },
    queryCard: {
      background: 'white',
      padding: '20px',
      borderRadius: '12px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      transition: 'all 0.3s ease',
      cursor: 'pointer',
      borderLeft: '4px solid #ff8f00'
    },
    queryText: {
      fontSize: '16px',
      color: '#333',
      marginBottom: '10px',
      lineHeight: '1.5'
    },
    queryLang: {
      fontSize: '12px',
      color: '#ff8f00',
      fontWeight: 'bold'
    },
    featuresGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
      gap: '20px',
      marginTop: '30px'
    },
    featureCard: {
      background: 'white',
      padding: '20px',
      borderRadius: '12px',
      textAlign: 'center',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
    },
    featureIcon: {
      fontSize: '40px',
      marginBottom: '10px'
    },
    featureTitle: {
      fontSize: '16px',
      fontWeight: 'bold',
      color: '#2e7d32',
      marginBottom: '8px'
    },
    featureDesc: {
      fontSize: '12px',
      color: '#666'
    }
  };

  // Handle query click - redirect to query page with pre-filled question
  const handleQueryClick = (question) => {
    // Store the question in sessionStorage to pre-fill on query page
    sessionStorage.setItem('prefilledQuestion', question);
    window.location.href = '/query';
  };

  // Stats data (you can replace with real API data later)
  const stats = [
    { number: '10,000+', label: 'Registered Farmers', icon: '👨‍🌾' },
    { number: '₹50L+', label: 'Total Disbursed', icon: '💰' },
    { number: '25,000+', label: 'Queries Answered', icon: '💬' },
    { number: '30+', label: 'Mandi Covered', icon: '🏪' }
  ];

  const features = [
    { icon: '💸', title: 'Payment Status', desc: 'PM-KISAN & KALIA YOJNA updates' },
    { icon: '📊', title: 'Mandi Prices', desc: 'Real-time crop rates' },
    { icon: '🌱', title: 'Soil Health', desc: 'Test reports & advice' },
    { icon: '☀️', title: 'Weather Forecast', desc: '7-day prediction' }
  ];

  const queries = [
    { text: 'मेरी PM-KISAN की किस्त आई क्या?', lang: 'हिन्दी' },
    { text: 'भुवनेश्वर मंडी में धान का भाव क्या है?', lang: 'हिन्दी' },
    { text: 'मेरी मिट्टी परीक्षण रिपोर्ट दिखाओ', lang: 'हिन्दी' },
    { text: 'अगले हफ्ते बारिश होगी क्या?', lang: 'हिन्दी' },
    { text: 'Did my PM-KISAN installment come?', lang: 'English' },
    { text: 'What is the price of paddy in Cuttack?', lang: 'English' }
  ];

  return React.createElement('div', { style: styles.container },
    // Header Section
    React.createElement('div', { style: styles.header },
      React.createElement('div', { style: styles.title },
        React.createElement('span', null, '🌾'),
        React.createElement('h1', { style: { margin: 0 } }, 'KrishiQuery'),
        React.createElement('span', null, '🇮🇳')
      ),
      React.createElement('p', { style: styles.subtitle }, 
        'Voice-Based Natural Language Query System for Indian Agriculture'
      ),
      React.createElement('p', { style: { ...styles.subtitle, fontSize: '14px', marginTop: '10px' } }, 
        'Ask questions in हिन्दी, ଓଡ଼ିଆ, or English'
      )
    ),

    // Stats Section
    React.createElement('div', { style: styles.statsGrid },
      stats.map((stat, index) =>
        React.createElement('div', { key: index, style: styles.statCard,
          onMouseEnter: (e) => e.currentTarget.style.transform = 'translateY(-5px)',
          onMouseLeave: (e) => e.currentTarget.style.transform = 'translateY(0)'
        },
          React.createElement('div', { style: { fontSize: '40px', marginBottom: '10px' } }, stat.icon),
          React.createElement('div', { style: styles.statNumber }, stat.number),
          React.createElement('div', { style: styles.statLabel }, stat.label)
        )
      )
    ),

    // Features Section
    React.createElement('div', null,
      React.createElement('h2', { style: styles.sectionTitle }, '✨ What We Offer'),
      React.createElement('div', { style: styles.featuresGrid },
        features.map((feature, index) =>
          React.createElement('div', { key: index, style: styles.featureCard },
            React.createElement('div', { style: styles.featureIcon }, feature.icon),
            React.createElement('div', { style: styles.featureTitle }, feature.title),
            React.createElement('div', { style: styles.featureDesc }, feature.desc)
          )
        )
      )
    ),

    // Quick Actions / Sample Queries
    React.createElement('div', { style: styles.quickActions },
      React.createElement('h2', { style: styles.sectionTitle }, '🎤 Try These Sample Queries'),
      React.createElement('div', { style: styles.queryGrid },
        queries.map((query, index) =>
          React.createElement('div', { 
            key: index, 
            style: styles.queryCard,
            onClick: () => handleQueryClick(query.text),
            onMouseEnter: (e) => {
              e.currentTarget.style.transform = 'translateX(5px)';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
            },
            onMouseLeave: (e) => {
              e.currentTarget.style.transform = 'translateX(0)';
              e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
            }
          },
            React.createElement('div', { style: styles.queryText }, query.text),
            React.createElement('div', { style: styles.queryLang }, query.lang)
          )
        )
      )
    ),

    // Voice Assistant CTA
    React.createElement('div', { 
      style: {
        background: 'linear-gradient(135deg, #ff8f00 0%, #ff6f00 100%)',
        borderRadius: '15px',
        padding: '25px',
        textAlign: 'center',
        marginTop: '30px',
        cursor: 'pointer',
        transition: 'transform 0.3s ease'
      },
      onClick: () => window.location.href = '/query',
      onMouseEnter: (e) => e.currentTarget.style.transform = 'scale(1.02)',
      onMouseLeave: (e) => e.currentTarget.style.transform = 'scale(1)'
    },
      React.createElement('div', { style: { fontSize: '48px', marginBottom: '10px' } }, '🔊'),
      React.createElement('h3', { style: { color: 'white', marginBottom: '10px' } }, 'Have a Question?'),
      React.createElement('p', { style: { color: 'white', opacity: 0.95 } }, 
        'Click here to ask in Hindi, Odia, or English'
      )
    ),

    // Footer
    React.createElement('div', { 
      style: {
        marginTop: '40px',
        padding: '20px',
        textAlign: 'center',
        borderTop: '1px solid #ddd',
        color: '#666',
        fontSize: '12px'
      }
    },
      React.createElement('p', null, '🌾 KrishiQuery - Empowering Indian Farmers with New Technology'),
      React.createElement('p', null, '© 2026 KrishiQuery | Support: 1800-XXX-XXXX')
    )
  );
};

export default Dashboard;