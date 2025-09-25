import pytest
from unittest.mock import patch, MagicMock
from src.agents import OrchestratorAgent

@patch('src.agents.model')
def test_orchestrator_routes_to_sauter_agent(mock_model):
    mock_routing_response = MagicMock()
    mock_routing_response.text = 'sauter_agent'
    mock_final_response = MagicMock()
    mock_final_response.text = 'A Sauter é uma empresa de tecnologia.'
    mock_model.generate_content.side_effect = [mock_routing_response, mock_final_response]

    orchestrator = OrchestratorAgent()
    question = "fale sobre a sauter"
    response = orchestrator.handle_question(question)

    assert response == 'A Sauter é uma empresa de tecnologia.'
    assert mock_model.generate_content.call_count == 2

@patch('src.agents.model')
def test_orchestrator_routes_to_data_agent(mock_model):
    mock_routing_response = MagicMock()
    mock_routing_response.text = 'data_agent'
    mock_final_response = MagicMock()
    mock_final_response.text = 'O volume da bacia do Tiete foi X.'
    mock_model.generate_content.side_effect = [mock_routing_response, mock_final_response]

    orchestrator = OrchestratorAgent()
    question = "qual o volume da bacia do tiete?"
    response = orchestrator.handle_question(question)

    assert response == 'O volume da bacia do Tiete foi X.'
    assert mock_model.generate_content.call_count == 2