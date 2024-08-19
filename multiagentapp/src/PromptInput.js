import React, { useState } from 'react';

function PromptInput() {
    const [prompt, setPrompt] = useState('');
    const [conversation, setConversation] = useState([]);

    const handleSubmit = async () => {
        const response = await fetch('http://localhost:8000/solve', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt }),
        });
        const data = await response.json();
        setConversation(data.conversation);
    };

    return (
        <div>
            <input
                type='text'
                value={prompt}
                onChange={e => setPrompt(e.target.value)}
                placeholder="Enter your prompt here"
            />
            <button onClick={handleSubmit}>Submit</button>
            <div>
                <h3>Conversation between Agents:</h3>
                <ul>
                    {conversation.map((msg, index) => (
                        <li key={index}>{msg}</li>
                    ))}
                </ul>
            </div>
        </div>
    );
}

export default PromptInput;
