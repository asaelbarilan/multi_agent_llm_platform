# from fastapi import FastAPI, Request
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from fastapi.responses import StreamingResponse
# from agents import initialize_agents, orchestrate_problem_solving
# import asyncio
#
# app = FastAPI()
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Adjust this to allow specific origins if needed
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# class Prompt(BaseModel):
#     prompt: str
#
# @app.post("/solve")
# async def solve_problem(prompt: Prompt):
#     agents = initialize_agents()  # Initialize the agents based on your setup
#
#     async def message_stream():
#         async for message in orchestrate_problem_solving(agents, prompt.prompt):
#             yield message + "\n"
#             await asyncio.sleep(0.1)  # Small delay to simulate real-time response
#
#     return StreamingResponse(message_stream(), media_type="text/plain")
#
#
#
# # to activate:
# # backend: PS C:\Users\Asael\PycharmProjects\multi_agent_llm_platform> uvicorn main:app --reload
# # UI: PS C:\Users\Asael\PycharmProjects\multi_agent_llm_platform\multiagentapp> npm start
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
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

    async def message_stream():
        async for message in orchestrate_problem_solving(agents, prompt.prompt):
            yield message + "\n"
            await asyncio.sleep(0.1)  # Small delay to simulate real-time response

    return StreamingResponse(message_stream(), media_type="text/plain")

# to activate:
# backend: PS C:\Users\Asael\PycharmProjects\multi_agent_llm_platform> uvicorn main:app --reload
# UI: PS C:\Users\Asael\PycharmProjects\multi_agent_llm_platform\multiagentapp> npm start
