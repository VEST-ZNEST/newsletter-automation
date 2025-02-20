import React, { useState } from 'react';
import './App.css';
import zNestLogo from './assets/znest-logo.png'; // Adjust the path as necessary

const App: React.FC = () => {
  const [date, setDate] = useState('');
  const [htmlContent, setHtmlContent] = useState<string | null>(null);
  const [numHeadlines, setNumHeadlines] = useState<number>(5); // Default number of headlines

  // Get today's date in the format YYYY-MM-DD
  const today = new Date().toISOString().split('T')[0];

  const handleGetHtmlBlock = () => {
    const content = `Date: ${date}\nNumber of Headlines: ${numHeadlines}`;
    setHtmlContent(content);
    console.log('Content:', content);
  };

  const handleRegenerate = () => {
    console.log('Regenerate button clicked');
    // Add logic for regenerating content
  };

  const handleScheduleSend = () => {
    console.log('Schedule send button clicked');
    // Add logic for scheduling send
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', height: '100vh', width: '100%' }}>
      <img src={zNestLogo} alt="Znest Logo" style={{ marginBottom: '20px', width: '150px' }} />
      <div className="centered-content" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', backgroundColor: '#f0f0f0', padding: '20px', borderRadius: '8px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '10px' }}>
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            max={today}
            style={{ marginBottom: '10px' }}
          />
          <label style={{ marginBottom: '5px', color: 'black' }}>Num of headlines:</label>
          <input
            type="number"
            value={numHeadlines}
            onChange={(e) => setNumHeadlines(Number(e.target.value))}
            min={1}
            style={{ width: '100px' }}
            placeholder="Headlines"
          />
        </div>
        <button style={{ marginBottom: '10px' }} onClick={handleGetHtmlBlock}>
          Get Headlines
        </button>
        {htmlContent && (
        <div style={{ marginTop: '10px', marginBottom: '10px', padding: '10px', border: '1px solid #ccc', backgroundColor: 'black', width: '80%', textAlign: 'left' }}>
          <h3>HTML Block</h3>
          <pre style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>{htmlContent}</pre>
        </div>
      )}
        <button style={{ marginBottom: '10px' }} onClick={handleRegenerate}>
          Regenerate
        </button>
        <button style={{ marginBottom: '10px' }} onClick={handleScheduleSend}>
          Schedule send
        </button>
      </div>
    </div>
  );
};

export default App;
