import React, { useState } from 'react';

function PromptInput({ onNewMessage }) {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (prompt.trim() === '') return;

    setLoading(true);

    // Use encodeURIComponent to safely include the prompt in the URL
    const eventSource = new EventSource(`http://localhost:8000/solve?prompt=${encodeURIComponent(prompt)}`);

    // Event handler for when the connection is opened
    eventSource.onopen = function () {
      console.log('Connection to server opened.');
    };

    // Capture messages as they stream in
    eventSource.onmessage = function (event) {
      console.log('Message received from backend:', event.data);
      onNewMessage(event.data);

      // Check for completion messages to close the EventSource
      if (
        event.data.includes('Solution verified, stopping conversation.') ||
        event.data.includes('Conversation ended without a verified solution.') ||
        event.data.includes('Max iterations reached, stopping conversation.')
      ) {
        eventSource.close();
        setLoading(false);
      }
    };

    // Handle errors
    eventSource.onerror = function (err) {
      console.error('EventSource failed:', err);
      eventSource.close();
      setLoading(false);
    };

    setPrompt(''); // Clear input field after submission
  };

  return (
    <form onSubmit={handleSubmit} className="prompt-input-container">
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
    </form>
  );
}

export default PromptInput;
