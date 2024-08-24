import React, { useState } from 'react';

function PromptInput() {
    const [prompt, setPrompt] = useState('');
    const [conversation, setConversation] = useState([]);
    const [error, setError] = useState(null);

    const handleSubmit = async () => {
        try {
            const response = await fetch('http://localhost:8000/solve', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt }),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            setConversation(data.conversation);  // Update this line
            setError(null);
        } catch (error) {
            setError('Failed to fetch data from the server');
            console.error('There was an error!', error);
        }
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
            {error && <p style={{ color: 'red' }}>{error}</p>}
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
