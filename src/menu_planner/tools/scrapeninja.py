from crewai.tools import BaseTool
from typing import Type, List, Optional
from pydantic import BaseModel, Field
import requests
import json
import os


class ScrapeNinjaInput(BaseModel):
    """Input schema for ScrapeNinja tool with advanced options"""
    url: str = Field(..., description="The URL to scrape")
    headers: Optional[List[str]] = Field(None, description="Custom headers to include")
    retry_num: Optional[int] = Field(1, description="Number of retry attempts")
    geo: Optional[str] = Field(None, description="Geolocation for request (e.g. 'us', 'eu')")
    proxy: Optional[str] = Field(None, description="Proxy server to use (format: http://user:pw@host:port)")
    follow_redirects: Optional[int] = Field(1, description="Whether to follow redirects (0 or 1)")
    timeout: Optional[int] = Field(8, description="Request timeout in seconds")
    text_not_expected: Optional[List[str]] = Field(None, description="Text patterns that should not appear")
    status_not_expected: Optional[List[int]] = Field(None, description="HTTP status codes that should not appear")
    extractor: Optional[str] = Field(None, description="Custom extractor JavaScript function")


class ScrapeNinjaTool(BaseTool):
    name: str = "ScrapeNinja"
    description: str = "Scrapes website content using the ScrapeNinja API with advanced options"
    args_schema: Type[BaseModel] = ScrapeNinjaInput

    def _run(self, **kwargs) -> str:
        """Scrape a website using ScrapeNinja API with advanced options"""
        api_url = "https://scrapeninja.p.rapidapi.com/scrape"
        api_key = os.getenv("RAPIDAPI_KEY")
        
        if not api_key:
            return "Error: RAPIDAPI_KEY environment variable not set"
            
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "scrapeninja.p.rapidapi.com"
        }
        
        payload = {
            "url": kwargs["url"],
            "retryNum": kwargs.get("retry_num", 1),
            "followRedirects": kwargs.get("follow_redirects", 1),
            "timeout": kwargs.get("timeout", 8)
        }
        
        # Add optional parameters if provided
        if "headers" in kwargs and kwargs["headers"]:
            payload["headers"] = kwargs["headers"]
        if "geo" in kwargs and kwargs["geo"]:
            payload["geo"] = kwargs["geo"]
        if "proxy" in kwargs and kwargs["proxy"]:
            payload["proxy"] = kwargs["proxy"]
        if "text_not_expected" in kwargs and kwargs["text_not_expected"]:
            payload["textNotExpected"] = kwargs["text_not_expected"]
        if "status_not_expected" in kwargs and kwargs["status_not_expected"]:
            payload["statusNotExpected"] = kwargs["status_not_expected"]
        if "extractor" in kwargs and kwargs["extractor"]:
            payload["extractor"] = kwargs["extractor"]
        
        try:
            response = requests.post(api_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            return response.text
        except Exception as e:
            return f"Error scraping {kwargs['url']}: {str(e)}"


def test_scrapeninja():
    """Test function with basic parameters"""
    tool = ScrapeNinjaTool()
    print("Testing basic ScrapeNinja functionality...")
    result = tool._run(url="https://www.free.fr/freebox/")
    print(f"Result: {result[:200]}..." if len(result) > 200 else f"Result: {result}")

    print(f"Result: {result}")

if __name__ == "__main__":
    test_scrapeninja()
