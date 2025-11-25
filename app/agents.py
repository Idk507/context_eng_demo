"""  Agent with the tools , middleware ,lifecycle handling .
"""

from langchain.agents import create_agent 
from langchain.chat_models import ChatOpenAI,init_chat_model
from langchain.agents.middleware import wrap_model_call
from langchain.tools import Tool
from .middleware import state_aware_prompt,inject_file_context,get_summarization_middleware
from .tools import search_articles,web_search,set_user_authenticated,is_user_authenticated


MODEL_NAME = "gpt-4o"
chat_model = init_chat_model(model_name= MODEL_NAME,temperature=0.2)


tools = [
    Tool.from_func(search_articles),
    Tool.from_func(web_search),
    Tool.from_func(set_user_authenticated),
    Tool.from_func(is_user_authenticated)
]


#custom middleware to only show web search after authetication

@wrap_model_call
def selective_tools(request, handler):
    state = request.state
    tools = request.tools
    if not state.get("is_authenticated", False):
        tools = [tool for tool in tools if tool.name != "web_search"]
        request = request.override(tools=tools)
    return handler(request)


def build_agent():
    agent = create_agent(
        model = chat_model,
        tools = tools,
        middleware = [
            state_aware_prompt,
            inject_file_context,
            selective_tools,
            get_summarization_middleware()
        ],
    )
    return agent
