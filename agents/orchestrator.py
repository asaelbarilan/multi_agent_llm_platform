# agents/orchestrator.py

from .environment import Environment
from .agents import ProblemSolvingAgent

def initialize_agents():
    agent1 = ProblemSolvingAgent("Solver")
    agent2 = ProblemSolvingAgent("Reviewer")
    return [agent1, agent2]

async def orchestrate_problem_solving(agents, prompt):
    env = Environment()
    for agent in agents:
        env.add_agent(agent)

    env.initiate_conversation(prompt)
    async for message in env.run_conversation():
        yield message
