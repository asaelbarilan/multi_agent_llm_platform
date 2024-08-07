
from fastapi import FastAPI
from pydantic import BaseModel
from agents import initialize_agents, orchestrate_problem_solving

app = FastAPI()

class Prompt(BaseModel):
    prompt: str

@app.post("/solve")
async def solve_problem(prompt: Prompt):
    agents = initialize_agents()  # Initialize the agents based on your setup
    conversation, solution = orchestrate_problem_solving(agents, prompt.prompt)
    return {"conversation": conversation, "solution": solution}

# Run the FastAPI server using: uvicorn main:app --reload
print('')