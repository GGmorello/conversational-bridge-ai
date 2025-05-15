import pandas as pd
from openai import OpenAI
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class SearchAgent:
    def __init__(self, api_key: str = None):
        """Initialize the search agent with OpenAI client.
        
        Args:
            api_key (str, optional): OpenAI API key. If not provided, will look for OPENAI_API_KEY in .env file.
        """
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        if not self.client.api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in .env file or pass it directly.")
        
    def load_bonds(self, csv_path: str) -> pd.DataFrame:
        """Load bonds data from CSV file.
        
        Args:
            csv_path (str): Path to the CSV file containing bonds data
            
        Returns:
            pd.DataFrame: DataFrame containing the bonds data
        """
        return pd.read_csv(csv_path)
    
    def _create_system_prompt(self, bonds_df: pd.DataFrame) -> str:
        """Create the system prompt with bonds data context.
        
        Args:
            bonds_df (pd.DataFrame): DataFrame containing bonds data
            
        Returns:
            str: System prompt for the chat completion
        """
        bonds_info = bonds_df.to_dict('records')
        return f"""You are a financial assistant specialized in analyzing bond data. 
        You have access to the following bonds information:
        {bonds_info}
        
        Please analyze the query and provide a clear, accurate response based on the available bond data.
        If the query cannot be answered with the available data, please state that clearly."""
    
    def search(self, query: str, bonds_df: pd.DataFrame) -> str:
        """Search and answer questions about bonds.
        
        Args:
            query (str): The user's question about bonds
            bonds_df (pd.DataFrame): DataFrame containing bonds data
            
        Returns:
            str: The answer to the query
        """
        system_prompt = self._create_system_prompt(bonds_df)
        
        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",  # Using the latest GPT-4 model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content

def main():
    # Example usage
    agent = SearchAgent()
    bonds_df = agent.load_bonds("path/to/your/bonds.csv")
    query = "What is the average yield of all bonds?"
    answer = agent.search(query, bonds_df)
    print(f"Query: {query}")
    print(f"Answer: {answer}")

if __name__ == "__main__":
    main()
