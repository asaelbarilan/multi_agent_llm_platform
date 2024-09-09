import asyncio
import subprocess
import sys
from langchain import LLMChain, PromptTemplate


# ------------------------------------------------------------------
# Custom Local LLM (Ollama)
# ------------------------------------------------------------------
class LocalModelLLM:
    """Local model integration."""

    def _call(self, prompt: str) -> str:
        if sys.platform == "win32":
            result = subprocess.run(
                ["ollama", "run", "llama3"],
                input=prompt.encode('utf-8'),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return result.stdout.decode('utf-8')
        else:
            process = asyncio.run(asyncio.create_subprocess_exec(
                "ollama", "run", "llama3",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            ))
            stdout, _ = asyncio.run(process.communicate(input=prompt.encode('utf-8')))
            return stdout.decode('utf-8')


# ------------------------------------------------------------------
# Define Agents: Critic, Actor, Math, Logic, General
# ------------------------------------------------------------------
class CriticAgent:
    """Critic Agent to review and provide feedback."""

    def __init__(self):
        self.name = "CriticAgent"

    def review(self, solution: str) -> str:
        """Provide feedback to the Actor's solution."""
        return f"Critic Agent: Reviewing the solution: {solution}. Feedback: It's okay, but consider this..."


class ActorAgent:
    """Actor Agent to propose solutions."""

    def __init__(self):
        self.name = "ActorAgent"

    def solve(self, problem: str) -> str:
        """Generates a solution."""
        return f"Actor Agent: Solving {problem}. Here is my solution: [Proposed Solution]"


class MathAgent:
    """Agent specialized in math problems."""

    def solve(self, problem: str) -> str:
        return f"Math solution for {problem} is {eval(problem)}."


class LogicAgent:
    """Agent that handles logic problems."""

    def solve(self, problem: str) -> str:
        return f"Logic solution: {problem}"


class GeneralKnowledgeAgent:
    """Agent that handles general knowledge queries using local LLM."""

    def __init__(self, llm):
        self.llm = llm

    def solve(self, problem: str) -> str:
        return self.llm._call(problem)


# ------------------------------------------------------------------
# Orchestrator Agent: Decides which flow to use
# ------------------------------------------------------------------
class OrchestratorAgent:
    def __init__(self, agents):
        self.agents = agents

    def decide_method(self, problem: str) -> str:
        """Decide on the best method based on the problem's context."""
        if "math" in problem.lower():
            return "Sequential"
        elif "logic" in problem.lower():
            return "Collaborative"
        elif "complex" in problem.lower():
            return "CriticActor"
        else:
            return "General"

    def solve(self, problem: str) -> str:
        """Orchestrates the solution process by selecting the best method."""
        method = self.decide_method(problem)
        if method == "Sequential":
            return self.sequential_chain(problem)
        elif method == "Collaborative":
            return self.collaborative_flow(problem)
        elif method == "CriticActor":
            return self.critic_actor_flow(problem)
        else:
            general_agent = next(agent for agent in self.agents if agent.name == "GeneralKnowledgeAgent")
            return general_agent.solve(problem)

    def sequential_chain(self, problem: str) -> str:
        """Sequentially pass the problem through agents."""
        math_agent = next(agent for agent in self.agents if agent.name == "MathAgent")
        logic_agent = next(agent for agent in self.agents if agent.name == "LogicAgent")

        math_solution = math_agent.solve(problem)
        logic_solution = logic_agent.solve(math_solution)
        return f"Sequential Result: {logic_solution}"

    def collaborative_flow(self, problem: str) -> str:
        """Collaborative solving between agents."""
        math_agent = next(agent for agent in self.agents if agent.name == "MathAgent")
        logic_agent = next(agent for agent in self.agents if agent.name == "LogicAgent")

        math_solution = math_agent.solve(problem)
        logic_solution = logic_agent.solve(problem)

        return f"Collaborative Result: Math says: {math_solution} | Logic says: {logic_solution}"

    def critic_actor_flow(self, problem: str) -> str:
        """Critic and Actor working together."""
        actor_agent = next(agent for agent in self.agents if agent.name == "ActorAgent")
        critic_agent = next(agent for agent in self.agents if agent.name == "CriticAgent")

        actor_solution = actor_agent.solve(problem)
        critic_feedback = critic_agent.review(actor_solution)
        return f"Critic-Actor Result: Actor: {actor_solution} | Critic: {critic_feedback}"


# ------------------------------------------------------------------
# Initialize Agents and Execute the Flow
# ------------------------------------------------------------------

def initialize_agents():
    math_agent = MathAgent()
    logic_agent = LogicAgent()
    llm = LocalModelLLM()
    general_agent = GeneralKnowledgeAgent(llm)
    actor_agent = ActorAgent()
    critic_agent = CriticAgent()

    orchestrator = OrchestratorAgent([
        math_agent, logic_agent, general_agent, actor_agent, critic_agent
    ])
    return orchestrator


async def main():
    orchestrator = initialize_agents()
    problem = "Solve 5 + 3"

    # The orchestrator dynamically selects the best method based on the problem
    result = orchestrator.solve(problem)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
