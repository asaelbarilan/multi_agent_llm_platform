# agents/agents_2.py

import asyncio
import subprocess
import sys

class ProblemSolvingAgent:
    def __init__(self, name):
        self.name = name

    async def process_message(self, message):
        response = await self.query_ollama(message)
        return response.strip()

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
