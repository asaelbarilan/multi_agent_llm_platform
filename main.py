from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from agents import initialize_agents, orchestrate_problem_solving
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to allow specific origins if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Prompt(BaseModel):
    prompt: str


@app.post("/solve")
async def solve_problem(prompt: Prompt):
    agents = initialize_agents()  # Initialize the agents based on your setup
    conversation = []

    async def message_stream():
        async for message in orchestrate_problem_solving(agents, prompt.prompt):
            conversation.append(message.strip())

    await message_stream()

    return JSONResponse(content={"conversation": conversation})
