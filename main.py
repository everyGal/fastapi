from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# Add CORS middleware to allow Agno Playground connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Agno Playground API is running"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get('message', '')
    return {
        "response": f"You said: {message}",
        "content": f"You said: {message}"
    }

@app.get("/api/agents")
async def list_agents():
    # Mock response for agents endpoint
    return {
        "agents": [
            {
                "id": "default-agent",
                "name": "Default Agent",
                "description": "A simple echo agent"
            }
        ]
    }

@app.post("/api/agents/{agent_id}/run")
async def run_agent(agent_id: str, request: Request):
    data = await request.json()
    message = data.get('message', '')
    return {
        "response": f"Agent {agent_id} received: {message}",
        "content": f"Agent {agent_id} received: {message}"
    }
