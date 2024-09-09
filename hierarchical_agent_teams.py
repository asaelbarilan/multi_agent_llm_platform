import asyncio
import subprocess
import sys
from langchain import LLMChain, PromptTemplate
from langchain.llms.base import LLM
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain.prompts import ChatPromptTemplate


# Custom LLM class for your local model
class LocalModelLLM(LLM):
    def _call(self, prompt: str, *args, **kwargs) -> str:
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

    @property
    def _llm_type(self) -> str:
        return "local_model_llm"

    @property
    def _identifying_params(self) -> dict:
        return {"model_name": "ollama llama3"}


# Problem Solving Agent (Worker)
class ProblemSolvingAgent:
    def __init__(self, name):
        self.name = name
        self.llm = LocalModelLLM()

        # Create a prompt template and LLMChain for problem solving
        template = "Solve the following problem: {problem}"
        self.prompt = PromptTemplate(template=template, input_variables=["problem"])
        self.chain = LLMChain(prompt=self.prompt, llm=self.llm)

    async def process_message(self, message):
        response = await self.chain.arun({"problem": message})
        return response


# Decision Orchestrator (Coordinator)
class OrchestratorAgent:
    def __init__(self, name):
        self.name = name
        self.llm = LocalModelLLM()

        # Define the decision-making template
        template = (
            "Based on the problem: '{problem}', decide which method to use.\n"
            "Options are:\n"
            "1. Sequential Chain\n"
            "2. Parallel Chain\n"
            "3. Collaborative Multi-Agent\n"
            "Explain your reasoning."
        )
        self.prompt = PromptTemplate(template=template, input_variables=["problem"])
        self.chain = LLMChain(prompt=self.prompt, llm=self.llm)

    async def decide_strategy(self, problem):
        # Get the decision from the orchestrator
        decision = await self.chain.arun({"problem": problem})
        print(f"Orchestrator Decision: {decision}")
        return decision


# Environment for running agents in a collaborative way
class Environment:
    def __init__(self):
        self.agents = []
        self.conversation = []
        self.solved = False

    def add_agent(self, agent):
        self.agents.append(agent)

    def initiate_conversation(self, prompt):
        self.conversation.append(f"Initial Prompt: {prompt}")

    async def run_conversation(self, strategy):
        iteration_count = 0
        max_iterations = 5  # Prevent infinite loops
        while not self.solved and iteration_count < max_iterations:
            iteration_count += 1
            print(f"--- Iteration {iteration_count} ---")
            for i, agent in enumerate(self.agents):
                conversation_history = "\n".join(self.conversation)
                response = await agent.process_message(conversation_history)
                print(f"{agent.name} response: {response}")
                self.conversation.append(f"{agent.name}: {response}")
                yield f"{agent.name}: {response}"

                if strategy == "Collaborative Multi-Agent":
                    next_agent = self.agents[(i + 1) % len(self.agents)]
                    refined_response = await next_agent.process_message(f"{response}\nAnalyze and refine the response")
                    print(f"{next_agent.name} refined response: {refined_response}")
                    self.conversation.append(f"{next_agent.name}: {refined_response}")
                    yield f"{next_agent.name}: {refined_response}"

                if self.validate_solution(response):
                    self.solved = await self.verify_solution_with_agents(response)
                    if self.solved:
                        yield "Solution verified, stopping conversation."
                        return
            if iteration_count >= max_iterations:
                print("Max iterations reached, stopping conversation.")
                break
        if not self.solved:
            print("Conversation ended without a verified solution.")

    def validate_solution(self, response):
        if "yes problem is solved" in response.lower() or "we can't solve this" in response.lower():
            print("Validation check: Solved")
            return True
        print("Validation check: Not Solved")
        return False

    async def verify_solution_with_agents(self, solution):
        for agent in self.agents:
            verification_prompt = f"The proposed solution is: {solution}\nDo you agree with this solution? If so, say 'yes problem is solved'."
            verification_response = await agent.process_message(verification_prompt)
            print(f"{agent.name} verification response: {verification_response}")
            if "no" in verification_response.lower():
                print(f"{agent.name} does not agree with the solution.")
                return False
        return True


# Initialize agents
def initialize_agents():
    orchestrator = OrchestratorAgent("Orchestrator")
    agent1 = ProblemSolvingAgent("Agent1")
    agent2 = ProblemSolvingAgent("Agent2")
    return orchestrator, [agent1, agent2]


# Main function to run the hierarchical team of agents
async def orchestrate_problem_solving(orchestrator, agents, prompt):
    env = Environment()
    for agent in agents:
        env.add_agent(agent)

    env.initiate_conversation(prompt)

    # Orchestrator decides the strategy
    strategy = await orchestrator.decide_strategy(prompt)

    # Run the conversation based on the strategy
    async for message in env.run_conversation(strategy):
        yield message


# Usage example
if __name__ == "__main__":
    orchestrator, agents = initialize_agents()
    prompt = "create a phone calculator app"


    async def main():
        async for message in orchestrate_problem_solving(orchestrator, agents, prompt):
            print(message)


    asyncio.run(main())
