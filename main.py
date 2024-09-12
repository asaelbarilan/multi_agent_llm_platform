from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from agents import initialize_agents, orchestrate_problem_solving
import asyncio

app = FastAPI()

# CORS middleware for allowing requests from all origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to allow specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Prompt(BaseModel):
    prompt: str

# Generator for streaming messages to frontend
async def message_stream(agents, prompt):
    async for message in orchestrate_problem_solving(agents, prompt):
        # Log the message being sent to the frontend
        print(f"Sending message: {message}")

        # Split message into lines and prefix each with 'data:'
        message_lines = message.strip().splitlines()
        sse_message = '\n'.join(f"data: {line}" for line in message_lines) + '\n\n'
        yield sse_message

@app.get("/solve")
async def solve_problem(prompt: str):
    agents = initialize_agents()  # Initialize agents
    # Return a streaming response for real-time updates
    return StreamingResponse(message_stream(agents, prompt), media_type="text/event-stream")
