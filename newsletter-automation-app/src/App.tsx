import React from 'react';
import './App.css';


const App: React.FC = () => {
  return (
    <div style={{ display: 'flex', width: '100%' }}>
      <div className="left-menu" style={{ position: 'fixed', top: 0, left: 0, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', width: '20%', height: '100vh', backgroundColor: '#f0f0f0', padding: '10px' }}>
        <button style={{ marginBottom: '10px' }} onClick={() => console.log('Regenerate Newsletter')}>
          Regenerate Newsletter
        </button>
        <button style={{ marginBottom: '10px' }} onClick={() => console.log('Fetch Newsletter Contents')}>
          Fetch Newsletter Contents
        </button>
        <button style={{ marginBottom: '10px' }} onClick={() => console.log('Schedule Newsletter')}>
          Schedule Newsletter
        </button>
      </div>
      <div style={{ marginLeft: '20%', width: '80%', padding: '10px' }}>
        {/* Empty section for future content */}
      </div>
    </div>
  );
};

export default App;
