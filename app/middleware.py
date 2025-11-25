"""
Middleware implementations: dynamic prompt, file injection (transient), summarization (lifecycle). We'll use LangChain middleware decorators described in the docs.

"""

from langchain.agents.middleware  import dynamic_prompt,wrap_model_call,ModelRequest,ModelResponse 
from typing import Callable
from langchain.agents.middleware import SummarizationMiddleware


@dynamic_prompt
def state_aware_prompt(request : ModelRequest) -> str :
    """
    Return a dynamic system prompt based on the message count and runtime flags in state.
    """
    message_count = len(request.messages)
    base = "You are an helpful AI assistant who is specialized in the company's knowledge base."
    if request.state.get("user_role") == "admin":
        base += " You have admin privileges."
    if message_count > 10:
        base += " The conversation is quite long, please be concise in your responses."
    return base

@wrap_model_call
def inject_file_context(request : ModelRequest,handler : Callable[[ModelRequest],ModelResponse]) -> ModelResponse:
    """
    Middleware to inject file content into the user message if a file_path is provided in state.
    """
    uploaded = request.state.get("upload_files",[])
    if uploaded : 
        lines = [f" - {f['name']} : {f['summary'][:200]}" for f in uploaded]
        file_context = "\n".join(lines)
        # append as a user message so the assistant see it with the right role 
        new_message = [*request.messages, {"role":"user","content": file_context}]
        request = request.override(messages=new_message)
    return handler(request)


def get_summarization_middleware():
    """
    Return the smaller cheaper model when the conversation longer than threshold    
    """ 
    return SummarizationMiddleware(
        model = "gpt-4o",
        max_tokens_before_summary = 2000,
        message_to_keep = 20
    )


