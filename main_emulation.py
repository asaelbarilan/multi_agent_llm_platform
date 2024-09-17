# main_test.py

import asyncio
from agents.agents import ProblemSolvingAgent
from agents.orchestrator import orchestrate_problem_solving

def initialize_agents():
    # Initialize the agents
    solver = ProblemSolvingAgent("Solver")
    reviewer = ProblemSolvingAgent("Reviewer")  # You can create a separate ReviewerAgent class if needed
    return [solver, reviewer]

if __name__ == "__main__":
    agents = initialize_agents()
    prompt = "Create a simple calculator web app using Flask that adds two numbers provided by the user."

    async def main():
        async for message in orchestrate_problem_solving(agents, prompt):
            print(message)

    asyncio.run(main())
