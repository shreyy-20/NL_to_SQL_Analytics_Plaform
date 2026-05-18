import React, { useState, useEffect } from 'react';

const Dashboard = () => {
  const [isMobile, setIsMobile] = useState(false);

  // Detect mobile device
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || window.innerWidth <= 768);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const styles = {
    container: {
      padding: isMobile ? '16px' : '24px',
      maxWidth: '1200px',
      margin: '0 auto',
      fontFamily: "'Segoe UI', 'Nirmala UI', 'Noto Sans Devanagari', 'Kalinga', sans-serif",
      background: 'linear-gradient(135deg, #f5f5dc 0%, #e8f5e9 100%)',
      minHeight: '100vh',
      boxSizing: 'border-box'
    },
    header: {
      marginBottom: isMobile ? '20px' : '40px',
      textAlign: 'center'
    },
    title: {
      fontSize: isMobile ? '28px' : '42px',
      color: '#2e7d32',
      marginBottom: '8px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '10px',
      flexWrap: 'wrap'
    },
    subtitle: {
      fontSize: isMobile ? '13px' : '18px',
      color: '#666',
      lineHeight: '1.4'
    },
    statsGrid: {
      display: 'grid',
      gridTemplateColumns: isMobile ? '1fr' : 'repeat(auto-fit, minmax(250px, 1fr))',
      gap: isMobile ? '12px' : '20px',
      marginBottom: isMobile ? '24px' : '40px'
    },
    statCard: {
      background: 'white',
      padding: isMobile ? '16px' : '25px',
      borderRadius: isMobile ? '12px' : '15px',
      textAlign: 'center',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      transition: 'transform 0.3s ease',
      cursor: 'pointer'
    },
    statNumber: {
      fontSize: isMobile ? '28px' : '36px',
      fontWeight: 'bold',
      color: '#2e7d32',
      marginBottom: '8px'
    },
    statLabel: {
      fontSize: isMobile ? '11px' : '14px',
      color: '#666',
      textTransform: 'uppercase',
      letterSpacing: '0.5px'
    },
    statIcon: {
      fontSize: isMobile ? '28px' : '40px',
      marginBottom: '8px'
    },
    sectionTitle: {
      fontSize: isMobile ? '20px' : '24px',
      color: '#2e7d32',
      marginBottom: isMobile ? '12px' : '20px',
      paddingBottom: '8px',
      borderBottom: '3px solid #ff8f00',
      display: 'inline-block'
    },
    featuresGrid: {
      display: 'grid',
      gridTemplateColumns: isMobile ? 'repeat(2, 1fr)' : 'repeat(auto-fit, minmax(200px, 1fr))',
      gap: isMobile ? '12px' : '20px',
      marginTop: '20px',
      marginBottom: isMobile ? '24px' : '40px'
    },
    featureCard: {
      background: 'white',
      padding: isMobile ? '14px' : '20px',
      borderRadius: '12px',
      textAlign: 'center',
      boxShadow: '0 2px 6px rgba(0,0,0,0.1)',
      transition: 'all 0.3s ease'
    },
    featureIcon: {
      fontSize: isMobile ? '28px' : '40px',
      marginBottom: '8px'
    },
    featureTitle: {
      fontSize: isMobile ? '13px' : '16px',
      fontWeight: 'bold',
      color: '#2e7d32',
      marginBottom: '6px'
    },
    featureDesc: {
      fontSize: isMobile ? '10px' : '12px',
      color: '#666',
      lineHeight: '1.3'
    },
    querySection: {
      marginBottom: isMobile ? '24px' : '40px'
    },
    sampleGrid: {
      display: 'grid',
      gridTemplateColumns: isMobile ? '1fr' : 'repeat(auto-fit, minmax(300px, 1fr))',
      gap: isMobile ? '10px' : '15px',
      marginTop: '15px'
    },
    sampleCard: {
      background: 'white',
      padding: isMobile ? '14px' : '20px',
      borderRadius: '12px',
      boxShadow: '0 2px 6px rgba(0,0,0,0.1)',
      transition: 'all 0.3s ease',
      cursor: 'pointer',
      borderLeft: `4px solid #ff8f00`
    },
    sampleText: {
      fontSize: isMobile ? '13px' : '16px',
      color: '#333',
      marginBottom: '8px',
      lineHeight: '1.4',
      wordBreak: 'break-word'
    },
    sampleLang: {
      fontSize: isMobile ? '10px' : '12px',
      color: '#ff8f00',
      fontWeight: 'bold'
    },
    ctaCard: {
      background: 'linear-gradient(135deg, #ff8f00 0%, #ff6f00 100%)',
      borderRadius: isMobile ? '12px' : '15px',
      padding: isMobile ? '18px' : '25px',
      textAlign: 'center',
      cursor: 'pointer',
      transition: 'transform 0.3s ease'
    },
    ctaIcon: {
      fontSize: isMobile ? '36px' : '48px',
      marginBottom: '8px'
    },
    ctaTitle: {
      fontSize: isMobile ? '18px' : '24px',
      color: 'white',
      marginBottom: '8px'
    },
    ctaText: {
      fontSize: isMobile ? '12px' : '14px',
      color: 'white',
      opacity: 0.95
    },
    footer: {
      marginTop: isMobile ? '30px' : '40px',
      padding: isMobile ? '15px' : '20px',
      textAlign: 'center',
      borderTop: '1px solid #ddd',
      color: '#666',
      fontSize: isMobile ? '10px' : '12px'
    }
  };

  const handleQueryClick = (question) => {
    sessionStorage.setItem('prefilledQuestion', question);
    window.location.href = '/query';
  };

  const stats = [
    { icon: '👨‍🌾', number: '10,000+', label: 'Registered Farmers' },
    { icon: '💰', number: '₹50L+', label: 'Total Disbursed' },
    { icon: '💬', number: '25,000+', label: 'Queries Answered' },
    { icon: '🏪', number: '30+', label: 'Mandi Covered' }
  ];

  const features = [
    { icon: '💸', title: 'Payment Status', desc: 'PM-KISAN & KALIA updates' },
    { icon: '📊', title: 'Mandi Prices', desc: 'Real-time crop rates' },
    { icon: '🌱', title: 'Soil Health', desc: 'Test reports & advice' },
    { icon: '☀️', title: 'Weather Forecast', desc: '7-day prediction' }
  ];

  const queries = [
    { text: 'मेरी PM-KISAN की किस्त आई क्या?', lang: 'हिन्दी' },
    { text: 'भुवनेश्वर मंडी में धान का भाव क्या है?', lang: 'हिन्दी' },
    { text: 'मेरी मिट्टी परीक्षण रिपोर्ट दिखाओ', lang: 'हिन्दी' }
  ];

  if (isMobile) {
    queries.push({ text: 'अगले हफ्ते बारिश होगी क्या?', lang: 'हिन्दी' });
  }

  return React.createElement('div', { style: styles.container },
    React.createElement('div', { style: styles.header },
      React.createElement('div', { style: styles.title },
        React.createElement('span', null, '🌾'),
        React.createElement('h1', { style: { margin: 0, fontSize: 'inherit' } }, 'KrishiQuery'),
        React.createElement('span', null, '🇮🇳')
      ),
      React.createElement('p', { style: styles.subtitle },
        isMobile ? 'Voice-Based Agi-Query System' : 'Voice-Based Natural Language Query System for Indian Agriculture'
      ),
      React.createElement('p', { style: { ...styles.subtitle, fontSize: isMobile ? '11px' : '14px', marginTop: '5px' } },
        isMobile ? 'हिन्दी, ଓଡ଼ିଆ, English' : 'Ask questions in हिन्दी, ଓଡ଼ିଆ, or English'
      )
    ),

    React.createElement('div', { style: styles.statsGrid },
      stats.map((stat, index) =>
        React.createElement('div', { key: index, style: styles.statCard,
          onMouseEnter: (e) => e.currentTarget.style.transform = 'translateY(-3px)',
          onMouseLeave: (e) => e.currentTarget.style.transform = 'translateY(0)',
          onTouchStart: (e) => e.currentTarget.style.transform = 'scale(0.98)',
          onTouchEnd: (e) => e.currentTarget.style.transform = 'scale(1)'
        },
          React.createElement('div', { style: styles.statIcon }, stat.icon),
          React.createElement('div', { style: styles.statNumber }, stat.number),
          React.createElement('div', { style: styles.statLabel }, stat.label)
        )
      )
    ),

    React.createElement('div', null,
      React.createElement('h2', { style: styles.sectionTitle }, '✨ What We Offer'),
      React.createElement('div', { style: styles.featuresGrid },
        features.map((feature, index) =>
          React.createElement('div', { key: index, style: styles.featureCard,
            onMouseEnter: (e) => e.currentTarget.style.transform = 'translateY(-2px)',
            onMouseLeave: (e) => e.currentTarget.style.transform = 'translateY(0)'
          },
            React.createElement('div', { style: styles.featureIcon }, feature.icon),
            React.createElement('div', { style: styles.featureTitle }, feature.title),
            React.createElement('div', { style: styles.featureDesc }, feature.desc)
          )
        )
      )
    ),

    React.createElement('div', { style: styles.querySection },
      React.createElement('h2', { style: styles.sectionTitle }, '🎤 Try These Queries'),
      React.createElement('div', { style: styles.sampleGrid },
        queries.map((query, index) =>
          React.createElement('div', {
            key: index,
            style: styles.sampleCard,
            onClick: () => handleQueryClick(query.text),
            onMouseEnter: (e) => {
              e.currentTarget.style.transform = 'translateX(5px)';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
            },
            onMouseLeave: (e) => {
              e.currentTarget.style.transform = 'translateX(0)';
              e.currentTarget.style.boxShadow = '0 2px 6px rgba(0,0,0,0.1)';
            },
            onTouchStart: (e) => e.currentTarget.style.transform = 'scale(0.98)',
            onTouchEnd: (e) => e.currentTarget.style.transform = 'scale(1)'
          },
            React.createElement('div', { style: styles.sampleText }, query.text),
            React.createElement('div', { style: styles.sampleLang }, query.lang)
          )
        )
      )
    ),

    React.createElement('div', {
      style: styles.ctaCard,
      onClick: () => window.location.href = '/query',
      onMouseEnter: (e) => e.currentTarget.style.transform = 'scale(1.02)',
      onMouseLeave: (e) => e.currentTarget.style.transform = 'scale(1)',
      onTouchStart: (e) => e.currentTarget.style.transform = 'scale(0.98)',
      onTouchEnd: (e) => e.currentTarget.style.transform = 'scale(1)'
    },
      React.createElement('div', { style: styles.ctaIcon }, '🔊'),
      React.createElement('h3', { style: styles.ctaTitle }, 'Have a Question?'),
      React.createElement('p', { style: styles.ctaText },
        isMobile ? 'Tap to ask in your language' : 'Click here to ask in Hindi, Odia, or English'
      )
    ),

    React.createElement('div', { style: styles.footer },
      React.createElement('p', null, '🌾 KrishiQuery - Empowering Indian Farmers'),
      React.createElement('p', null, '© 2026 KrishiQuery | Support: 1800-XXX-XXXX')
    )
  );
};

export default Dashboard;