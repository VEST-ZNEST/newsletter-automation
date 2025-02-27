import React, { useState } from 'react';
import './App.css';
import zNestLogo from './assets/znest-logo.png'; // Adjust the path as necessary
import axios from 'axios';

const App: React.FC = () => {
  // Get today's date in the format YYYY-MM-DD
  const today = new Date().toISOString().split('T')[0];

  const [date, setDate] = useState(today);
  const [headlines, setHeadlines] = useState<string[]>([]);
  const [htmlContent, setHtmlContent] = useState<string | null>(null);
  const [showHtml, setShowHtml] = useState(false);

  // Store input values separately until "Generate Newsletter" is clicked
  const [inputDate, setInputDate] = useState(today);
  const [inputEndDate, setInputEndDate] = useState(today);

  const handleGenerateNewsletter = () => {
    if (!inputDate) {
      return;
    }

    setDate(inputDate);

    axios
      .get("http://localhost:5001/api/ai-news", {
        params: {
          //date_from: inputDate,
          date_to: inputEndDate,
          numHeadlines: 5,
        },
      })
      .then((response) => {
        const fetchedHeadlines: string[] = response.data.headlines;
        setHeadlines(fetchedHeadlines);
        
        // Generate HTML newsletter content
        const content = `
        <div>
          <ul style="list-style-type: disc; padding-left: 20px;">
            ${fetchedHeadlines.map(headline => `<li style="margin-bottom: 10px;"><strong style="color: blue;">${headline}</strong></li>`).join('')}
          </ul>
        </div>
      `;
        setHtmlContent(content);
      });
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', height: '100vh', width: '100%' }}>
      <img src={zNestLogo} alt="Znest Logo" style={{ marginBottom: '20px', width: '150px' }} />
      <div className="centered-content" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', backgroundColor: '#f0f0f0', padding: '20px', borderRadius: '8px' }}>
        
        {/* Date Range Input */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '10px' }}>
          <label style={{ marginBottom: '5px', color: 'black' }}>Start Date:</label>
          <input
            type="date"
            value={inputDate}
            onChange={(e) => setInputDate(e.target.value)}
            max={today}
            style={{ marginBottom: '10px' }}
          />
          <label style={{ marginBottom: '5px', color: 'black' }}>End Date:</label>
          <input
            type="date"
            value={inputEndDate}
            onChange={(e) => setInputEndDate(e.target.value)}
            max={today}
            style={{ marginBottom: '10px' }}
          />
        </div>

        <button style={{ marginBottom: '10px' }} onClick={handleGenerateNewsletter}>
          Generate Newsletter
        </button>

        {/* Conditionally render either headlines or HTML block */}
        {htmlContent && showHtml ? (
          <div style={{ marginTop: '10px', marginBottom: '10px', padding: '10px', border: '1px solid #ccc', backgroundColor: 'black', width: '100%', textAlign: 'left', color: 'white' }}>
            <pre style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>{htmlContent}</pre>
          </div>
        ) : (
          headlines.length > 0 && (
            <div style={{ marginTop: '10px', marginBottom: '10px', padding: '10px', backgroundColor: 'white', border: '1px solid #ccc', width: '100%', textAlign: 'left' }}>
              <ul>
                {headlines.map((headline, index) => (
                  <li key={index} dangerouslySetInnerHTML={{ __html: headline }} />
                ))}
              </ul>
            </div>
          )
        )}

        {/* Toggle switch with label */}
        {htmlContent && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px', marginBottom: '10px' }}>
            <label style={{ fontSize: '14px', color: 'black' }}>Show HTML</label>
            <label className="switch">
              <input type="checkbox" checked={showHtml} onChange={() => setShowHtml(prev => !prev)} />
              <span className="slider round"></span>
            </label>
          </div>
        )}

        <button style={{ marginBottom: '10px' }} onClick={() => console.log('Regenerate button clicked')}>
          Regenerate
        </button>
        <button style={{ marginBottom: '10px' }} onClick={() => console.log('Schedule send button clicked')}>
          Schedule send
        </button>
      </div>
    </div>
  );
};

export default App;