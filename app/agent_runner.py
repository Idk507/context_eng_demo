from .agents import build_agent

def run_agent_step(agent, user_id: str, message: str):
    """Run a single agent step: send a user message, receive responses. This demonstrates state updates.

    Returns: agent_response_text, updated_state
    """
    # The agent object returned by create_agent has a runtime; we create a session-scoped runtime
    runtime = agent.create_runtime(state={
        "user_id": user_id,
        "messages": []
    })

    # Send the user message
    response = runtime.run(message)

    # If any tool returned authentication success, update runtime state
    # (LangChain tool results are part of the runtime; for simplicity, we scan response)
    if isinstance(response, str) and response.startswith("AUTH_SUCCESS:"):
        uid = response.split(":", 1)[1]
        runtime.state.update({"authenticated": True, "user_id": uid})

    return response, runtime.state


