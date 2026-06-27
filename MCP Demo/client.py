from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

import asyncio

async def main():
    client = MultiServerMCPClient(
        {
            "math":{
                "command": "python",
                "args":["mathserver.py"],
                "transport": "stdio"
            },
            "weather":{
                "url": "http://localhost:8000/mcp",
                "transport": "streamable-http"
            }
        }
    )

    tools=await client.get_tools()
    model = ChatGroq(model="qwen/qwen3-32b")
    agent=create_agent(model, tools)

    math_response=await agent.ainvoke({
        "messages":[{"role":"user","content":"What is (3+5) x 12"}]
    })

    weather_response=await agent.ainvoke({
        "messages":[{"role":"user","content":"What is the weather in New York"}]
    })

    print("Weather Response:", weather_response['messages'][-1].content)

    print("Math Response:", math_response['messages'][-1].content)

asyncio.run(main())