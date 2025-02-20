import React, { useState } from 'react';
import './App.css';


const App: React.FC = () => {
  const [date, setDate] = useState('');

  const handleGetHtmlBlock = async () => {
    try {
      const response = await fetch(`https://your-api-endpoint.com/get-html?date=${date}`);
      const data = await response.json();
      console.log('HTML Block:', data);
    } catch (error) {
      console.error('Error fetching HTML block:', error);
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', width: '100%' }}>
      <div className="centered-content" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', backgroundColor: '#f0f0f0', padding: '20px', borderRadius: '8px' }}>
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          style={{ marginBottom: '10px' }}
        />
        <button style={{ marginBottom: '10px' }} onClick={handleGetHtmlBlock}>
          Get HTML Block
        </button>
      </div>
    </div>
  );
};

export default App;
