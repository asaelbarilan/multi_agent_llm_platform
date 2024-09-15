// File: Conversation.js
// Path: C:/Users/Asael/PycharmProjects/multi_agent_llm_platform/multiagentapp/src/Conversation.js

import React, { useEffect, useRef } from 'react';
import './Conversation.css';

function Conversation({ messages }) {
  const containerRef = useRef(null);

  useEffect(() => {
    // Scroll to the bottom when messages change
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [messages]);

  // Helper function to render content with code blocks
  const renderContentWithCodeBlocks = (content) => {
    const parts = content.split(/(```[\s\S]*?```)/g); // Split content by code blocks
    return parts.map((part, index) => {
      if (part.startsWith('```') && part.endsWith('```')) {
        // It's a code block
        const codeContent = part.slice(3, -3); // Remove the triple backticks
        return (
          <pre key={index} className="code-block">
            <code>{codeContent}</code>
          </pre>
        );
      } else {
        // Regular text
        return (
          <span key={index} style={{ whiteSpace: 'pre-wrap' }}>
            {part}
          </span>
        );
      }
    });
  };

  return (
    <div className="conversation-container" ref={containerRef}>
      {messages.map((message, index) => {
        const isAgent = message.type === 'agent';
        const isSystem = message.type === 'system';
        const isError = message.type === 'error';

        // Check for code blocks
        const codeBlockPattern = /```[\s\S]*?```/g;
        const hasCodeBlock = codeBlockPattern.test(message.content);

        return (
          <div
            key={index}
            className={`message ${isAgent ? 'agent' : isSystem ? 'system' : isError ? 'error' : 'user'}`}
          >
            {isAgent && <div className="agent-name">{message.agent}</div>}
            {isError && <div className="error-message">Error: {message.content}</div>}
            {!(isAgent || isError) && (
              <div className="message-content">
                {hasCodeBlock ? (
                  renderContentWithCodeBlocks(message.content)
                ) : (
                  <span style={{ whiteSpace: 'pre-wrap' }}>{message.content}</span>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

export default Conversation;
