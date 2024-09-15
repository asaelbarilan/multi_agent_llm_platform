# File: main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from agents import initialize_agents, orchestrate_problem_solving, LocalModelLLM
import os

app = FastAPI()

# CORS middleware for allowing requests from all origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to allow specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Generator for streaming messages to frontend
def message_stream(orchestrator, prompt):
    try:
        conversation = orchestrate_problem_solving(orchestrator, prompt)
        for message in conversation:
            # Log the message being sent to the frontend
            print(f"Sending message: {message}")

            # Split message into lines and prefix each with 'data:'
            message_lines = message.strip().splitlines()
            sse_message = '\n'.join(f"data: {line}" for line in message_lines) + '\n\n'
            yield sse_message
    except Exception as e:
        # In case of error, send the error message to the frontend
        error_message = f"data: Error: {str(e)}\n\n"
        yield error_message


@app.get("/solve")
def solve_problem(prompt: str):
    # Choose your LLM
    # For local model:
    llm = LocalModelLLM(model_name="llama3")

    # If you want to use OpenAI's GPT-3.5, uncomment the following lines:
    # os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
    # from langchain.llms import OpenAI
    # llm = OpenAI(model_name="gpt-3.5-turbo", temperature=0)

    orchestrator = initialize_agents(llm=llm)  # Initialize orchestrator

    # Return a streaming response for real-time updates
    return StreamingResponse(message_stream(orchestrator, prompt), media_type="text/event-stream")
