import React from 'react';

const Dashboard = () => {
  return React.createElement('div', { style: { padding: '20px' } },
    React.createElement('h1', null, 'KrishiQuery Dashboard'),
    React.createElement('p', null, 'Welcome to the KrishiQuery system!'),
    React.createElement('p', null, 'Use the Query page to ask questions in Hindi, Odia, or English.'),
    React.createElement('hr'),
    React.createElement('h3', null, 'Sample Queries:'),
    React.createElement('ul', null,
      React.createElement('li', null, 'मेरी PM-KISAN की किस्त आई क्या?'),
      React.createElement('li', null, 'भुवनेश्वर मंडी में धान का भाव क्या है?'),
      React.createElement('li', null, 'मेरी मिट्टी परीक्षण रिपोर्ट दिखाओ'),
      React.createElement('li', null, 'अगले हफ्ते बारिश होगी क्या?')
    )
  );
};

export default Dashboard;
