
import asyncio
import subprocess
import sys
from langchain import LLMChain, PromptTemplate
from langchain.llms.base import LLM
from typing import List

# Custom LLM class for your local model
from langchain.llms.base import LLM
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
class ProblemSolvingAgent:
    def __init__(self, name):
        self.name = name
        self.llm = LocalModelLLM()

        # Create a prompt template and LLMChain
        template = "Solve the following problem: {problem}"
        self.prompt = PromptTemplate(template=template, input_variables=["problem"])
        self.chain = LLMChain(prompt=self.prompt, llm=self.llm)

    async def process_message(self, message):
        response = await self.chain.arun({"problem": message})
        return response

class Environment:
    def __init__(self):
        self.agents = []
        self.conversation = []
        self.solved = False

    def add_agent(self, agent):
        self.agents.append(agent)

    def initiate_conversation(self, prompt):
        self.conversation.append(f"Initial Prompt: {prompt}")

    async def run_conversation(self):
        iteration_count = 0
        max_iterations = 3  # Prevent infinite loops
        while not self.solved and iteration_count < max_iterations:
            iteration_count += 1
            print(f"--- Iteration {iteration_count} ---")
            for i, agent in enumerate(self.agents):
                # Share the entire conversation history with each agent
                conversation_history = "\n".join(self.conversation)
                response = await agent.process_message(conversation_history)
                print(f"{agent.name} response: {response}")
                self.conversation.append(f"{agent.name}: {response}")
                yield f"{agent.name}: {response}"

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
        # Check if the response contextually solves the problem by asking if it's solved
        if "yes problem is solved" in response.lower() or "we can't solve this" in response.lower():
            print("Validation check: Solved")
            return True
        print("Validation check: Not Solved")
        return False

    async def verify_solution_with_agents(self, solution):
        # Ask all agents if they agree with the solution
        for agent in self.agents:
            verification_prompt = f"The proposed solution is: {solution}\nDo you agree with this solution? If so, say 'yes problem is solved' and explain why. If you can't solve the problem, say 'we can't solve this'. If not, explain why not."
            verification_response = await agent.process_message(verification_prompt)
            print(f"{agent.name} verification response: {verification_response}")
            if "no" in verification_response.lower():
                print(f"{agent.name} does not agree with the solution.")
                return False
        return True

def initialize_agents():
    agent1 = ProblemSolvingAgent("Agent1")
    agent2 = ProblemSolvingAgent("Agent2")
    return [agent1, agent2]

async def orchestrate_problem_solving(agents, prompt):
    env = Environment()
    for agent in agents:
        env.add_agent(agent)

    env.initiate_conversation(prompt)
    async for message in env.run_conversation():
        yield message

# Usage example
if __name__ == "__main__":
    agents = initialize_agents()
    prompt = "give me a method to solve the lottery"

    async def main():
        async for message in orchestrate_problem_solving(agents, prompt):
            print(message)

    asyncio.run(main())

