import requests
import re

def paper_search(search_text):
    try:
        web_link = f"https://huggingface.co/api/papers/search?q={search_text}"
        response = requests.get(web_link,timeout=10)
        data = response.json()
        papers = data if isinstance(data,list) else data.get("papers",[])
        if not papers:
            return "No academic papers found for related to this."
        results = []
        for paper in papers[:3]: 
            paper_id = paper.get("id","Unknown")
            title =paper.get("title","Unknown")
            summary = paper.get("summary","")
            results.append({"id":paper_id,"title":title,"summary":summary[:1000] if summary else "No summary."})
        return str(results)
    except Exception as e:
        return f"[ERROR]: Not able to search the paper {str(e)}"

def read_paper(paper_id):
    try:
        paper_id = re.sub(r'v\d+$','',paper_id)
        web_link = f"https://huggingface.co/api/papers/{paper_id}"
        response = requests.get(web_link,timeout=10)
        if response.status_code == 404:
            return f"[ERROR]: Paper {paper_id} not indexed on Hugging Face. Use web_fetch on 'https://arxiv.org/abs/{paper_id}' instead."
        data = response.json()
        title = data.get("title","Unknown")
        summary = data.get("summary","No summary available.")
        authors_list = data.get("authors",[])
        authors = [a.get("name","Unknown") for a in authors_list] if authors_list else ["Unknown"]
        published = data.get("publishedAt", "Unknown")
        md_link = f"https://huggingface.co/papers/{paper_id}.md"
        md_response = requests.get(md_link,timeout=10)
        text_response = ""
        if (md_response.status_code == 200) :
            text_response = md_response.text
        details = (f"Title: {title}\n"f"Authors:{', '.join(authors)}\n"f"Published:{published}\n\n" f"Summary:\n{summary}\n\n\n"f"Main Content :\n{text_response}")
        return details[:15000]
    except Exception as e:
        return f"[ERROR]: Not able to read the paper because {str(e)}"

papers_tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "paper_search",
            "description": "Searches Hugging Face for scientific and technical papers. Returns titles, short summaries, and paper IDs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_text": {
                        "type": "string",
                        "description": "The topic or keywords to search for on the web."
                    }
                },
                "required": ["search_text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_paper",
            "description": "Retrieves the full abstract, author list, and publication details for a specific paper using its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "paper_id": {
                        "type": "string",
                        "description": "The exact paper ID string, e.g., '2303.17564'."
                    }
                },
                "required": ["paper_id"]
            }
        }
    }
]