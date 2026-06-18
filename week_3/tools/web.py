import os
import requests
import trafilatura
from urllib.parse import urlparse

def web_search(search_text):
    try:
        api_key = os.environ.get("SERPER_API_KEY")
        web_link = "https://google.serper.dev/search"
        parameters = {"q":search_text}
        headers = {'X-API-KEY':api_key,'Content-Type':'application/json'}
        response = requests.post(web_link,headers=headers,json=parameters,timeout=10)
        data = response.json() 
        organic_results = data.get("organic",[])[:5]
        if not organic_results:
            return "No results found related to this query."
        results = []
        for item in organic_results:
            results.append({"title":item.get("title"),"link":item.get("link"),"snippet":item.get("snippet")})   
        return str(results)
    except Exception as e:
        return f"[ERROR]: Not able to search because {str(e)}"

def web_fetch(web_link):
    try:
        headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        parsed_link = urlparse(web_link)
        is_root = parsed_link.path in("","/")
        if is_root :
            base_link = f"{parsed_link.scheme}://{parsed_link.netloc}"
            try :
                response = requests.get(f"{base_link}/llms.txt",headers=headers,allow_redirects=True,timeout=10)
                if response.status_code == 200:
                    text = f"[llms.txt found]\n\n{response.text}\n\n---\nOriginal URL: {web_link}"
                    return text[:5000]
            except Exception:
                pass
        response = requests.get(web_link,headers=headers,timeout=10)
        response.raise_for_status()
        text = trafilatura.extract(response.text,include_comments=False,include_tables=True)
        if text:
            return text[:5000]
        else:
            return "[WARNING]: Not able to extract readable data from this page."
    except Exception as e:
        return f"[ERROR]: Not able to fetch the data because {str(e)}"

web_tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Searches the web for a query and returns titles, URLs, and snippets.",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_text": {
                        "type": "string",
                        "description": "The search text to look up on the internet."
                    }
                },
                "required": ["search_text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_fetch",
            "description": "Fetches and reads the raw text content of a specific URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "web_link": {
                        "type": "string",
                        "description": "The exact link of the webpage to read."
                    }
                },
                "required": ["web_link"]
            }
        }
    }
]