import React, { useState } from 'react';

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

    setLoading(true);
    setResponse(null);
    
    try {
      const res = await fetch('/api/queries/', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-API-Key': 'krishiquery_dev_key_2024'
        },
        body: JSON.stringify({
          question: question,
          phone_number: phone,
          language: language
        })
      });
      
      if (res.status === 401) {
        throw new Error('Invalid API key. Please check backend configuration.');
      }
      
      const data = await res.json();
      setResponse(data);
    } catch (error) {
      setResponse({ answer: `Error: ${error.message}` });
    } finally {
      setLoading(false);
    }
  };

  const sampleQuestions = {
    hi: ['???? PM-KISAN ?? ????? ?? ?????', '????????? ??? ??? ?? ??? ???? ???', '???? ?????? ?? ??????? ?????', '???? ????? ????? ???? ?????'],
    or: ['??? PM-KISAN ?????? ????? ???', '??????????? ???? ????? ?????'],
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
          <option value="hi">?????? (Hindi)</option>
          <option value="or">????? (Odia)</option>
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
