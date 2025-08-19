"""
Tests for AIGenerator tool calling functionality

This test suite validates the AIGenerator's interaction with Claude API and tool execution.
Key focus areas include tool calling decisions, parameter passing, conversation history
integration, and error handling.

The tests use MockAnthropicClient to simulate Claude API responses without making actual
API calls, enabling fast and reliable testing.

Test coverage:
- Basic response generation without tools
- Tool calling logic and execution flow
- Conversation history integration with tool responses  
- Error handling during tool execution
- Multiple tool calls in a single response
- API parameter configuration and message formatting
- System prompt content validation
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import anthropic

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ai_generator import AIGenerator
from test_helpers import (
    MockAnthropicClient, 
    MockToolManager, 
    mock_anthropic_client, 
    mock_tool_manager,
    assert_tool_called_with
)


class TestAIGeneratorToolCalling:
    """Test suite for AIGenerator tool calling functionality"""
    
    def test_generate_response_without_tools(self, mock_anthropic_client):
        """Test basic response generation without tools"""
        # Setup
        mock_anthropic_client.set_response("This is a general response about programming.")
        
        with patch('anthropic.Anthropic', return_value=mock_anthropic_client):
            generator = AIGenerator(api_key="test_key", model="claude-3-haiku-20240307")
            
            # Execute
            result = generator.generate_response(query="What is programming?")
            
            # Verify
            assert result == "This is a general response about programming."
            assert mock_anthropic_client.call_count == 1
            
            # Verify API call parameters
            call_args = mock_anthropic_client.calls[0]
            assert call_args['model'] == "claude-3-haiku-20240307"
            assert call_args['temperature'] == 0
            assert call_args['max_tokens'] == 800
            assert 'tools' not in call_args  # No tools provided
            
    def test_generate_response_with_tools_no_tool_use(self, mock_anthropic_client, mock_tool_manager):
        """Test response generation with tools available but not used"""
        # Setup - Claude decides not to use tools
        mock_anthropic_client.set_response("General programming is about writing instructions for computers.")
        mock_anthropic_client.set_tool_use(False)
        
        with patch('anthropic.Anthropic', return_value=mock_anthropic_client):
            generator = AIGenerator(api_key="test_key", model="claude-3-haiku-20240307")
            
            # Execute
            result = generator.generate_response(
                query="What is programming in general?",
                tools=mock_tool_manager.get_tool_definitions(),
                tool_manager=mock_tool_manager
            )
            
            # Verify
            assert result == "General programming is about writing instructions for computers."
            assert mock_anthropic_client.call_count == 1
            assert len(mock_tool_manager.execute_calls) == 0  # No tools executed
            
            # Verify tools were provided to Claude
            call_args = mock_anthropic_client.calls[0]
            assert 'tools' in call_args
            assert call_args['tool_choice'] == {"type": "auto"}
            
    def test_generate_response_with_tool_use(self, mock_anthropic_client, mock_tool_manager):
        """Test response generation where Claude uses tools"""
        # Setup - Mock tool use flow
        mock_anthropic_client.set_tool_use(True)
        mock_tool_manager.set_tool_result("search_course_content", "Python is a programming language used for web development, data science, and automation.")
        
        # Mock the second API call after tool execution
        mock_final_response = Mock()
        mock_final_response.content = [Mock()]
        mock_final_response.content[0].text = "Based on the course materials, Python is a programming language used for web development, data science, and automation."
        
        with patch('anthropic.Anthropic') as mock_anthropic:
            # Setup mock client to handle both calls
            mock_client = Mock()
            mock_anthropic.return_value = mock_client
            
            # First call returns tool use
            tool_response = Mock()
            tool_response.stop_reason = "tool_use"
            tool_content = Mock()
            tool_content.type = "tool_use" 
            tool_content.name = "search_course_content"
            tool_content.id = "tool_1"
            tool_content.input = {"query": "What is Python?"}
            tool_response.content = [tool_content]
            
            # Second call returns final response
            mock_client.messages.create.side_effect = [tool_response, mock_final_response]
            
            generator = AIGenerator(api_key="test_key", model="claude-3-haiku-20240307")
            
            # Execute
            result = generator.generate_response(
                query="What is Python?",
                tools=mock_tool_manager.get_tool_definitions(),
                tool_manager=mock_tool_manager
            )
            
            # Verify final result
            assert "Based on the course materials, Python is a programming language" in result
            
            # Verify tool was executed
            assert len(mock_tool_manager.execute_calls) == 1
            assert_tool_called_with(mock_tool_manager, "search_course_content", query="What is Python?")
            
            # Verify two API calls were made (initial + follow-up)
            assert mock_client.messages.create.call_count == 2
    
    def test_generate_response_with_conversation_history(self, mock_anthropic_client, mock_tool_manager):
        """Test response generation with conversation history"""
        # Setup
        mock_anthropic_client.set_response("Based on our previous discussion about variables, let me explain functions.")
        history = "User: What are variables?\nAssistant: Variables store data values."
        
        with patch('anthropic.Anthropic', return_value=mock_anthropic_client):
            generator = AIGenerator(api_key="test_key", model="claude-3-haiku-20240307")
            
            # Execute
            result = generator.generate_response(
                query="What are functions?",
                conversation_history=history,
                tools=mock_tool_manager.get_tool_definitions(),
                tool_manager=mock_tool_manager
            )
            
            # Verify
            assert result == "Based on our previous discussion about variables, let me explain functions."
            
            # Verify history was included in system prompt
            call_args = mock_anthropic_client.calls[0]
            assert history in call_args['system']
            
    def test_generate_response_tool_execution_error(self, mock_anthropic_client, mock_tool_manager):
        """Test handling of tool execution errors"""
        # Setup - Mock tool use that results in error
        mock_tool_manager.set_tool_result("search_course_content", "No relevant content found.")
        
        with patch('anthropic.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_anthropic.return_value = mock_client
            
            # First call returns tool use
            tool_response = Mock()
            tool_response.stop_reason = "tool_use"
            tool_content = Mock()
            tool_content.type = "tool_use"
            tool_content.name = "search_course_content"
            tool_content.id = "tool_1"
            tool_content.input = {"query": "nonexistent topic"}
            tool_response.content = [tool_content]
            
            # Second call returns final response handling the error
            final_response = Mock()
            final_response.content = [Mock()]
            final_response.content[0].text = "I couldn't find any relevant course materials on that topic."
            
            mock_client.messages.create.side_effect = [tool_response, final_response]
            
            generator = AIGenerator(api_key="test_key", model="claude-3-haiku-20240307")
            
            # Execute
            result = generator.generate_response(
                query="Tell me about nonexistent topic",
                tools=mock_tool_manager.get_tool_definitions(),
                tool_manager=mock_tool_manager
            )
            
            # Verify error is handled gracefully
            assert "couldn't find any relevant course materials" in result
            
            # Verify tool was still executed (returned error message)
            assert len(mock_tool_manager.execute_calls) == 1
    
    def test_generate_response_multiple_tool_calls(self, mock_anthropic_client, mock_tool_manager):
        """Test handling of multiple tool calls in one response"""
        # Setup
        mock_tool_manager.set_tool_result("search_course_content", "Python basics from course materials")
        
        with patch('anthropic.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_anthropic.return_value = mock_client
            
            # First call returns multiple tool uses
            tool_response = Mock()
            tool_response.stop_reason = "tool_use"
            
            tool_content_1 = Mock()
            tool_content_1.type = "tool_use"
            tool_content_1.name = "search_course_content"
            tool_content_1.id = "tool_1"
            tool_content_1.input = {"query": "Python basics"}
            
            tool_content_2 = Mock()
            tool_content_2.type = "tool_use" 
            tool_content_2.name = "search_course_content"
            tool_content_2.id = "tool_2"
            tool_content_2.input = {"query": "Python advanced", "course_name": "Advanced Python"}
            
            tool_response.content = [tool_content_1, tool_content_2]
            
            # Second call returns final response
            final_response = Mock()
            final_response.content = [Mock()]
            final_response.content[0].text = "Here's information about Python from basic to advanced levels."
            
            mock_client.messages.create.side_effect = [tool_response, final_response]
            
            generator = AIGenerator(api_key="test_key", model="claude-3-haiku-20240307")
            
            # Execute
            result = generator.generate_response(
                query="Tell me about Python basics and advanced topics",
                tools=mock_tool_manager.get_tool_definitions(),
                tool_manager=mock_tool_manager
            )
            
            # Verify
            assert "Here's information about Python from basic to advanced levels." in result
            
            # Verify both tools were executed
            assert len(mock_tool_manager.execute_calls) == 2
            
            # Verify first tool call
            call_1 = mock_tool_manager.execute_calls[0]
            assert call_1['tool_name'] == "search_course_content"
            assert call_1['kwargs']['query'] == "Python basics"
            
            # Verify second tool call
            call_2 = mock_tool_manager.execute_calls[1]
            assert call_2['tool_name'] == "search_course_content"
            assert call_2['kwargs']['query'] == "Python advanced"
            assert call_2['kwargs']['course_name'] == "Advanced Python"
    
    def test_system_prompt_content(self, mock_anthropic_client):
        """Test that system prompt contains expected instructions"""
        # Setup
        mock_anthropic_client.set_response("Test response")
        
        with patch('anthropic.Anthropic', return_value=mock_anthropic_client):
            generator = AIGenerator(api_key="test_key", model="claude-3-haiku-20240307")
            
            # Execute
            generator.generate_response(query="Test query")
            
            # Verify system prompt content
            call_args = mock_anthropic_client.calls[0]
            system_content = call_args['system']
            
            # Check for key instructions
            assert "search_course_content" in system_content
            assert "get_course_outline" in system_content
            assert "One search per query maximum" in system_content
            assert "Brief, Concise and focused" in system_content
    
    def test_api_parameters_configuration(self, mock_anthropic_client):
        """Test that API parameters are correctly configured"""
        # Setup
        mock_anthropic_client.set_response("Test response")
        
        with patch('anthropic.Anthropic', return_value=mock_anthropic_client):
            generator = AIGenerator(api_key="test_key", model="claude-3-haiku-20240307")
            
            # Execute
            generator.generate_response(query="Test query")
            
            # Verify API parameters
            call_args = mock_anthropic_client.calls[0]
            assert call_args['model'] == "claude-3-haiku-20240307"
            assert call_args['temperature'] == 0
            assert call_args['max_tokens'] == 800
            assert len(call_args['messages']) == 1
            assert call_args['messages'][0]['role'] == "user"
            assert call_args['messages'][0]['content'] == "Test query"
    
    def test_tool_result_message_format(self, mock_anthropic_client, mock_tool_manager):
        """Test that tool results are properly formatted in messages"""
        # Setup
        mock_tool_manager.set_tool_result("search_course_content", "Course content result")
        
        with patch('anthropic.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_anthropic.return_value = mock_client
            
            # First call returns tool use
            tool_response = Mock()
            tool_response.stop_reason = "tool_use"
            tool_content = Mock()
            tool_content.type = "tool_use"
            tool_content.name = "search_course_content"
            tool_content.id = "tool_123"
            tool_content.input = {"query": "test"}
            tool_response.content = [tool_content]
            
            # Second call returns final response  
            final_response = Mock()
            final_response.content = [Mock()]
            final_response.content[0].text = "Final response"
            
            mock_client.messages.create.side_effect = [tool_response, final_response]
            
            generator = AIGenerator(api_key="test_key", model="claude-3-haiku-20240307")
            
            # Execute
            generator.generate_response(
                query="test query",
                tools=mock_tool_manager.get_tool_definitions(),
                tool_manager=mock_tool_manager
            )
            
            # Verify the second API call has properly formatted messages
            second_call_args = mock_client.messages.create.call_args_list[1][1]
            messages = second_call_args['messages']
            
            # Should have: original user message, assistant tool use, tool result
            assert len(messages) == 3
            
            # Check tool result message format
            tool_result_msg = messages[2]
            assert tool_result_msg['role'] == 'user'
            assert len(tool_result_msg['content']) == 1
            
            tool_result = tool_result_msg['content'][0]
            assert tool_result['type'] == 'tool_result'
            assert tool_result['tool_use_id'] == 'tool_123'
            assert tool_result['content'] == 'Course content result'