import React, { useState } from 'react';
import './App.css';
import zNestLogo from './assets/znest-logo.png'; // Adjust the path as necessary

const App: React.FC = () => {
  // Get today's date in the format YYYY-MM-DD
  const today = new Date().toISOString().split('T')[0];

  const [data, setData] = useState<any>(null);

  // Store input values separately until "Get Headlines" is clicked
  const [inputDate, setInputDate] = useState(today);
  const [inputNumHeadlines, setInputNumHeadlines] = useState<number>(5);
  const [inputTopic, setInputTopic] = useState("AI Headlines");

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGetHeadlines = async (regenerate: boolean = false) => {
    if (!inputDate || inputNumHeadlines <= 0) {
      return; // Do nothing if no date is selected or numHeadlines is 0
    }


    setIsLoading(true);
    setError(null);



    try {
      if (inputTopic === "Senior Housing News") {
        console.log('Fetching from backend...');
        const url = `http://localhost:5000/api/senior-housing/headlines?num_headlines=${inputNumHeadlines}`;
        const response = await fetch(url, {
          method: regenerate ? 'POST' : 'GET'
        });
        console.log('Response status:', response.status);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch headlines: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('Response data:', data);
        
        if (data.error) {
          throw new Error(data.error);
        }
        
        if (!data.articles || !Array.isArray(data.articles)) {
          throw new Error('Invalid articles data received');
        }
        
        if (!data.html_content) {
          throw new Error('No HTML content received');
        }
        
        setData(data);
      } else {
        // Simulate loading for other topics
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Temporary handling for other topics
        const generatedHeadlines = Array.from({ length: inputNumHeadlines }, (_, i) => `${inputTopic} Headline ${i + 1}`);
        setData({
          articles: generatedHeadlines.map(title => ({
            title,
            url: '#',
            publication_date: new Date().toISOString()
          }))
        });

      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An error occurred';
      console.error('Error fetching headlines:', error);
      setError(`Failed to fetch headlines: ${errorMessage}`);
      setData(null);
    } finally {
      setIsLoading(false);
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

        <button 
          style={{ marginBottom: '10px', opacity: isLoading ? 0.7 : 1 }} 
          onClick={() => handleGetHeadlines(false)} 
          disabled={isLoading}
        >
          {isLoading ? 'Loading...' : 'Get Headlines'}
        </button>

        {error && (
          <div style={{ color: 'red', marginBottom: '10px' }}>
            {error}
          </div>
        )}

        {/* Display articles as a list */}
        {data && data.articles && (
          <div style={{ marginTop: '10px', marginBottom: '10px', padding: '20px', backgroundColor: 'white', border: '1px solid #ccc', width: '100%', maxWidth: '800px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
            <h3 style={{ color: '#333', marginBottom: '15px', borderBottom: '2px solid #eee', paddingBottom: '10px' }}>
              Senior Housing News - {new Date().toLocaleDateString()}
            </h3>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {data.articles.map((article: any, index: number) => (
                <li key={index} style={{ marginBottom: '15px', padding: '10px', borderBottom: '1px solid #eee' }}>
                  <a 
                    href={article.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    style={{ 
                      color: '#2c5282', 
                      textDecoration: 'none',
                      fontSize: '16px',
                      fontWeight: 500
                    }}
                  >
                    {article.title}
                  </a>

                </li>
              ))}
            </ul>
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