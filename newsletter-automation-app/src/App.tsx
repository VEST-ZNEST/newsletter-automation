import React, { useState } from 'react';
import './App.css';
import zNestLogo from './assets/znest-logo.png'; // Adjust the path as necessary
import axios from 'axios';

const App: React.FC = () => {
  // Get today's date in the format YYYY-MM-DD
  const today = new Date().toISOString().split('T')[0];

  // State variables
  const [data, setData] = useState<any>(null);
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

  const handleGetHeadlines = async (regenerate: boolean = false) => {
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

    try {
      switch (inputTopic) {
        case "AI Headlines": {
          const response = await axios.get("http://localhost:5001/api/ai-news", {
            params: {
              date_from: inputDate,
              date_to: inputEndDate,
              numHeadlines: inputNumHeadlines,
            },
          });

          const fetchedHeadlines: string[] = response.data.headlines;
          console.log("fetchedHeadlines: ", fetchedHeadlines);
          setHeadlines(fetchedHeadlines);

          // Generate HTML block after fetching headlines
          const content = `<div>\n  <p>Date: ${inputDate}</p>\n  <p>Topic: ${inputTopic}</p>\n  <p>Number of Headlines: ${inputNumHeadlines}</p>\n  <ul>\n    ${fetchedHeadlines.map(h => `<li>${h}</li>`).join('\n    ')}\n  </ul>\n</div>`;
          setHtmlContent(content);
          break;
        }

        case "Senior Housing News": {
          console.log('Fetching from backend...');
          console.log(`Using parameters - start_date: ${inputDate}, end_date: ${inputEndDate}, num_headlines: ${inputNumHeadlines}`);
          
          // Send parameters in the request body as JSON
          const response = await fetch('http://localhost:5000/api/senior-housing/headlines', {
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
            throw new Error(`Failed to fetch headlines: ${response.statusText}`);
          }

          const result = await response.json();
          if (result.error) {
            throw new Error(result.error);
          }

          setData({
            articles: result.articles.map((article: any) => ({
              title: article.title,
              url: article.url,
              author: article.author,
              publicationDate: new Date(article.publication_date).toLocaleDateString(),
            })),
            htmlContent: result.html_content
          });

          setHeadlines(result.articles.map((article: any) => article.title));
          setHtmlContent(result.html_content);
          break;
        }

        case "For-Sale Listings":
          // TODO(harris): get top {numHeadlines} headlines on day {date}
          break;

        default:
          throw new Error(`Unsupported topic: ${inputTopic}`);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An error occurred';
      console.error('Error fetching headlines:', error);
      setError(errorMessage);
      setData(null);
      setHeadlines([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', height: '100vh', width: '100%' }}>
      <img src={zNestLogo} alt="Znest Logo" style={{ marginBottom: '20px', width: '150px' }} />
      <div className="centered-content" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', backgroundColor: '#f0f0f0', padding: '20px', borderRadius: '8px', maxWidth: '800px', width: '90%' }}>
        
        {/* Date Range Input */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '20px', width: '100%' }}>
          <label style={{ marginBottom: '5px', color: 'black' }}>Start Date:</label>
          <input
            type="date"
            value={inputDate}
            onChange={(e) => setInputDate(e.target.value)}
            max={today}
            style={{ marginBottom: '10px', padding: '5px', width: '200px' }}
          />
          <label style={{ marginBottom: '5px', color: 'black' }}>End Date:</label>
          <input
            type="date"
            value={inputEndDate}
            onChange={(e) => setInputEndDate(e.target.value)}
            max={today}
            style={{ marginBottom: '10px', padding: '5px', width: '200px' }}
          />
        </div>

        {/* Number of Headlines Input */}
        <div style={{ marginBottom: '20px', width: '100%', textAlign: 'center' }}>
          <label style={{ marginBottom: '5px', display: 'block', color: 'black' }}>Number of Headlines:</label>
          <input
            type="number"
            value={inputNumHeadlines}
            onChange={(e) => setInputNumHeadlines(Number(e.target.value))}
            min={1}
            style={{ width: '200px', padding: '5px' }}
            placeholder="Enter number"
          />
        </div>
        
        {/* Topic Dropdown */}
        <div style={{ marginBottom: '20px', width: '100%', textAlign: 'center' }}>
          <label style={{ marginBottom: '5px', display: 'block', color: 'black' }}>Select Topic:</label>
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

        {/* Action Buttons */}
        <div style={{ marginBottom: '20px', display: 'flex', gap: '10px' }}>
          <button 
            style={{ 
              padding: '8px 16px',
              backgroundColor: isLoading ? '#ccc' : '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: isLoading ? 'not-allowed' : 'pointer'
            }} 
            onClick={() => handleGetHeadlines(false)}
            disabled={isLoading}
          >
            {isLoading ? 'Loading...' : 'Get Headlines'}
          </button>
          
          {inputTopic === 'Senior Housing News' && (
            <button 
              style={{ 
                padding: '8px 16px',
                backgroundColor: isLoading ? '#ccc' : '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: isLoading ? 'not-allowed' : 'pointer'
              }} 
              onClick={() => handleGetHeadlines(true)}
              disabled={isLoading}
            >
              Regenerate
            </button>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div style={{ color: '#dc3545', marginBottom: '20px', padding: '10px', backgroundColor: '#f8d7da', borderRadius: '4px', width: '100%', textAlign: 'center' }}>
            {error}
          </div>
        )}

        
        {/* Headlines Display */}
        {(headlines.length > 0 || data?.articles) && (
          <div style={{ 
            marginTop: '20px',
            padding: '20px',
            backgroundColor: 'white',
            border: '1px solid #dee2e6',
            borderRadius: '8px',
            width: '100%',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}>
            <h3 style={{ color: '#343a40', marginBottom: '15px', textAlign: 'center' }}>{date} - {topic}</h3>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {data?.articles ? (
                // Display Senior Housing News articles with links
                data.articles.map((article: any, index: number) => (
                  <li 
                    key={index}
                    style={{ 
                      marginBottom: '10px',
                      padding: '10px',
                      borderBottom: '1px solid #dee2e6',
                      fontSize: '16px'
                    }}
                  >
                    <a 
                      href={article.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ 
                        color: '#2c5282',
                        textDecoration: 'none',
                        fontWeight: 500
                      }}
                    >
                      {article.title}
                    </a>
                  </li>
                ))
              ) : (
                // Display AI Headlines
                headlines.map((headline, index) => (
                  <li 
                    key={index} 
                    dangerouslySetInnerHTML={{ __html: headline }}
                    style={{ 
                      marginBottom: '10px',
                      padding: '10px',
                      borderBottom: '1px solid #dee2e6',
                      fontSize: '16px'
                    }}
                  />
                ))
              )}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;