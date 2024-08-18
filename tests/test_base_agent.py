# File: tests/test_base_agent.py

import pytest
from app.agent.base_agent import BaseAgent
from tests.mocks.mock_llm import create_mock_llm

@pytest.fixture
def mock_responses():
    return [
        "<interview_stage>Introduction</interview_stage><interviewer>Hello! Welcome to the interview. Can you please introduce yourself?</interviewer>",
        "<interview_stage>Technical Questions</interview_stage><interviewer>Great introduction! Let's move on to some technical questions. Can you explain the difference between a list and a tuple in Python?</interviewer>",
        "<interview_stage>Closing</interview_stage><interviewer>Thank you for your time. We'll be in touch soon with next steps.</interviewer>"
    ]

@pytest.fixture
def mock_llm(mock_responses):
    return create_mock_llm(mock_responses, model_name="gpt-3.5-turbo")

@pytest.fixture
def base_agent(mock_llm):
    class TestAgent(BaseAgent):
        def get_prompt(self):
            return "This is a test prompt for the interview."

        def num_tokens_from_string(self, string: str) -> int:
            return len(string.split())

    return TestAgent(mock_llm, "Mock resume", "Mock job description")

def test_base_agent_initialization(base_agent):
    assert base_agent.resume_content == "Mock resume"
    assert base_agent.job_description_content == "Mock job description"

def test_base_agent_interview_chain(base_agent, mock_responses):
    response = base_agent.interview_chain.invoke({"input": "Start the interview"})
    assert response == mock_responses[0]

def test_base_agent_extract_interviewer_content(base_agent, mock_responses):
    response = base_agent.interview_chain.invoke({"input": "Start the interview"})
    interviewer_content = base_agent.extract_interviewer_content(response)
    assert interviewer_content == "Hello! Welcome to the interview. Can you please introduce yourself?"

def test_base_agent_extract_interview_stage(base_agent, mock_responses):
    response = base_agent.interview_chain.invoke({"input": "Start the interview"})
    stage = base_agent.extract_interview_stage(response)
    assert stage == "Introduction"

def test_base_agent_multiple_calls(base_agent, mock_responses):
    response1 = base_agent.interview_chain.invoke({"input": "Start the interview"})
    assert response1 == mock_responses[0]
    response2 = base_agent.interview_chain.invoke({"input": "Continue"})
    assert response2 == mock_responses[1]

def test_base_agent_out_of_responses(base_agent):
    base_agent.interview_chain.invoke({"input": "Start"})
    base_agent.interview_chain.invoke({"input": "Continue"})
    base_agent.interview_chain.invoke({"input": "Finish"})
    with pytest.raises(IndexError):
        base_agent.interview_chain.invoke({"input": "Extra"})

def test_base_agent_token_usage(base_agent):
    base_agent.interview_chain.invoke({"input": "Start the interview"})
    usage = base_agent.get_token_usage()
    assert "prompt_tokens" in usage
    assert "completion_tokens" in usage
    assert "total_tokens" in usage
    assert "total_cost" in usage

def test_base_agent_num_tokens_from_string(base_agent):
    text = "This is a test string"
    num_tokens = base_agent.num_tokens_from_string(text)
    assert num_tokens == 5  # 简化的 token 计算方法

def test_get_prompt(base_agent):
    prompt = base_agent.get_prompt()
    assert prompt == "This is a test prompt for the interview."