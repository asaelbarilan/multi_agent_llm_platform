// File: PromptInput.js
// Path: C:/Users/Asael/PycharmProjects/multi_agent_llm_platform/multiagentapp/src/PromptInput.js

import React, { useState } from 'react';

function PromptInput({ onNewMessage }) {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [eventSource, setEventSource] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (prompt.trim() === '') return;

    setLoading(true);

    // Close any existing EventSource to prevent multiple connections
    if (eventSource) {
      eventSource.close();
    }

    const newEventSource = new EventSource(
      `http://localhost:8000/solve?prompt=${encodeURIComponent(prompt)}`
    );

    setEventSource(newEventSource);

    newEventSource.onopen = function () {
      console.log('Connection to server opened.');
    };

    newEventSource.onmessage = function (event) {
      console.log('Message received from backend:', event.data);
      onNewMessage(event.data);

      // Check for completion messages to close the EventSource
      if (
        event.data.includes('All tasks completed successfully.') ||
        event.data.includes('Tasks could not be completed.') ||
        event.data.startsWith("Error:")
      ) {
        newEventSource.close();
        setLoading(false);
      }
    };

    newEventSource.onerror = function (err) {
      console.error('EventSource failed:', err);
      newEventSource.close();
      setLoading(false);
    };

    setPrompt(''); // Clear input field after submission
  };

  return (
    <form onSubmit={handleSubmit} className="prompt-input-container">
      <div className="prompt-input-wrapper">
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          className="prompt-input"
          placeholder="Enter your prompt here"
          disabled={loading}
        />
        <button type="submit" className="submit-button" disabled={loading}>
          {loading ? 'Processing...' : 'Submit'}
        </button>
      </div>
    </form>
  );
}

export default PromptInput;
