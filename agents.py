# File: agents.py

import asyncio
import subprocess
import sys
import re
import json
import os
from typing import Optional, List, Mapping, Any
from pydantic import Field

# Corrected imports
from langchain.prompts import PromptTemplate
from langchain.llms.base import LLM
from langchain.tools import BaseTool

# Custom LLM class for your local model (using Ollama)
class LocalModelLLM(LLM):
    model_name: str
    max_new_tokens: int = Field(default=256)

    def __post_init__(self):
        super().__post_init__()
        # Any additional initialization code

    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        try:
            if sys.platform == "win32":
                # Windows-specific workaround
                result = subprocess.run(
                    ["ollama", "run", self.model_name],
                    input=prompt.encode('utf-8'),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True  # Add shell=True for Windows
                )
                # Debugging: Print stdout and stderr
                print("OLLAMA STDOUT:", result.stdout.decode('utf-8'))
                print("OLLAMA STDERR:", result.stderr.decode('utf-8'))

                error_message = result.stderr.decode('utf-8') if result.stderr else ''
                if result.returncode != 0:
                    print(f"LLM error: {error_message}")
                    raise Exception(f"Error in LLM call: {error_message}")
                return result.stdout.decode('utf-8')
            else:
                # For other platforms, use asyncio subprocess
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(self.async_call(prompt))
                return result
        except Exception as e:
            print(f"Exception in _call: {e}")
            raise

    async def async_call(self, prompt: str) -> str:
        try:
            process = await asyncio.create_subprocess_exec(
                "ollama", "run", self.model_name,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate(input=prompt.encode('utf-8'))
            # Debugging: Print stdout and stderr
            print("OLLAMA STDOUT:", stdout.decode('utf-8'))
            print("OLLAMA STDERR:", stderr.decode('utf-8'))

            error_message = stderr.decode('utf-8') if stderr else ''
            if process.returncode != 0:
                print(f"LLM error: {error_message}")
                raise Exception(f"Error in LLM call: {error_message}")
            return stdout.decode('utf-8')
        except Exception as e:
            print(f"Exception in async_call: {e}")
            raise

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"model_name": self.model_name}

# Code Execution Tool
class CodeExecutorTool(BaseTool):
    name = "code_executor"
    description = "Executes Python code and returns the output."

    def _run(self, code):
        try:
            # Define a restricted execution environment
            restricted_globals = {"__builtins__": {}}
            restricted_locals = {}
            exec(code, restricted_globals, restricted_locals)
            return restricted_locals.get('output', 'No output variable defined.')
        except Exception as e:
            return f"Error during execution: {str(e)}"

    async def _arun(self, code):
        # For async execution, implement if needed
        return self._run(code)

# Problem Solving Agent
class ProblemSolvingAgent:
    def __init__(self, name, role, task, llm, retriever=None):
        self.name = name
        self.role = role
        self.task = task
        self.llm = llm
        self.retriever = retriever
        self.tools = [CodeExecutorTool()]

    def process(self, context):
        # Retrieve relevant documents if RAG is enabled
        retrieved_info = ""
        if self.retriever:
            docs = self.retriever.get_relevant_documents(self.task)
            retrieved_info = "\n".join([doc.page_content for doc in docs])

        prompt_template = PromptTemplate(
            input_variables=["role", "task", "context", "retrieved_info"],
            template="""
Role: {role}
Task: {task}
Context: {context}
Retrieved Information: {retrieved_info}

As {role}, think through the task step-by-step and provide your reasoning before giving the final output.

Your response should include:
- Your reasoning process.
- The final output or answer.

If you write code, enclose it within triple backticks and specify the language, like ```python
code_here
```.
"""
        )
        chain = prompt_template | self.llm
        try:
            output = chain.invoke({
                "role": self.role,
                "task": self.task,
                "context": context,
                "retrieved_info": retrieved_info
            })
            print(f"Agent {self.name} Output:\n{output}")
        except Exception as e:
            print(f"Error invoking chain for agent {self.name}: {e}")
            raise

        # Check for code blocks and execute them
        code_blocks = re.findall(r'```python\n(.*?)\n```', output, re.DOTALL)
        execution_results = ""
        for code in code_blocks:
            result = self.tools[0].run(code)
            execution_results += f"\nExecution Result:\n{result}"

        return output + execution_results

# Orchestrator Agent
class OrchestratorAgent:
    def __init__(self, llm):
        self.llm = llm
        self.agent_list = []

    def define_purpose(self, purpose):
        # Generate a plan and create agents accordingly
        plan_prompt = PromptTemplate(
            input_variables=["purpose"],
            template="""
You are an AI orchestrator. The purpose is: {purpose}

1. Break down the purpose into tasks.
2. Decide which agents are needed to accomplish these tasks.
3. For each agent, define its name, role, and responsibilities.

Provide the plan strictly as a JSON array with no additional text or explanations. The JSON should follow this exact format:

[
  {{
    "agent_name": "Agent1",
    "role": "Role description",
    "task": "Task description"
  }},
  ...
]
"""
        )
        chain = plan_prompt | self.llm
        try:
            plan = chain.invoke({"purpose": purpose})
            print(f"Generated Plan JSON: {plan}")  # Debugging statement
        except Exception as e:
            print(f"Error invoking plan chain: {e}")
            raise
        return plan

    def create_agents(self, plan_json):
        try:
            # Trim any leading/trailing whitespace
            trimmed_plan = plan_json.strip()

            # Validate that the JSON starts with '[' and ends with ']'
            if not trimmed_plan.startswith('[') or not trimmed_plan.endswith(']'):
                print("Plan JSON does not start with '[' or end with ']'")
                raise Exception("Invalid JSON plan")

            plan = json.loads(trimmed_plan)
            print(f"Parsed Plan: {plan}")  # Debugging statement
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError: {e}")
            print(f"Received Plan JSON: {plan_json}")
            raise Exception("Invalid JSON plan")
        except Exception as e:
            print(f"Exception in create_agents: {e}")
            raise

        for agent_info in plan:
            try:
                agent = ProblemSolvingAgent(
                    name=agent_info["agent_name"],
                    role=agent_info["role"],
                    task=agent_info["task"],
                    llm=self.llm
                )
                self.agent_list.append(agent)
                print(f"Created Agent: {agent.name}")  # Debugging statement
            except KeyError as ke:
                print(f"Missing key in agent_info: {ke}")
                continue
            except Exception as e:
                print(f"Error creating agent {agent_info.get('agent_name', 'Unknown')}: {e}")
                continue

# Environment
class Environment:
    def __init__(self):
        self.conversation = []
        self.solved = False

    def run(self, orchestrator, initial_purpose):
        # Orchestrator defines purpose and creates agents
        plan_json = orchestrator.define_purpose(initial_purpose)
        orchestrator.create_agents(plan_json)

        # Main loop
        context = ""
        for agent in orchestrator.agent_list:
            response = agent.process(context)
            print(f"{agent.name}:\n{response}\n")
            self.conversation.append(f"{agent.name}:\n{response}")
            context += f"\n{agent.name}:\n{response}"

            # Simple validation to check if task mentions completion
            if "task completed" in response.lower():
                self.solved = True

        if self.solved:
            print("All tasks completed successfully.")
        else:
            print("Tasks could not be completed.")

    def get_conversation(self):
        return self.conversation

# Initialize agents
def initialize_agents(llm):
    orchestrator = OrchestratorAgent(llm=llm)
    return orchestrator

# Function to orchestrate problem solving
def orchestrate_problem_solving(orchestrator, prompt):
    env = Environment()
    env.run(orchestrator, prompt)
    return env.get_conversation()
