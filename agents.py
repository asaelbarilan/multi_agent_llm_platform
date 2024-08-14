# import subprocess
#
# class ProblemSolvingAgent:
#     def __init__(self, name):
#         self.name = name
#
#     def process_message(self, message):
#         # Ask the agent to solve the problem and confirm its resolution
#         response = self.query_ollama(message)
#         return response
#
#     def query_ollama(self, prompt):
#         result = subprocess.run(
#             ["ollama", "run", "llama3"],
#             input=prompt,
#             text=True,
#             capture_output=True,
#             encoding='utf-8'
#         )
#         return result.stdout
#
# class Environment:
#     def __init__(self):
#         self.agents = []
#         self.conversation = []
#         self.solved = False
#
#     def add_agent(self, agent):
#         self.agents.append(agent)
#
#     def initiate_conversation(self, prompt):
#         self.conversation.append(f"Initial Prompt: {prompt}")
#
#     def run_conversation(self):
#         iteration_count = 0
#         max_iterations = 3  # Prevent infinite loops
#         while not self.solved and iteration_count < max_iterations:
#             iteration_count += 1
#             print(f"--- Iteration {iteration_count} ---")
#             for i, agent in enumerate(self.agents):
#                 # Share the entire conversation history with each agent
#                 conversation_history = "\n".join(self.conversation)
#                 response = agent.process_message(conversation_history)
#                 print(f"{agent.name} response: {response}")
#                 self.conversation.append(f"{agent.name}: {response}")
#
#                 if self.validate_solution(response):
#                     self.solved = self.verify_solution_with_agents(response)
#                     if self.solved:
#                         print("Solution verified, stopping conversation.")
#                         break
#                 else:
#                     # Introduce follow-up questions between agents
#                     if i < len(self.agents) - 1:
#                         follow_up_question = f"Do you agree with {agent.name}'s response? Can you confirm if the problem is solved?"
#                         self.conversation.append(follow_up_question)
#             if iteration_count >= max_iterations:
#                 print("Max iterations reached, stopping conversation.")
#                 break
#         if not self.solved:
#             print("Conversation ended without a verified solution.")
#
#     def is_problem_solved(self):
#         return self.solved
#
#     def get_last_message(self):
#         return self.conversation[-1]
#
#     def get_solution(self):
#         return self.conversation[-1]
#
#     def validate_solution(self, response):
#         # Check if the response contextually solves the problem by asking if it's solved
#         if "yes problem is solved" or  "we can't solve this" in response.lower():
#             print("Validation check: Solved")
#             return True
#         print("Validation check: Not Solved")
#         return False
#
#     def verify_solution_with_agents(self, solution):
#         # Ask all agents if they agree with the solution
#         for agent in self.agents:
#             verification_prompt = f"The proposed solution is: {solution}\nDo you agree with this solution? If so,say 'yes problem is solved'  and explain why.or if you cant solve the problem say 'we can't solve this' If not, explain why not."
#             verification_response = agent.process_message(verification_prompt)
#             print(f"{agent.name} verification response: {verification_response}")
#             if "no" in verification_response.lower():
#                 print(f"{agent.name} does not agree with the solution.")
#                 return False
#         return True
#
# def initialize_agents():
#     agent1 = ProblemSolvingAgent("Agent1")
#     agent2 = ProblemSolvingAgent("Agent2")
#
#     return [agent1, agent2]
#
# def orchestrate_problem_solving(agents, prompt):
#     env = Environment()
#     for agent in agents:
#         env.add_agent(agent)
#
#     env.initiate_conversation(prompt)
#     env.run_conversation()
#
#     solution = env.get_solution()
#     return env.conversation, solution
#
# # Usage example
# if __name__ == "__main__":
#     agents = initialize_agents()
#     conversation, solution = orchestrate_problem_solving(agents, "how much is 1+1")
#     for message in conversation:
#         print(message)
#     print("Final Solution:", solution)


import asyncio
import subprocess

class ProblemSolvingAgent:
    def __init__(self, name):
        self.name = name

    async def process_message(self, message):
        response = await self.query_ollama(message)
        return response

    async def query_ollama(self, prompt):
        result = await asyncio.create_subprocess_exec(
            "ollama", "run", "llama3",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )
        stdout, _ = await result.communicate(input=prompt)
        return stdout

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
        while not self.solved:
            for agent in self.agents:
                last_message = self.conversation[-1]
                response = await agent.process_message(last_message)
                self.conversation.append(f"{agent.name}: {response}")
                yield f"{agent.name}: {response}"
                if self.validate_solution(response):
                    self.solved = True
                    yield "Solution verified, stopping conversation."
                    return

    def validate_solution(self, response):
        return "yes problem is solved" in response.lower()

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

