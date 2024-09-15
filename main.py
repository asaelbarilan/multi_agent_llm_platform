# File: main.py
# Path: C:/Users/Asael/PycharmProjects/multi_agent_llm_platform/main.py

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from agents import initialize_agents, orchestrate_problem_solving

app = FastAPI()

# CORS middleware for allowing requests from all origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to allow specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Generator for streaming messages to frontend
async def message_stream(agents, prompt):
    try:
        async for message in orchestrate_problem_solving(agents, prompt):
            # Log the message being sent to the frontend
            print(f"Sending message: {message}")

            # Split message into lines and prefix each with 'data:'
            message_lines = message.strip().splitlines()
            sse_message = '\n'.join(f"data: {line}" for line in message_lines) + '\n\n'
            yield sse_message
    except Exception as e:
        error_message = f"Error during problem solving: {str(e)}"
        print(error_message)
        yield f"data: {error_message}\n\n"

@app.get("/solve")
async def solve_problem(prompt: str, model: str = Query(default="gpt2")):
    try:
        agents = initialize_agents(model_name=model)  # Initialize agents with the selected model
        # Return a streaming response for real-time updates
        return StreamingResponse(message_stream(agents, prompt), media_type="text/event-stream")
    except Exception as e:
        error_response = {"error": f"Failed to load model '{model}': {e}"}
        print(f"Error in /solve endpoint: {e}")
        return JSONResponse(status_code=400, content=error_response)

# Endpoint to fetch available models
@app.get("/models")
async def get_models():
    available_models = [
        {"value": "distilgpt2", "label": "DistilGPT-2"},
        {"value": "gpt2", "label": "GPT-2"},
        {"value": "gpt2-medium", "label": "GPT-2 Medium"},
        {"value": "EleutherAI/gpt-neo-125M", "label": "GPT-Neo 125M"},
        {"value": "EleutherAI/gpt-neo-1.3B", "label": "GPT-Neo 1.3B"},
        {"value": "facebook/opt-125m", "label": "OPT-125M"},
        {"value": "facebook/opt-350m", "label": "OPT-350M"},
        {"value": "bigscience/bloom-560m", "label": "BLOOM 560M"},
        {"value": "bigscience/bloom-1b1", "label": "BLOOM 1.1B"},
        {"value": "microsoft/Phi-3.5-MoE-instruct", "label": "Phi 3.5 MoE-Instruct"},  # Added Phi 3.5
        # Add more models as needed
    ]
    return {"models": available_models}
