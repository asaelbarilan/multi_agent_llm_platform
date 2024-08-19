import React from 'react';
import './App.css';
import PromptInput from './PromptInput';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Multi-Agent LLM Platform</h1>
        <PromptInput />
      </header>
    </div>
  );
}

export default App;
