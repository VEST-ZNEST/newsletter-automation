import React, { useState, useEffect } from 'react';
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
  const [inputEndDate, setInputEndDate] = useState(today);
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

    switch (inputTopic) {
      case "AI Headlines": {
        axios
          .get("http://localhost:5001/api/ai-news", {
            params: {
              date_from: inputDate,
              date_to: inputEndDate,
              numHeadlines: inputNumHeadlines,
            },
          })
          .then((response) => {
            const fetchedHeadlines: string[] = response.data.headlines;
            console.log("fetchedHeadlines: ", fetchedHeadlines);
            setHeadlines(fetchedHeadlines);
            // Use the new function to update HTML
            updateHtmlContent(fetchedHeadlines);
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

  const handleDeleteHeadline = (indexToDelete: number) => {
    const updatedHeadlines = headlines.filter((_, index) => index !== indexToDelete);
    setHeadlines(updatedHeadlines);
    
    // Update HTML content with delete buttons
    updateHtmlContent(updatedHeadlines);
  };

  // New function to update HTML content
  const updateHtmlContent = (headlinesList: string[]) => {
    const content = `<div>\n<ul>\n    ${headlinesList.map((h, i) => 
      `<li>${h}<button id="delete-btn-${i}" data-index="${i}" style="margin-left: 10px; padding: 2px 8px; background-color: #ff4444; color: white; border: none; border-radius: 4px; cursor: pointer;">Delete</button></li>`
    ).join('\n    ')}\n  </ul>\n</div>`;
    setHtmlContent(content);
  };

  // Add direct click handler using useRef and useEffect
  const previewRef = React.useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    // Function to handle clicks on the preview pane
    const handlePreviewClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      
      // Check if a delete button was clicked
      if (target.tagName === 'BUTTON' && target.id.startsWith('delete-btn-')) {
        const index = parseInt(target.getAttribute('data-index') || '0', 10);
        handleDeleteHeadline(index);
        e.preventDefault();
      }
    };
    
    // Add click event to the preview div
    const previewDiv = previewRef.current;
    if (previewDiv) {
      previewDiv.addEventListener('click', handlePreviewClick);
    }
    
    return () => {
      if (previewDiv) {
        previewDiv.removeEventListener('click', handlePreviewClick);
      }
    };
  }, [headlines]);

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

        <button style={{ marginBottom: '10px' }} onClick={handleGetHeadlines}>
          Get Headlines
        </button>

        {/* Preview with delete functionality */}
        {htmlContent && (
          <div style={{ 
            display: 'flex', 
            gap: '20px', 
            width: '100%', 
            marginTop: '10px'
          }}>
            {/* Preview */}
            <div 
              ref={previewRef}
              style={{ 
                flex: 1, 
                padding: '10px', 
                backgroundColor: 'white', 
                border: '1px solid #ccc'
              }}
            >
              <h3 style={{ color: 'black' }}>{date} - {topic}</h3>
              <div dangerouslySetInnerHTML={{ __html: htmlContent }} />
            </div>
            
            {/* Editor */}
            <div style={{ 
              flex: 1
            }}>
              <textarea
                value={htmlContent}
                onChange={(e) => setHtmlContent(e.target.value)}
                style={{ 
                  width: '100%', 
                  height: '300px', 
                  padding: '10px',
                  fontFamily: 'monospace'
                }}
              />
            </div>
          </div>
        )}

        <button style={{ marginBottom: '10px' }} onClick={() => console.log('Regenerate button clicked')}>
          Regenerate
        </button>
      </div>
    </div>
  );
};

export default App;