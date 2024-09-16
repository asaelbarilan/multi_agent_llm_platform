# test_main.py

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_solve_endpoint():
    # Simulate a prompt
    prompt = "Test prompt for unit testing."

    # Send a GET request to the /solve endpoint
    with client.stream("GET", f"/solve?prompt={prompt}") as response:
        assert response.status_code == 200
        # Check that the response headers indicate streaming content
        assert response.headers.get("content-type") == "text/event-stream"

        # Collect the streamed messages
        messages = []
        for line in response.iter_lines():
            decoded_line = line.decode('utf-8')
            print(f"Received line: {decoded_line}")
            if decoded_line.startswith("data:"):
                # Extract the message content
                message_content = decoded_line[5:].strip()
                messages.append(message_content)

        # Check that we received some messages
        assert len(messages) > 0
        print(f"Collected messages: {messages}")
