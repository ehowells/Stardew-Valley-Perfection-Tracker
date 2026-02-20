import React, { useState } from 'react';
import './App.css';
import FileUpload from './components/FileUpload';
import Results from './components/Results';

function App() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileUpload = async (file) => {
    setLoading(true);
    setError(null);
    setResults(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('https://stardew-valley-perfection-tracker.onrender.com/api/analyze', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to analyze file');
      }

      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Stardew Valley Perfection Tracker</h1>
        <p>Upload your save file to track your progress toward perfection!</p>
      </header>

      <main className="App-main">
        <FileUpload onFileUpload={handleFileUpload} loading={loading} />

        {error && (
          <div className="error-message">
            <h3>Error</h3>
            <p>{error}</p>
          </div>
        )}

        {loading && (
          <div className="loading">
            <p>Analyzing your save file...</p>
          </div>
        )}

        {results && <Results results={results} />}
      </main>

      <footer className="App-footer">
        <p>Save file location: Your Stardew Valley saves are typically in:</p>
        <ul>
          <li>Windows: %APPDATA%\StardewValley\Saves\[YourFarmName]_[ID]\[YourFarmName]_[ID]</li>
          <li>Mac: ~/.config/StardewValley/Saves/[YourFarmName]_[ID]/[YourFarmName]_[ID]</li>
          <li>Linux: ~/.config/StardewValley/Saves/[YourFarmName]_[ID]/[YourFarmName]_[ID]</li>
        </ul>
      </footer>
    </div>
  );
}

export default App;
