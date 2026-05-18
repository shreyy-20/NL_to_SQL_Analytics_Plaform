import React, { useState } from 'react';
import { queryService } from '../services/api';

const QueryInterface = () => {
  const [phone, setPhone] = useState('9876543210');
  const [question, setQuestion] = useState('');
  const [language, setLanguage] = useState('hi');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const askQuery = async () => {
    if (!question.trim()) {
      alert('Please enter a question');
      return;
    }

    if (!/^[6-9]\d{9}$/.test(phone)) {
      alert('Please enter a valid 10-digit Indian mobile number');
      return;
    }

    setLoading(true);
    setResponse(null);
    
    try {
      const res = await queryService.processQuery(question, phone, language);
      setResponse(res.data);
    } catch (error) {
      const backendMessage =
        error?.response?.data?.detail ||
        error?.response?.data?.error ||
        error?.response?.data?.answer ||
        error?.message ||
        'Unable to reach backend service.';

      const configuredApi =
        process.env.REACT_APP_API_URL || 'http://localhost:8000 (default fallback)';

      setResponse({
        answer: `Error: ${backendMessage}. API base: ${configuredApi}`
      });
    } finally {
      setLoading(false);
    }
  };

  const sampleQuestions = {
    hi: [
      'मेरी PM-KISAN की किस्त आई क्या?',
      'भुवनेश्वर मंडी में धान का भाव क्या है?',
      'मेरी मिट्टी परीक्षण रिपोर्ट दिखाओ',
      'अगले हफ्ते बारिश होगी क्या?'
    ],
    or: [
      'ମୋ PM-KISAN କିଷ୍ଟି ଆସିଛି କି?',
      'ଭୁବନେଶ୍ୱର ମଣ୍ଡିରେ ଧାନ ଦାମ କେତେ?'
    ],
    en: ['Did my PM-KISAN installment come?', 'What is the price of paddy in Bhubaneswar?', 'Show my soil health report', 'Will it rain next week?']
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px' }}>
      <h1>Ask KrishiQuery</h1>
      <p>Ask questions in Hindi, Odia, or English about payments, prices, soil, and weather.</p>
      
      <div style={{ marginBottom: '15px' }}>
        <label><strong>Phone Number:</strong></label><br />
        <input
          type="text"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          style={{ padding: '8px', width: '250px', marginTop: '5px', border: '1px solid #ccc', borderRadius: '4px' }}
        />
      </div>

      <div style={{ marginBottom: '15px' }}>
        <label><strong>Language:</strong></label><br />
        <select value={language} onChange={(e) => setLanguage(e.target.value)} style={{ padding: '8px', marginTop: '5px', width: '200px', border: '1px solid #ccc', borderRadius: '4px' }}>
          <option value="hi">हिंदी (Hindi)</option>
          <option value="or">ଓଡ଼ିଆ (Odia)</option>
          <option value="en">English</option>
        </select>
      </div>

      <div style={{ marginBottom: '15px' }}>
        <label><strong>Your Question:</strong></label><br />
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          rows="4"
          style={{ width: '100%', padding: '10px', marginTop: '5px', border: '1px solid #ccc', borderRadius: '4px' }}
          placeholder="Type your question here..."
        />
      </div>

      <div style={{ marginBottom: '15px' }}>
        <strong>Sample Questions:</strong>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginTop: '10px' }}>
          {(sampleQuestions[language] || sampleQuestions.hi).map((q, idx) => (
            <button
              key={idx}
              onClick={() => setQuestion(q)}
              style={{ padding: '5px 10px', background: '#e0e0e0', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}
            >
              {q.length > 40 ? q.substring(0, 40) + '...' : q}
            </button>
          ))}
        </div>
      </div>

      <button
        onClick={askQuery}
        disabled={loading}
        style={{
          background: '#2e7d32',
          color: 'white',
          padding: '12px 30px',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          fontSize: '16px',
          fontWeight: 'bold'
        }}
      >
        {loading ? 'Processing...' : 'Ask KrishiQuery'}
      </button>

      {response && (
        <div style={{ marginTop: '20px', padding: '15px', background: '#e8f5e9', borderRadius: '8px', border: '1px solid #c8e6c9' }}>
          <h3 style={{ marginTop: 0, color: '#2e7d32' }}>Response:</h3>
          <p style={{ fontSize: '16px', lineHeight: '1.5' }}>{response.answer || response.error || 'No response'}</p>
          {response.intent && (
            <small style={{ color: '#666' }}>
              Intent: {response.intent} | Confidence: {Math.round((response.confidence || 0) * 100)}% | Time: {response.processing_time_ms || 0}ms
            </small>
          )}
        </div>
      )}
    </div>
  );
};

export default QueryInterface;
