import React, { useState, useRef } from 'react';
import { queryService } from '../services/api';

const QueryInterface = () => {
  const [phone, setPhone] = useState('9876543210');
  const [question, setQuestion] = useState('');
  const [language, setLanguage] = useState('hi');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [recordingStatus, setRecordingStatus] = useState('');
  
  const recognitionRef = useRef(null);

  // Initialize speech recognition
  const initSpeechRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      alert('Sorry, your browser does not support voice input. Please use Chrome, Edge, or Safari.');
      return null;
    }
    
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = getSpeechLanguage(language);
    
    recognition.onstart = () => {
      setIsListening(true);
      setRecordingStatus('🎙️ Listening... Speak your question now');
    };
    
    recognition.onend = () => {
      setIsListening(false);
      setTimeout(() => setRecordingStatus(''), 2000);
    };
    
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setQuestion(transcript);
      setRecordingStatus(`✅ Heard: "${transcript}"`);
      setTimeout(() => setRecordingStatus(''), 3000);
    };
    
    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setRecordingStatus(`❌ Error: ${event.error}. Please try again`);
      setIsListening(false);
      setTimeout(() => setRecordingStatus(''), 3000);
    };
    
    return recognition;
  };
  
  const getSpeechLanguage = (lang) => {
    const langMap = {
      'hi': 'hi-IN',     // Hindi (India)
      'or': 'or-IN',     // Odia (India)
      'en': 'en-IN'      // English (India)
    };
    return langMap[lang] || 'hi-IN';
  };
  
  const startVoiceInput = () => {
    if (isListening) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      return;
    }
    
    const recognition = initSpeechRecognition();
    if (recognition) {
      recognitionRef.current = recognition;
      recognition.start();
    }
  };

  const askQuery = async () => {
    if (!question.trim()) {
      alert('Please enter a question or use voice input');
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
      
      // Optional: Text-to-speech for response
      if (res.data && res.data.answer && window.speechSynthesis) {
        const utterance = new SpeechSynthesisUtterance(res.data.answer);
        utterance.lang = getSpeechLanguage(language);
        utterance.rate = 0.9; // Slightly slower for better understanding
        window.speechSynthesis.speak(utterance);
      }
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

  const styles = {
    container: {
      padding: '24px',
      maxWidth: '900px',
      margin: '0 auto',
      fontFamily: "'Segoe UI', 'Nirmala UI', 'Noto Sans Devanagari', 'Kalinga', sans-serif",
      background: 'linear-gradient(135deg, #f5f5dc 0%, #e8f5e9 100%)',
      minHeight: '100vh'
    },
    header: {
      marginBottom: '30px',
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
      marginBottom: '10px'
    },
    queryCard: {
      background: 'white',
      borderRadius: '20px',
      padding: '30px',
      boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
      marginBottom: '30px'
    },
    formGroup: {
      marginBottom: '25px'
    },
    label: {
      display: 'block',
      marginBottom: '8px',
      fontWeight: 'bold',
      color: '#333',
      fontSize: '14px'
    },
    inputWrapper: {
      position: 'relative',
      display: 'flex',
      gap: '10px',
      alignItems: 'center'
    },
    inputIcon: {
      position: 'absolute',
      left: '12px',
      top: '50%',
      transform: 'translateY(-50%)',
      fontSize: '18px'
    },
    input: {
      flex: 1,
      padding: '14px 16px 14px 45px',
      border: '2px solid #e0e0e0',
      borderRadius: '12px',
      fontSize: '16px',
      transition: 'all 0.3s ease',
      outline: 'none',
      fontFamily: 'inherit',
      boxSizing: 'border-box'
    },
    voiceButton: {
      padding: '14px 20px',
      background: isListening ? '#f44336' : '#ff8f00',
      color: 'white',
      border: 'none',
      borderRadius: '12px',
      cursor: 'pointer',
      fontSize: '18px',
      transition: 'all 0.3s ease',
      animation: isListening ? 'pulse 1.5s infinite' : 'none'
    },
    select: {
      width: '100%',
      padding: '14px 16px',
      border: '2px solid #e0e0e0',
      borderRadius: '12px',
      fontSize: '16px',
      transition: 'all 0.3s ease',
      outline: 'none',
      fontFamily: 'inherit',
      background: 'white',
      cursor: 'pointer'
    },
    textareaWrapper: {
      position: 'relative'
    },
    textarea: {
      width: '100%',
      padding: '14px 16px',
      border: '2px solid #e0e0e0',
      borderRadius: '12px',
      fontSize: '16px',
      transition: 'all 0.3s ease',
      outline: 'none',
      fontFamily: 'inherit',
      resize: 'vertical',
      boxSizing: 'border-box',
      paddingRight: '50px'
    },
    micIconOverlay: {
      position: 'absolute',
      right: '12px',
      bottom: '12px',
      background: '#ff8f00',
      borderRadius: '50%',
      width: '36px',
      height: '36px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      cursor: 'pointer',
      border: 'none',
      color: 'white',
      fontSize: '18px'
    },
    inputFocus: {
      borderColor: '#2e7d32',
      boxShadow: '0 0 0 3px rgba(46,125,50,0.1)'
    },
    recordingStatus: {
      marginTop: '10px',
      padding: '10px',
      borderRadius: '8px',
      fontSize: '13px',
      textAlign: 'center',
      background: isListening ? '#fff3e0' : '#e8f5e9',
      color: isListening ? '#e65100' : '#2e7d32'
    },
    sampleSection: {
      marginBottom: '25px'
    },
    sampleTitle: {
      fontSize: '14px',
      fontWeight: 'bold',
      color: '#333',
      marginBottom: '12px',
      display: 'flex',
      alignItems: 'center',
      gap: '8px'
    },
    sampleGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
      gap: '12px'
    },
    sampleButton: {
      padding: '12px 16px',
      background: '#f5f5f5',
      border: '1px solid #e0e0e0',
      borderRadius: '10px',
      cursor: 'pointer',
      fontSize: '13px',
      textAlign: 'left',
      transition: 'all 0.3s ease',
      fontFamily: 'inherit',
      color: '#333'
    },
    submitButton: {
      width: '100%',
      padding: '16px',
      background: 'linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '12px',
      cursor: 'pointer',
      fontSize: '18px',
      fontWeight: 'bold',
      transition: 'all 0.3s ease',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '10px'
    },
    submitButtonDisabled: {
      opacity: 0.6,
      cursor: 'not-allowed'
    },
    responseCard: {
      background: 'linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%)',
      borderRadius: '20px',
      padding: '25px',
      border: '1px solid #a5d6a7',
      animation: 'fadeIn 0.5s ease'
    },
    responseHeader: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      marginBottom: '15px',
      flexWrap: 'wrap',
      gap: '10px'
    },
    responseTitle: {
      fontSize: '18px',
      fontWeight: 'bold',
      color: '#2e7d32',
      margin: 0,
      display: 'flex',
      alignItems: 'center',
      gap: '8px'
    },
    responseIcon: {
      fontSize: '24px'
    },
    responseText: {
      fontSize: '16px',
      lineHeight: '1.6',
      color: '#333',
      marginBottom: '15px'
    },
    responseMeta: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: '15px',
      paddingTop: '12px',
      borderTop: '1px solid #a5d6a7',
      fontSize: '12px',
      color: '#666'
    },
    metaBadge: {
      background: 'white',
      padding: '4px 12px',
      borderRadius: '20px',
      display: 'inline-flex',
      alignItems: 'center',
      gap: '6px'
    },
    voiceHint: {
      textAlign: 'center',
      marginTop: '20px',
      padding: '12px',
      background: '#fff3e0',
      borderRadius: '12px',
      fontSize: '13px',
      color: '#e65100'
    }
  };

  // Add keyframe animation for pulse effect
  const styleSheet = document.createElement("style");
  styleSheet.textContent = `
    @keyframes pulse {
      0% { transform: scale(1); opacity: 1; }
      50% { transform: scale(1.05); opacity: 0.8; }
      100% { transform: scale(1); opacity: 1; }
    }
  `;
  document.head.appendChild(styleSheet);

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
        React.createElement('span', null, '🎤'),
        React.createElement('h1', { style: { margin: 0 } }, 'Ask KrishiQuery'),
        React.createElement('span', null, '🌾')
      ),
      React.createElement('p', { style: styles.subtitle },
        'Ask questions using VOICE or text in हिन्दी, ଓଡ଼ିଆ, or English'
      )
    ),

    // Main Query Card
    React.createElement('div', { style: styles.queryCard },
      // Phone Number
      React.createElement('div', { style: styles.formGroup },
        React.createElement('label', { style: styles.label }, '📱 Phone Number'),
        React.createElement('div', { style: styles.inputWrapper },
          React.createElement('span', { style: styles.inputIcon }, '📞'),
          React.createElement('input', {
            type: 'tel',
            value: phone,
            onChange: (e) => setPhone(e.target.value),
            onFocus: handleInputFocus,
            onBlur: handleInputBlur,
            style: styles.input,
            placeholder: 'Enter 10-digit mobile number'
          })
        )
      ),

      // Language Selector
      React.createElement('div', { style: styles.formGroup },
        React.createElement('label', { style: styles.label }, '🌐 Language (for voice input)'),
        React.createElement('select', {
          value: language,
          onChange: (e) => setLanguage(e.target.value),
          onFocus: handleInputFocus,
          onBlur: handleInputBlur,
          style: styles.select
        },
          React.createElement('option', { value: 'hi' }, 'हिंदी (Hindi)'),
          React.createElement('option', { value: 'or' }, 'ଓଡ଼ିଆ (Odia)'),
          React.createElement('option', { value: 'en' }, 'English')
        )
      ),

      // Question Input with Voice Button
      React.createElement('div', { style: styles.formGroup },
        React.createElement('label', { style: styles.label }, '💬 Your Question'),
        React.createElement('div', { style: styles.textareaWrapper },
          React.createElement('textarea', {
            value: question,
            onChange: (e) => setQuestion(e.target.value),
            onFocus: handleInputFocus,
            onBlur: handleInputBlur,
            rows: 4,
            style: styles.textarea,
            placeholder: 'Type your question here... or click the microphone to speak'
          }),
          React.createElement('button', {
            onClick: startVoiceInput,
            style: styles.micIconOverlay,
            onMouseEnter: (e) => e.currentTarget.style.transform = 'scale(1.1)',
            onMouseLeave: (e) => e.currentTarget.style.transform = 'scale(1)',
            title: 'Click to speak your question'
          },
            React.createElement('span', null, isListening ? '⏹️' : '🎙️')
          )
        ),
        recordingStatus && React.createElement('div', { style: styles.recordingStatus },
          React.createElement('span', null, recordingStatus)
        )
      ),

      // Sample Questions
      React.createElement('div', { style: styles.sampleSection },
        React.createElement('div', { style: styles.sampleTitle },
          React.createElement('span', null, '📋'),
          React.createElement('span', null, 'Sample Questions (click to use)')
        ),
        React.createElement('div', { style: styles.sampleGrid },
          (sampleQuestions[language] || sampleQuestions.hi).map((q, idx) =>
            React.createElement('button', {
              key: idx,
              onClick: () => setQuestion(q),
              onMouseEnter: (e) => {
                e.currentTarget.style.background = '#e8f5e9';
                e.currentTarget.style.borderColor = '#2e7d32';
              },
              onMouseLeave: (e) => {
                e.currentTarget.style.background = '#f5f5f5';
                e.currentTarget.style.borderColor = '#e0e0e0';
              },
              style: styles.sampleButton
            }, q)
          )
        )
      ),

      // Submit Button
      React.createElement('button', {
        onClick: askQuery,
        disabled: loading,
        onMouseEnter: (e) => {
          if (!loading) {
            e.currentTarget.style.transform = 'translateY(-2px)';
            e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
          }
        },
        onMouseLeave: (e) => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
        },
        style: { ...styles.submitButton, ...(loading ? styles.submitButtonDisabled : {}) }
      },
        loading ? '⏳ Processing...' : '🔊 Ask KrishiQuery'
      ),

      // Voice Hint
      React.createElement('div', { style: styles.voiceHint },
        React.createElement('span', null, '🎙️ '),
        React.createElement('span', null, 'Click the microphone icon to speak your question in ', 
          language === 'hi' ? 'Hindi' : language === 'or' ? 'Odia' : 'English')
      )
    ),

    // Response Section
    response && React.createElement('div', { style: styles.responseCard },
      React.createElement('div', { style: styles.responseHeader },
        React.createElement('div', { style: styles.responseTitle },
          React.createElement('span', { style: styles.responseIcon }, '📝'),
          React.createElement('span', null, 'Response')
        ),
        response.intent && React.createElement('span', { style: styles.metaBadge },
          React.createElement('span', null, '🎯'),
          React.createElement('span', null, response.intent)
        )
      ),
      React.createElement('div', { style: styles.responseText },
        response.answer || response.error || 'No response'
      ),
      React.createElement('div', { style: styles.responseMeta },
        response.intent && React.createElement('span', { style: styles.metaBadge },
          React.createElement('span', null, '📊'),
          React.createElement('span', null, `Confidence: ${Math.round((response.confidence || 0) * 100)}%`)
        ),
        response.processing_time_ms && React.createElement('span', { style: styles.metaBadge },
          React.createElement('span', null, '⏱️'),
          React.createElement('span', null, `${response.processing_time_ms}ms`)
        ),
        React.createElement('span', { style: styles.metaBadge },
          React.createElement('span', null, '🤖'),
          React.createElement('span', null, 'KrishiQuery AI')
        ),
        React.createElement('span', { style: { ...styles.metaBadge, cursor: 'pointer' }, onClick: () => {
          if (response.answer && window.speechSynthesis) {
            const utterance = new SpeechSynthesisUtterance(response.answer);
            utterance.lang = getSpeechLanguage(language);
            utterance.rate = 0.9;
            window.speechSynthesis.speak(utterance);
          }
        } },
          React.createElement('span', null, '🔊'),
          React.createElement('span', null, 'Listen Again')
        )
      )
    )
  );
};

export default QueryInterface;