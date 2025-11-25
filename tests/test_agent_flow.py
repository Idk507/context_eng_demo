from app.agents import build_agent

def test_agent_creation():
    agent = build_agent()
    assert agent is not None
    