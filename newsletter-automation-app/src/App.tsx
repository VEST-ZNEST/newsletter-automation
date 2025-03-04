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
              numHeadlines: inputNumHeadlines, // number of headlines requested
          },
         })
        .then((response) => {
          const fetchedHeadlines: string[] = response.data.headlines;
          console.log("fetchedHeadlines: ", fetchedHeadlines);
          // Update state with the fetched headlines array
          setHeadlines(fetchedHeadlines)
          // Update HTML content without delete buttons
          updateHtmlContent(fetchedHeadlines);
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
    
    // Update HTML content without delete buttons
    updateHtmlContent(updatedHeadlines);
  };

  // Update HTML content without delete buttons
  const updateHtmlContent = (headlinesList: string[]) => {
    const content = `<div>\n<ul>\n    ${headlinesList.map(h => 
      `<li style="text-align: left;">${h}</li>`
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

  const handleCopyToClipboard = () => {
    if (htmlContent) {
      navigator.clipboard.writeText(htmlContent).then(() => {
        alert('HTML content copied to clipboard!');
      }).catch(err => {
        console.error('Failed to copy: ', err);
      });
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', height: '100vh', width: '100%' }}>
      <img src={zNestLogo} alt="Znest Logo" style={{ marginBottom: '20px', width: '150px' }} />
      <div className="centered-content" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', backgroundColor: '#f0f0f0', padding: '20px', borderRadius: '8px' }}>
        
        {/* Inputs, Topic Dropdown, and Get Headlines Button in one line */}
        <div style={{ 
          display: 'flex', 
          flexDirection: 'row', 
          alignItems: 'center', 
          justifyContent: 'center', 
          gap: '10px', 
          marginBottom: '20px' 
        }}>
          {/* Start Date Input */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <label style={{ marginBottom: '5px', color: 'black' }}>Start Date:</label>
            <input
              type="date"
              value={inputDate}
              onChange={(e) => setInputDate(e.target.value)}
              max={today}
            />
          </div>

          {/* End Date Input */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <label style={{ marginBottom: '5px', color: 'black' }}>End Date:</label>
            <input
              type="date"
              value={inputEndDate}
              onChange={(e) => setInputEndDate(e.target.value)}
              max={today}
            />
          </div>

          {/* Number of Headlines Input */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <label style={{ marginBottom: '5px', color: 'black' }}>Num of headlines:</label>
            <input
              type="number"
              value={inputNumHeadlines}
              onChange={(e) => setInputNumHeadlines(Number(e.target.value))}
              min={1}
              style={{ width: '100px' }}
              placeholder="Headlines"
            />
          </div>

          {/* Topic Dropdown */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <label style={{ marginBottom: '5px', color: 'black' }}>Select Topic:</label>
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

          {/* Get Headlines Button */}
          <button 
            style={{ 
              marginTop: '20px',
              padding: '5px 10px'
            }} 
            onClick={handleGetHeadlines}
          >
            Get Headlines
          </button>
        </div>

        {/* Layout for headlines and editor */}
        {htmlContent && (
          <div style={{ 
            display: 'flex', 
            flexDirection: 'row', 
            gap: '20px', 
            width: '100%', 
            marginTop: '10px'
          }}>
            {/* Headlines with delete buttons */}
            <div style={{ 
              flex: 1, 
              padding: '10px', 
              backgroundColor: 'white', 
              border: '1px solid #ccc',
              overflowY: 'auto',
              maxHeight: '400px'
            }}>
              <h3 style={{ color: 'black' }}>{date} - {topic}</h3>
              
              <div>
                <ul style={{ paddingLeft: '20px', listStyleType: 'disc' }}>
                  {headlines.map((headline, index) => (
                    <li key={index} style={{ marginBottom: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ flex: 1, textAlign: 'left' }} dangerouslySetInnerHTML={{ __html: headline }}></span>
                      <button 
                        onClick={() => handleDeleteHeadline(index)}
                        style={{
                          padding: '5px 10px',
                          backgroundColor: '#ff4444',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          transition: 'background-color 0.3s ease',
                          fontSize: '14px'
                        }}
                        onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#cc0000'}
                        onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#ff4444'}
                      >
                        Delete
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Right side with HTML Preview and Editor */}
            <div style={{ 
              flex: 1, 
              display: 'flex', 
              flexDirection: 'column', 
              gap: '10px',
              position: 'relative'
            }}>
              {/* HTML Preview */}
              <div style={{ 
                flex: 1, 
                backgroundColor: 'white', 
                border: '1px solid #ccc',
                overflowY: 'auto',
                width: '100%',
                minHeight: '60%'
              }}>
                <div dangerouslySetInnerHTML={{ __html: htmlContent }} />
              </div>

              {/* Editor */}
              <div style={{ position: 'relative', flex: 1 }}>
                <textarea
                  value={htmlContent}
                  onChange={(e) => setHtmlContent(e.target.value)}
                  style={{ 
                    width: '100%', 
                    height: '100%', 
                    padding: '10px',
                    fontFamily: 'monospace'
                  }}
                />

                {/* Copy to Clipboard Button */}
                <button 
                  style={{ 
                    position: 'absolute',
                    top: '10px',
                    right: '10px',
                    padding: '3px 6px',
                    fontSize: '12px',
                    backgroundColor: '#007bff',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    transition: 'background-color 0.3s ease'
                  }}
                  onClick={handleCopyToClipboard}
                >
                  Copy to Clipboard
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;