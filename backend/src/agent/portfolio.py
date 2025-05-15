import pandas as pd
from openai import OpenAI
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from agent.search import SearchAgent

# Load environment variables from .env file
load_dotenv()

class PortfolioAgent:
    def __init__(self, api_key: str = None):
        """Initialize the portfolio agent with OpenAI client and search agent.
        
        Args:
            api_key (str, optional): OpenAI API key. If not provided, will look for OPENAI_API_KEY in .env file.
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        if not self.client.api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in .env file or pass it directly.")
        self.search_agent = SearchAgent(api_key=api_key)
    
    def _get_search_tool(self) -> Dict[str, Any]:
        """Define the search tool for function calling.
        
        Returns:
            Dict[str, Any]: Tool definition for OpenAI function calling
        """
        return {
            "type": "function",
            "function": {
                "name": "search_bonds",
                "description": "Search for bonds that match specific criteria",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to find relevant bonds"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    
    def create_portfolio(self, messages: List[Dict[str, str]], bonds_df: pd.DataFrame) -> Dict[str, Any]:
        """Create a portfolio based on user requirements.
        
        Args:
            messages (List[Dict[str, str]]): List of message dictionaries with 'role' and 'content' keys
            bonds_df (pd.DataFrame): DataFrame containing bonds data
            
        Returns:
            Dict[str, Any]: Portfolio recommendation with explanation
        """
        # First, let's understand the user's requirements
        system_prompt = """
You are a fixed-income investment advisor tasked with constructing bond portfolios using a dataset of available bonds. Each bond includes the following fields: issuer, ask price, coupon, yield, maturity date, credit rating, currency, and ISIN.

You also have access to a search tool that can be used to:
•⁠  ⁠Retrieve missing or updated information on issuers or bonds (e.g., rating, news, credit outlook)
•⁠  ⁠Validate credit quality, issuer reputation, or recent developments
•⁠  ⁠Fill in gaps in the dataset if required to complete the recommendation

Client Investment Preferences (specified at runtime):

1.⁠ ⁠Risk Appetite:
   - Conservative (investment-grade only)
   - Moderate (mix of investment-grade and high-yield)
   - Aggressive (high-yield permitted)

2.⁠ ⁠Investment Horizon:
   - Short-term (<3 years)
   - Medium-term (3–7 years)
   - Long-term (>7 years)

3.⁠ ⁠Income Needs:
   - High income (focus on higher coupon/yield)
   - Capital preservation (focus on safety, liquidity, and quality)

4.⁠ ⁠Currency Preference:
   - EUR-only
   - Multi-currency

5.⁠ ⁠Maturity Preference:
   One of the following:
   - Custom Range: Bonds maturing between specific dates (e.g., Jan 2026 – Dec 2030)
   - Bullet Maturity: Bonds clustered near a target year (e.g., 2030 ± 1 year)
   - Laddered Maturities: User specifies:
     - Minimum maturity
     - Maximum maturity
     - Gap between maturities (e.g., 1 year)
     - You must select bonds that fall as close as possible to these time intervals

Bond Selection Criteria:

•⁠  ⁠Maximize yield consistent with user-defined risk and maturity preferences
•⁠  ⁠Ensure diversification across issuers and maturities
•⁠  ⁠Only include bonds with available ask prices
•⁠  ⁠Use your search tool if key data (like ratings) is missing or unclear

Portfolio Output:

•⁠  ⁠List of 5–10 recommended bonds
•⁠  ⁠Suggested portfolio weights (as % of total)
•⁠  ⁠Justification for each recommendation (e.g., rating fit, yield advantage, maturity match)
•⁠  ⁠Portfolio-level summary:
  - Weighted average yield
  - Average maturity
  - Risk profile (based on ratings or spread)

Use the provided bond dataset to make all decisions. Be clear, structured, and tailored to the user's preferences.
"""
        
        # Add system message at the beginning
        conversation_messages = [{"role": "system", "content": system_prompt}] + messages
        print(conversation_messages)
        # Initial call to understand requirements and plan the portfolio
        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=conversation_messages,
            tools=[self._get_search_tool()],
            tool_choice="auto"
        )
        print(response)
        # Process the response and handle function calls
        while True:
            message = response.choices[0].message
            conversation_messages.append(message)
            
            if message.tool_calls:
                # Handle the function call
                tool_call = message.tool_calls[0]
                if tool_call.function.name == "search_bonds":
                    # Execute the search
                    search_query = eval(tool_call.function.arguments)["query"]
                    search_result = self.search_agent.search(search_query, bonds_df)
                    
                    # Add the function response to messages
                    conversation_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": search_result
                    })
                    
                    # Get the next response
                    response = self.client.chat.completions.create(
                        model="gpt-4-turbo-preview",
                        messages=conversation_messages,
                        tools=[self._get_search_tool()],
                        tool_choice="auto"
                    )
                    print(response)
            else:
                # No more function calls, we have our final response
                break
        
        return {
            "portfolio_recommendation": message.content,
            "raw_messages": conversation_messages  # Including raw messages for debugging if needed
        }

def main():
    # Example usage
    agent = PortfolioAgent()

    bond_df = pd.read_csv("src/agent/bonds.csv")    
    # Example conversation messages
    messages = [
        {"role": "user", "content": "I need a conservative portfolio with a focus on government bonds"},
        {"role": "assistant", "content": "I understand you're looking for a conservative portfolio. Could you specify your investment horizon and minimum yield requirements?"},
        {"role": "user", "content": "I'm looking for a 5-year investment horizon and would like at least 3% yield"}
    ]
    
    result = agent.create_portfolio(messages, bond_df)
    print("Portfolio Recommendation:")
    print(result["portfolio_recommendation"])

if __name__ == "__main__":
    main() 