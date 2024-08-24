import asyncio

import asyncio
import subprocess
import sys

class ProblemSolvingAgent:
    def __init__(self, name):
        self.name = name

    async def process_message(self, message):
        response = await self.query_ollama(message)
        return response

    async def query_ollama(self, prompt):
        if sys.platform == "win32":
            # Windows-specific workaround
            result = subprocess.run(
                ["ollama", "run", "llama3"],
                input=prompt.encode('utf-8'),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return result.stdout.decode('utf-8')
        else:
            # Other platforms
            process = await asyncio.create_subprocess_exec(
                "ollama", "run", "llama3",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate(input=prompt.encode('utf-8'))
            return stdout.decode('utf-8')
#
# class ProblemSolvingAgent:
#     def __init__(self, name):
#         self.name = name
#
#     async def process_message(self, message):
#         # Ask the agent to solve the problem and confirm its resolution
#         response = await self.query_ollama(message)
#         return response
#
#     async def query_ollama(self, prompt):
#         process = await asyncio.create_subprocess_exec(
#             "ollama", "run", "llama3",
#             stdin=asyncio.subprocess.PIPE,
#             stdout=asyncio.subprocess.PIPE,
#             stderr=asyncio.subprocess.PIPE
#         )
#
#         stdout, stderr = await process.communicate(input=prompt.encode('utf-8'))
#
#         if stderr:
#             raise Exception(f"Subprocess error: {stderr.decode('utf-8')}")
#
#         return stdout.decode('utf-8')


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
    prompt = "Solve 1+1"


    async def main():
        async for message in orchestrate_problem_solving(agents, prompt):
            print(message)


    asyncio.run(main())
