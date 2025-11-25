"""
 Tools are regular Python functions decorated with `@tool(parse_docstring=True)` so LangChain can expose their signatures and docstrings to the LLM.

"""


from langchain.tools import tool 
import sqlite3
from pathlib import Path
import os
import requests

BASE_DIR = Path(__file__).resolve().parent


DB_PATH = Path(os.getenv("DATABASE_URL", "sqlite:///./data/context_agent.db").replace("sqlite:///", ""))


@tool(parse_docstring=True)
def search_articles(query : str , limit : int = 5) -> str:
    """
    Search internal articles in the articles DB for entries matching the query and return the top results.

    Args :
        query :  search query string
        limit : number of results to return (default is 5)
    Returns :
        A string representation of the top matching articles.
    """

    conn = sqlite3.connect(DB_PATH)
    curr = conn.cursor()
    curr.execute("SELECT title, content FROM articles WHERE content LIKE ? LIMIT ?", (f"%{query}%", limit))
    rows = curr.fetchall() 
    conn.close()
    if not rows :
        return "No matching articles found."
    out = []
    for i ,(title, content) in enumerate (rows,1):
        out.append(f"{i}. {title}\n{content}\n")

    return "\n".join(out)

@tool(parse_docstring=True)
def web_search(query : str, limit : int = 5) -> str:
    """
    Perform a web search using the DuckDuckGo Instant Answer API and return the top results.

    Args :
        query : search query string
        limit : number of results to return (default is 5)
    Returns :
        A string representation of the top search results.
    """
    url = "https://api.duckduckgo.com/"
    params = {
        "q" : query,
        "format" : "json",
        "no_redirect" : 1,
        "no_html" : 1,
        "skip_disambig" : 1
    }
    response = requests.get(url, params=params)
    data = response.json()
    results = []
    if "RelatedTopics" in data:
        for topic in data["RelatedTopics"][:limit]:
            if "Text" in topic:
                results.append(topic["Text"])
    if not results:
        return "No results found."
    return "\n".join([f"{i+1}. {result}" for i, result in enumerate(results)])

@tool(parse_docstring=True)
def set_user_authenticated(user_id: str) -> str:
    """
    Set the user as authenticated in the users database.

    Args:
        user_id: The unique identifier of the user.
    Returns:

        A confirmation message indicating the user has been authenticated.
    """
    conn = sqlite3.connect(DB_PATH)
    curr = conn.cursor()
    curr.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (?, ?, ?)", (user_id, "User"+user_id, None))
    conn.commit()
    conn.close()
    return f"User {user_id} is now authenticated."

@tool(parse_docstring=True)
def is_user_authenticated(user_id: str) -> str:
    """
    Check if the user is authenticated in the users database.

    Args:
        user_id: The unique identifier of the user.
    Returns:
        A message indicating whether the user is authenticated or not.          

    """
    conn = sqlite3.connect(DB_PATH)
    curr = conn.cursor()
    curr.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    row = curr.fetchone()
    conn.close()
    if row:
        return f"User {user_id} is authenticated."
    else:
        return f"User {user_id} is not authenticated."
    
