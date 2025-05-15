from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pandas as pd
from agent.portfolio import PortfolioAgent

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

# Initialize the portfolio agent and load bonds data
portfolio_agent = PortfolioAgent()
bonds_df = pd.read_csv("src/agent/bonds.csv")

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        if not request.messages:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        # Convert Pydantic messages to the format expected by PortfolioAgent
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Create portfolio using the agent
        result = portfolio_agent.create_portfolio(messages, bonds_df)
        
        return {
            "message": result["portfolio_recommendation"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 