from langchain_community.utilities import WikipediaAPIWrapper
from crewai.tools import tool


@tool("search_wikipedia")
def search_wikipedia(query: str) -> str:
    """Fetches a summary from Wikipedia for the given query."""
    wiki_tool = WikipediaAPIWrapper()    
    return wiki_tool.run(query)