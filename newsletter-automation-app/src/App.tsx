import React, { useState } from 'react';
import './App.css';
import zNestLogo from './assets/znest-logo.png'; // Adjust the path as necessary
import axios from 'axios';

const App: React.FC = () => {
  // Get today's date in the format YYYY-MM-DD
  const today = new Date().toISOString().split('T')[0];

  const [date, setDate] = useState(today);
  const [numHeadlines, setNumHeadlines] = useState<number>(5);
  const [headlines, setHeadlines] = useState<string[]>([]);
  const [htmlContent, setHtmlContent] = useState<string | null>(null);
  const [showHtml, setShowHtml] = useState(false);
  const [topic, setTopic] = useState("AI Headlines"); // Default topic

  // Store input values separately until "Get Headlines" is clicked
  const [inputDate, setInputDate] = useState(today);
  const [inputNumHeadlines, setInputNumHeadlines] = useState<number>(5);
  const [inputTopic, setInputTopic] = useState("AI Headlines");

  const handleGetHeadlines = () => {
    if (!inputDate || inputNumHeadlines <= 0) {
      return;
    }

    // Update states only when "Get Headlines" is pressed
    setDate(inputDate);
    setNumHeadlines(inputNumHeadlines);
    setTopic(inputTopic);

    switch (topic) {
      case "AI Headlines": {
        axios
          .get("http://localhost:5001/api/ai-news", {
            params: {
              date: inputDate,
              numHeadlines: inputNumHeadlines,
            },
          })
          .then((response) => {
            const fetchedHeadlines: string[] = response.data.headlines;
            console.log("fetchedHeadlines: ", fetchedHeadlines)
            setHeadlines(fetchedHeadlines);
            // Generate HTML block after fetching headlines
            const content = `<div>\n  <p>Date: ${inputDate}</p>\n  <p>Topic: ${inputTopic}</p>\n  <p>Number of Headlines: ${inputNumHeadlines}</p>\n  <ul>\n    ${fetchedHeadlines.map(h => `<li>${h}</li>`).join('\n    ')}\n  </ul>\n</div>`;
            setHtmlContent(content);
          });
        break;
      }
      case "Senior Housing News":
        // TODO(tyler): get top {numHeadlines} headlines on day {date} as an array and setHeadlines(your array of headlines)
        break;
      case "For-Sale Listings":
        // TODO(harris): get top {numHeadlines} headlines on day {date} as an array and setHeadlines(your array of headlines)
        break;
      default:
        break;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', height: '100vh', width: '100%' }}>
      <img src={zNestLogo} alt="Znest Logo" style={{ marginBottom: '20px', width: '150px' }} />
      <div className="centered-content" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', backgroundColor: '#f0f0f0', padding: '20px', borderRadius: '8px' }}>
        
        {/* Date Input */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '10px' }}>
          <input
            type="date"
            value={inputDate}
            onChange={(e) => setInputDate(e.target.value)}
            max={today}
            style={{ marginBottom: '10px' }}
          />
          
          {/* Number of Headlines Input */}
          <label style={{ marginBottom: '5px', color: 'black' }}>Num of headlines:</label>
          <input
            type="number"
            value={inputNumHeadlines}
            onChange={(e) => setInputNumHeadlines(Number(e.target.value))}
            min={1}
            style={{ width: '100px' }}
            placeholder="Headlines"
          />
          
          {/* Topic Dropdown */}
          <label style={{ marginTop: '10px', marginBottom: '5px', color: 'black' }}>Select Topic:</label>
          <select
            value={inputTopic}
            onChange={(e) => setInputTopic(e.target.value)}
            style={{ width: '200px', padding: '5px' }}
          >
            <option value="AI Headlines">AI Headlines</option>
            <option value="Senior Housing News">Senior Housing News</option>
            <option value="For-Sale Listings">For-Sale Listings</option>
          </select>
        </div>

        <button style={{ marginBottom: '10px' }} onClick={handleGetHeadlines}>
          Get Headlines
        </button>

        {/* Conditionally render either headlines or HTML block */}
        {htmlContent && showHtml ? (
          <div style={{ marginTop: '10px', marginBottom: '10px', padding: '10px', border: '1px solid #ccc', backgroundColor: 'black', width: '100%', textAlign: 'left', color: 'white' }}>
            <pre style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>{htmlContent}</pre>
          </div>
        ) : (
          headlines.length > 0 && (
            <div style={{ marginTop: '10px', marginBottom: '10px', padding: '10px', backgroundColor: 'white', border: '1px solid #ccc', width: '100%', textAlign: 'center' }}>
              <h3 style={{ color: 'black' }}>{date} - {topic}</h3>
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