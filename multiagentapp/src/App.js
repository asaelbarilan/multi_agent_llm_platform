// File: App.js
// Path: C:/Users/Asael/PycharmProjects/multi_agent_llm_platform/multiagentapp/src/App.js

import React, { useState } from 'react';
import PromptInput from './PromptInput';
import Conversation from './Conversation';
import './App.css'; // Ensure App.css is imported

function App() {
  // Maintain a state to track the conversation messages
  const [messages, setMessages] = useState([]);

  // Function to handle new messages coming from the EventSource
  const handleNewMessage = (message) => {
    // Parse the message
    let parsedMessage = {};

    // Check if the message contains ":", indicating agent name and message
    const colonIndex = message.indexOf(':');
    if (colonIndex !== -1) {
      const agentName = message.substring(0, colonIndex).trim();
      const content = message.substring(colonIndex + 1).trim();
      parsedMessage = {
        type: 'agent',
        agent: agentName,
        content: content,
      };
    } else {
      // If no colon, treat it as a system message
      parsedMessage = {
        type: 'system',
        content: message,
      };
    }

    setMessages((prevMessages) => [...prevMessages, parsedMessage]); // Append new messages
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Multi-Agent LLM Platform</h1>
        <PromptInput onNewMessage={handleNewMessage} /> {/* Pass the function to capture new messages */}
      </header>
      <Conversation messages={messages} /> {/* Display the conversation outside the header */}
    </div>
  );
}

export default App;
