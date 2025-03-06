import React, { useState, useEffect } from 'react';
import './App.css';
import zNestLogo from './assets/znest-logo.png'; // Adjust the path as necessary
import axios from 'axios';

// Define interfaces for type safety
interface Article {
  title: string;
  url: string;
  author?: string;
  publicationDate?: string;
}

interface NewsData {
  articles: Article[];
  htmlContent: string;
}

const App: React.FC = () => {
  // Get today's date in the format YYYY-MM-DD
  const today = new Date().toISOString().split('T')[0];

  // State variables
  const [data, setData] = useState<NewsData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [headlines, setHeadlines] = useState<string[]>([]);
  const [htmlContent, setHtmlContent] = useState('');

  // Input state
  const [inputDate, setInputDate] = useState(today);
  const [inputEndDate, setInputEndDate] = useState(today);
  const [inputNumHeadlines, setInputNumHeadlines] = useState<number>(5);
  const [inputTopic, setInputTopic] = useState("AI Headlines");

  // Display state
  const [date, setDate] = useState(today);
  const [topic, setTopic] = useState("AI Headlines");
  const [numHeadlines, setNumHeadlines] = useState(5);

  // Function to handle regenerating articles using the select-articles endpoint
  const handleRegenerateArticles = async () => {
    if (!inputDate || inputNumHeadlines <= 0) {
      return;
    }

    setIsLoading(true);
    setError(null);

    // Update states when regenerate is pressed
    setDate(inputDate);
    setNumHeadlines(inputNumHeadlines);
    setTopic(inputTopic);

    try {
      console.log('Regenerating articles with date restrictions...');
      console.log(`Using parameters - start_date: ${inputDate}, end_date: ${inputEndDate}, num_headlines: ${inputNumHeadlines}`);
      
      // Send parameters in the request body as JSON instead of in the URL
      const response = await fetch('http://localhost:5000/api/select-articles', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          start_date: inputDate,
          end_date: inputEndDate,
          num_headlines: inputNumHeadlines
        }),
        credentials: 'include',
        mode: 'cors'
      });

      if (!response.ok) {
        throw new Error(`Failed to regenerate articles: ${response.statusText}`);
      }

      const result = await response.json();
      if (result.error) {
        throw new Error(result.error);
      }

      // Now get the updated articles with HTML content
      console.log('Getting headlines with same date parameters...');
      const headlinesResponse = await fetch('http://localhost:5000/api/senior-housing/headlines', {
        method: 'POST', // Changed to POST to send data in body
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          start_date: inputDate,
          end_date: inputEndDate,
          num_headlines: inputNumHeadlines
        }),
        credentials: 'include',
        mode: 'cors'
      });

      if (!headlinesResponse.ok) {
        throw new Error(`Failed to fetch headlines: ${headlinesResponse.statusText}`);
      }

      const headlinesResult = await headlinesResponse.json();
      if (headlinesResult.error) {
        throw new Error(headlinesResult.error);
      }

      setData({
        articles: headlinesResult.articles.map((article: any) => ({
          title: article.title,
          url: article.url,
          author: article.author,
          publicationDate: new Date(article.publication_date).toLocaleDateString(),
        })),
        htmlContent: headlinesResult.html_content
      });

      setHeadlines(headlinesResult.articles.map((article: any) => article.title));
      setHtmlContent(headlinesResult.html_content);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An error occurred';
      console.error('Error regenerating articles:', error);
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGetHeadlines = (regenerate: boolean = false) => {
    if (!inputDate || inputNumHeadlines <= 0) {
      return;
    }

    // If regenerate is true, use the dedicated regenerate function
    if (regenerate && inputTopic === "Senior Housing News") {
      return handleRegenerateArticles();
    }

    setIsLoading(true);
    setError(null);

    // Update states when "Get Headlines" is pressed
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
            setHeadlines(fetchedHeadlines);
            // Update HTML content without delete buttons
            updateHtmlContent(fetchedHeadlines);
          })
          .catch((error) => {
            const errorMessage = error instanceof Error ? error.message : 'An error occurred';
            console.error('Error fetching AI headlines:', error);
            setError(errorMessage);
            setData(null);
            setHeadlines([]);
          })
          .finally(() => {
            setIsLoading(false);
          });
        break;
      }

      case "Senior Housing News": {
        console.log('Fetching from backend...');
        console.log(`Using parameters - start_date: ${inputDate}, end_date: ${inputEndDate}, num_headlines: ${inputNumHeadlines}`);
        
        // Send parameters in the request body as JSON
        fetch('http://localhost:5000/api/senior-housing/headlines', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          body: JSON.stringify({
            start_date: inputDate,
            end_date: inputEndDate,
            num_headlines: inputNumHeadlines
          }),
          credentials: 'include',
          mode: 'cors'
        })
        .then(response => {
          if (!response.ok) {
            throw new Error(`Failed to fetch headlines: ${response.statusText}`);
          }
          return response.json();
        })
        .then(result => {
          if (result.error) {
            throw new Error(result.error);
          }

          // Create articles with title and url only
          setData({
            articles: result.articles.map((article: any) => ({
              title: article.title,
              url: article.url
            })),
            htmlContent: result.html_content
          });

          setHeadlines(result.articles.map((article: any) => article.title));
          setHtmlContent(result.html_content);
        })
        .catch(error => {
          const errorMessage = error instanceof Error ? error.message : 'An error occurred';
          console.error('Error fetching Senior Housing headlines:', error);
          setError(errorMessage);
          setData(null);
          setHeadlines([]);
        })
        .finally(() => {
          setIsLoading(false);
        });
        break;
      }

      case "For-Sale Listings":
        // TODO(harris): get top {numHeadlines} headlines on day {date}
        setIsLoading(false);
        break;

      default:
        console.error(`Unsupported topic: ${inputTopic}`);
        setError(`Unsupported topic: ${inputTopic}`);
        setIsLoading(false);
    }
  };

  const handleDeleteHeadline = (indexToDelete: number) => {
    // Get the headline being deleted
    const headlineToDelete = headlines[indexToDelete];
    
    // Update the headlines list
    const updatedHeadlines = headlines.filter((_, index) => index !== indexToDelete);
    setHeadlines(updatedHeadlines);
    
    // If we have data with articles (Senior Housing News case)
    if (data && data.articles) {
      // Filter out the deleted article from the data
      const updatedArticles = data.articles.filter((article: Article) => article.title !== headlineToDelete);
      
      // Update the data state with filtered articles
      setData({
        ...data,
        articles: updatedArticles
      });
    }
    
    // Update HTML content without delete buttons
    updateHtmlContent(updatedHeadlines);
  };

  // Update HTML content without delete buttons
  const updateHtmlContent = (headlinesList: string[]) => {
    // For Senior Housing News, we expect data to have articles with urls
    if (topic === "Senior Housing News" && data && data.articles) {
      // Create HTML with hyperlinks - only include articles whose titles are in the headlinesList
      const content = `<div>\n<ul>\n    ${data.articles
        .filter((article: Article) => headlinesList.includes(article.title)) // Only include non-deleted headlines
        .map((article: Article) => 
          `<li style="text-align: left;"><a href="${article.url}" target="_blank">${article.title}</a></li>`
        )
        .join('\n    ')}\n  </ul>\n</div>`;
      setHtmlContent(content);
    } else {
      // For other topics, just use the headlines as plain text
      const content = `<div>\n<ul>\n    ${headlinesList.map(h => 
        `<li style="text-align: left;">${h}</li>`
      ).join('\n    ')}\n  </ul>\n</div>`;
      setHtmlContent(content);
    }
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
      <div className="centered-content" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', backgroundColor: '#f0f0f0', padding: '20px', borderRadius: '8px', maxWidth: '800px', width: '90%' }}>
        
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
            onClick={(e) => handleGetHeadlines()}
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
                      <span style={{ flex: 1, textAlign: 'left' }}>
                        {topic === "Senior Housing News" && data && data.articles ? (
                          // Find the matching article to get the URL
                          data.articles.find((a: Article) => a.title === headline) ? (
                            <a href={data.articles.find((a: Article) => a.title === headline)?.url} target="_blank" rel="noopener noreferrer">
                              {headline}
                            </a>
                          ) : headline
                        ) : headline}
                      </span>
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