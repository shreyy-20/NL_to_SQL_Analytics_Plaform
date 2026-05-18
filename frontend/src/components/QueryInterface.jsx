import React, { useState, useRef, useEffect } from 'react';
import { queryService } from '../services/api';

const QueryInterface = () => {
  const [phone, setPhone] = useState('9876543210');
  const [question, setQuestion] = useState('');
  const [language, setLanguage] = useState('hi');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [recordingStatus, setRecordingStatus] = useState('');
  const [isMobile, setIsMobile] = useState(false);
  
  const recognitionRef = useRef(null);

  // Detect mobile device
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent));
    };
    checkMobile();
    // Also check on resize
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

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
      setRecordingStatus(`✅ Heard: "${transcript.substring(0, 50)}${transcript.length > 50 ? '...' : ''}"`);
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
      'hi': 'hi-IN',
      'or': 'or-IN',
      'en': 'en-IN'
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
      
      if (res.data && res.data.answer && window.speechSynthesis) {
        const utterance = new SpeechSynthesisUtterance(res.data.answer);
        utterance.lang = getSpeechLanguage(language);
        utterance.rate = 0.9;
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

  // Responsive styles for mobile
  const styles = {
    container: {
      padding: isMobile ? '16px' : '24px',
      maxWidth: '100%',
      width: '100%',
      margin: '0 auto',
      fontFamily: "'Segoe UI', 'Nirmala UI', 'Noto Sans Devanagari', 'Kalinga', sans-serif",
      background: 'linear-gradient(135deg, #f5f5dc 0%, #e8f5e9 100%)',
      minHeight: '100vh',
      boxSizing: 'border-box'
    },
    header: {
      marginBottom: isMobile ? '20px' : '30px',
      textAlign: 'center'
    },
    title: {
      fontSize: isMobile ? '28px' : '36px',
      color: '#2e7d32',
      marginBottom: '8px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '10px',
      flexWrap: 'wrap'
    },
    subtitle: {
      fontSize: isMobile ? '13px' : '16px',
      color: '#666',
      marginBottom: '8px',
      lineHeight: '1.4',
      padding: '0 10px'
    },
    queryCard: {
      background: 'white',
      borderRadius: isMobile ? '16px' : '20px',
      padding: isMobile ? '20px' : '30px',
      boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
      marginBottom: '20px'
    },
    formGroup: {
      marginBottom: isMobile ? '18px' : '25px'
    },
    label: {
      display: 'block',
      marginBottom: '8px',
      fontWeight: 'bold',
      color: '#333',
      fontSize: isMobile ? '13px' : '14px'
    },
    inputWrapper: {
      position: 'relative',
      display: 'flex',
      gap: '10px',
      alignItems: 'center',
      flexWrap: isMobile ? 'wrap' : 'nowrap'
    },
    inputIcon: {
      position: 'absolute',
      left: '12px',
      top: '50%',
      transform: 'translateY(-50%)',
      fontSize: isMobile ? '16px' : '18px'
    },
    input: {
      flex: 1,
      width: '100%',
      padding: isMobile ? '12px 16px 12px 40px' : '14px 16px 14px 45px',
      border: '2px solid #e0e0e0',
      borderRadius: '12px',
      fontSize: isMobile ? '14px' : '16px',
      transition: 'all 0.3s ease',
      outline: 'none',
      fontFamily: 'inherit',
      boxSizing: 'border-box',
      WebkitAppearance: 'none'
    },
    select: {
      width: '100%',
      padding: isMobile ? '12px 14px' : '14px 16px',
      border: '2px solid #e0e0e0',
      borderRadius: '12px',
      fontSize: isMobile ? '14px' : '16px',
      transition: 'all 0.3s ease',
      outline: 'none',
      fontFamily: 'inherit',
      background: 'white',
      cursor: 'pointer',
      WebkitAppearance: 'none'
    },
    textareaWrapper: {
      position: 'relative'
    },
    textarea: {
      width: '100%',
      padding: isMobile ? '12px 50px 12px 14px' : '14px 50px 14px 16px',
      border: '2px solid #e0e0e0',
      borderRadius: '12px',
      fontSize: isMobile ? '14px' : '16px',
      transition: 'all 0.3s ease',
      outline: 'none',
      fontFamily: 'inherit',
      resize: 'vertical',
      boxSizing: 'border-box',
      minHeight: isMobile ? '80px' : '100px'
    },
    micIconOverlay: {
      position: 'absolute',
      right: '12px',
      bottom: '12px',
      background: isListening ? '#f44336' : '#ff8f00',
      borderRadius: '50%',
      width: isMobile ? '40px' : '36px',
      height: isMobile ? '40px' : '36px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      cursor: 'pointer',
      border: 'none',
      color: 'white',
      fontSize: isMobile ? '18px' : '16px',
      transition: 'all 0.3s ease',
      boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
    },
    recordingStatus: {
      marginTop: '10px',
      padding: '10px',
      borderRadius: '8px',
      fontSize: isMobile ? '11px' : '13px',
      textAlign: 'center',
      background: isListening ? '#fff3e0' : '#e8f5e9',
      color: isListening ? '#e65100' : '#2e7d32',
      wordBreak: 'break-word'
    },
    sampleSection: {
      marginBottom: '20px'
    },
    sampleTitle: {
      fontSize: isMobile ? '13px' : '14px',
      fontWeight: 'bold',
      color: '#333',
      marginBottom: '10px',
      display: 'flex',
      alignItems: 'center',
      gap: '6px'
    },
    sampleGrid: {
      display: 'grid',
      gridTemplateColumns: isMobile ? '1fr' : 'repeat(auto-fit, minmax(250px, 1fr))',
      gap: '10px'
    },
    sampleButton: {
      padding: isMobile ? '10px 14px' : '12px 16px',
      background: '#f5f5f5',
      border: '1px solid #e0e0e0',
      borderRadius: '10px',
      cursor: 'pointer',
      fontSize: isMobile ? '12px' : '13px',
      textAlign: 'left',
      transition: 'all 0.3s ease',
      fontFamily: 'inherit',
      color: '#333',
      width: '100%',
      wordBreak: 'break-word',
      lineHeight: '1.4'
    },
    submitButton: {
      width: '100%',
      padding: isMobile ? '14px' : '16px',
      background: 'linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '12px',
      cursor: 'pointer',
      fontSize: isMobile ? '16px' : '18px',
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
      borderRadius: isMobile ? '16px' : '20px',
      padding: isMobile ? '18px' : '25px',
      border: '1px solid #a5d6a7',
      animation: 'fadeIn 0.5s ease'
    },
    responseHeader: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      marginBottom: '12px',
      flexWrap: 'wrap',
      gap: '8px'
    },
    responseTitle: {
      fontSize: isMobile ? '16px' : '18px',
      fontWeight: 'bold',
      color: '#2e7d32',
      margin: 0,
      display: 'flex',
      alignItems: 'center',
      gap: '8px'
    },
    responseText: {
      fontSize: isMobile ? '14px' : '16px',
      lineHeight: '1.5',
      color: '#333',
      marginBottom: '12px',
      wordBreak: 'break-word'
    },
    responseMeta: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: '10px',
      paddingTop: '10px',
      borderTop: '1px solid #a5d6a7',
      fontSize: isMobile ? '10px' : '12px',
      color: '#666'
    },
    metaBadge: {
      background: 'white',
      padding: '4px 10px',
      borderRadius: '20px',
      display: 'inline-flex',
      alignItems: 'center',
      gap: '4px'
    },
    voiceHint: {
      textAlign: 'center',
      marginTop: '16px',
      padding: '10px',
      background: '#fff3e0',
      borderRadius: '12px',
      fontSize: isMobile ? '11px' : '13px',
      color: '#e65100'
    }
  };

  // Add keyframe animation
  useEffect(() => {
    const styleSheet = document.createElement("style");
    styleSheet.textContent = `
      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
      }
      @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
      }
      input, textarea, select, button {
        font-size: 16px !important; /* Prevents zoom on iOS */
      }
      button {
        touch-action: manipulation;
      }
    `;
    document.head.appendChild(styleSheet);
    return () => document.head.removeChild(styleSheet);
  }, []);

  const handleInputFocus = (e) => {
    e.target.style.borderColor = '#2e7d32';
    e.target.style.boxShadow = '0 0 0 3px rgba(46,125,50,0.1)';
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
        React.createElement('h1', { style: { margin: 0, fontSize: 'inherit' } }, 'Ask KrishiQuery'),
        React.createElement('span', null, '🌾')
      ),
      React.createElement('p', { style: styles.subtitle },
        isMobile ? 'Ask using VOICE or text in हिन्दी, ଓଡ଼ିଆ, English' : 'Ask questions using VOICE or text in हिन्दी, ଓଡ଼ିଆ, or English'
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
            placeholder: 'Enter 10-digit number',
            inputMode: 'numeric',
            pattern: '[0-9]*'
          })
        )
      ),

      // Language Selector
      React.createElement('div', { style: styles.formGroup },
        React.createElement('label', { style: styles.label }, '🌐 Language'),
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
            rows: isMobile ? 3 : 4,
            style: styles.textarea,
            placeholder: 'Type here... or tap the microphone to speak'
          }),
          React.createElement('button', {
            onClick: startVoiceInput,
            style: styles.micIconOverlay,
            onMouseEnter: (e) => e.currentTarget.style.transform = 'scale(1.05)',
            onMouseLeave: (e) => e.currentTarget.style.transform = 'scale(1)',
            onTouchStart: (e) => e.currentTarget.style.transform = 'scale(0.95)',
            onTouchEnd: (e) => e.currentTarget.style.transform = 'scale(1)'
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
          React.createElement('span', null, 'Sample Questions')
        ),
        React.createElement('div', { style: styles.sampleGrid },
          (sampleQuestions[language] || sampleQuestions.hi).slice(0, isMobile ? 3 : 4).map((q, idx) =>
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
            }, q.length > 50 ? q.substring(0, 47) + '...' : q)
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
          }
        },
        onMouseLeave: (e) => {
          e.currentTarget.style.transform = 'translateY(0)';
        },
        onTouchStart: (e) => e.currentTarget.style.transform = 'scale(0.98)',
        onTouchEnd: (e) => e.currentTarget.style.transform = 'scale(1)',
        style: { ...styles.submitButton, ...(loading ? styles.submitButtonDisabled : {}) }
      },
        loading ? '⏳ Processing...' : '🔊 Ask KrishiQuery'
      ),

      // Voice Hint
      React.createElement('div', { style: styles.voiceHint },
        React.createElement('span', null, '🎙️ '),
        React.createElement('span', null, isMobile ? 'Tap the 🎙️ to speak your question' : 'Click the microphone icon to speak your question')
      )
    ),

    // Response Section
    response && React.createElement('div', { style: styles.responseCard },
      React.createElement('div', { style: styles.responseHeader },
        React.createElement('div', { style: styles.responseTitle },
          React.createElement('span', null, '📝'),
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
        React.createElement('span', { 
          style: { ...styles.metaBadge, cursor: 'pointer' }, 
          onClick: () => {
            if (response.answer && window.speechSynthesis) {
              const utterance = new SpeechSynthesisUtterance(response.answer);
              utterance.lang = getSpeechLanguage(language);
              utterance.rate = 0.9;
              window.speechSynthesis.speak(utterance);
            }
          },
          onTouchStart: (e) => e.currentTarget.style.transform = 'scale(0.95)',
          onTouchEnd: (e) => e.currentTarget.style.transform = 'scale(1)'
        },
          React.createElement('span', null, '🔊'),
          React.createElement('span', null, 'Listen')
        )
      )
    )
  );
};

export default QueryInterface;