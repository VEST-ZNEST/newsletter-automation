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

  // Add a new state for editable HTML
  const [editableHtml, setEditableHtml] = useState<string>('');

  // Update the state to include a copy confirmation
  const [isCopied, setIsCopied] = useState(false);

  const handleGenerateNewsletter = () => {
    if (!inputDate || !inputEndDate) {
      alert('Please select both start and end dates');
      return;
    }

    if (new Date(inputDate) > new Date(inputEndDate)) {
      alert('Start date cannot be after end date');
      return;
    }

    setDate(inputDate);

    axios
      .get("http://localhost:5001/api/ai-news", {
        params: {
          date_from: inputDate,
          date_to: inputEndDate,
          numHeadlines: 5,
        },
      })
      .then((response) => {
        const fetchedHeadlines: string[] = response.data.headlines;
        setHeadlines(fetchedHeadlines);
        
        const content = `
<div style="text-align: left;">
  <ul style="list-style-type: disc; padding-left: 20px;">
    ${fetchedHeadlines.map(headline => `
    <li style="margin-bottom: 10px; text-align: left;">
      <strong style="color: blue;">${headline}</strong>
    </li>`).join('')}
  </ul>
</div>
        `.trim();
        
        setHtmlContent(content);
        setEditableHtml(content);
      })
      .catch((error) => {
        console.error('Error fetching news:', error);
        alert('Failed to fetch news. Please try again.');
      });
  };

  // Update the handleCopyToClipboard function
  const handleCopyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(editableHtml);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000); // Hide message after 2 seconds
    } catch (err) {
      console.error('Failed to copy: ', err);
    }
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

        {/* Replace the toggle switch with a textarea and preview */}
        {htmlContent && (
          <div style={{ display: 'flex', gap: '20px', width: '100%', marginTop: '20px' }}>
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ color: 'black', margin: 0 }}>Edit HTML</h3>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  {isCopied && <span style={{ color: 'green', fontSize: '0.9em' }}>Copied to Clipboard!</span>}
                  <button 
                    onClick={handleCopyToClipboard}
                    style={{
                      padding: '5px 12px',
                      backgroundColor: '#646cff',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '0.8em',
                      transition: 'background-color 0.2s'
                    }}
                  >
                    Copy
                  </button>
                </div>
              </div>
              <textarea
                value={editableHtml}
                onChange={(e) => setEditableHtml(e.target.value)}
                style={{
                  width: '100%',
                  height: '300px',
                  padding: '10px',
                  fontFamily: 'monospace',
                  backgroundColor: 'black',
                  color: 'white',
                  border: '1px solid #ccc',
                  borderRadius: '4px'
                }}
              />
            </div>
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <h3 style={{ color: 'black', margin: 0 }}>Live Preview</h3>
              <div
                style={{
                  padding: '10px',
                  border: '1px solid #ccc',
                  backgroundColor: 'white',
                  height: '300px',
                  overflowY: 'auto'
                }}
                dangerouslySetInnerHTML={{ __html: editableHtml }}
              />
            </div>
          </div>
        )}

        <button style={{ marginTop: '20px', marginBottom: '10px' }} onClick={() => console.log('Regenerate button clicked')}>
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