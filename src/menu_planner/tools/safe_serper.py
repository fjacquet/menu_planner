#!/usr/bin/env python
"""
SafeSerperTool - A robust wrapper for web search with improved error handling

This module provides a more robust search tool that can handle various input formats 
and ensure proper type conversion to prevent validation errors when used by AI agents.
"""

from crewai.tools import BaseTool
import requests
import os


class SafeSerperTool(BaseTool):
    """A robust web search tool with improved error handling"""
    name: str = "search_internet"
    description: str = "A tool to search the internet for up-to-date information on any topic. Use this tool when you need current data or facts about events, people, or concepts."
    
    
    def _run(self, search_query: str) -> str:
        """Execute the search query with error handling"""
        # Validation and normalization
        if not search_query or not isinstance(search_query, str):
            if isinstance(search_query, dict) and 'search_query' in search_query:
                search_query = search_query['search_query']
            elif isinstance(search_query, dict) and 'description' in search_query:
                search_query = search_query['description']
            else:
                search_query = str(search_query)
        
        # API call
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            return "Error: SERPER_API_KEY environment variable not set"
        
        try:
            response = requests.post(
                "https://google.serper.dev/search",
                headers={
                    'X-API-KEY': api_key,
                    'Content-Type': 'application/json'
                },
                json={"q": search_query}
            )
            response.raise_for_status()
            data = response.json()
            
            # Format the results in a user-friendly way
            result = f"Search results for: {search_query}\n\n"
            
            if 'organic' in data:
                for i, item in enumerate(data['organic'][:5], 1):
                    result += f"{i}. {item.get('title', 'No title')}\n"
                    result += f"   {item.get('snippet', 'No description')}\n"
                    result += f"   URL: {item.get('link', 'No link')}\n\n"
            
            return result
        except Exception as e:
            return f"Error performing search: {str(e)}"
    
    async def _arun(self, search_query: str) -> str:
        """Async version of the run method"""
        return self._run(search_query)
