"""
End-to-end integration tests for RAG system

This test suite validates the complete RAG system pipeline from user query to response,
including component integration, session management, and error propagation.

These integration tests use mocked components to ensure reliable testing while validating
the interactions between RAGSystem, AIGenerator, CourseSearchTool, and SessionManager.

Test coverage:
- Content-specific queries triggering search tools
- General questions bypassing search (efficiency)
- Session management and conversation history integration
- Error handling and graceful degradation
- Source tracking through the complete pipeline  
- Multi-course result formatting and presentation
- System analytics and course catalog management
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass

# Add parent directory to path to import backend modules  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from rag_system import RAGSystem
from vector_store import SearchResults
from test_helpers import (
    MockVectorStore,
    MockAnthropicClient, 
    MockToolManager,
    sample_course,
    sample_chunks,
    sample_search_results,
    empty_search_results,
    mock_vector_store
)


@dataclass 
class MockConfig:
    """Mock configuration for testing"""
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 100
    CHROMA_PATH: str = "./test_chroma_db"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    MAX_RESULTS: int = 5
    ANTHROPIC_API_KEY: str = "test_api_key"
    ANTHROPIC_MODEL: str = "claude-3-haiku-20240307"
    MAX_HISTORY: int = 2


class TestRAGSystemIntegration:
    """Integration tests for the full RAG system pipeline"""

    def test_query_content_specific_triggers_search(self, sample_search_results):
        """Test that content-specific queries trigger search tools"""
        # Setup mocks
        mock_vector_store = MockVectorStore()
        mock_vector_store.set_search_results(sample_search_results)
        
        config = MockConfig()
        
        # Mock all components
        with patch('rag_system.DocumentProcessor'), \
             patch('rag_system.VectorStore', return_value=mock_vector_store), \
             patch('rag_system.SessionManager') as mock_session, \
             patch('anthropic.Anthropic') as mock_anthropic:
            
            # Setup anthropic mock to simulate tool use
            mock_client = Mock()
            mock_anthropic.return_value = mock_client
            
            # First call: Claude requests tool use
            tool_response = Mock()
            tool_response.stop_reason = "tool_use"
            tool_content = Mock()
            tool_content.type = "tool_use"
            tool_content.name = "search_course_content"
            tool_content.id = "tool_1"
            tool_content.input = {"query": "What is Python?"}
            tool_response.content = [tool_content]
            
            # Second call: Claude responds with search results
            final_response = Mock()
            final_response.content = [Mock()]
            final_response.content[0].text = "Python is a high-level programming language used for web development and data science."
            
            mock_client.messages.create.side_effect = [tool_response, final_response]
            
            # Initialize RAG system
            rag_system = RAGSystem(config)
            
            # Execute query
            response, sources = rag_system.query("What is Python?")
            
            # Verify search was triggered
            assert mock_vector_store.search_call_count == 1
            assert mock_vector_store.search_calls[0]['query'] == "What is Python?"
            
            # Verify response contains expected content
            assert "Python is a high-level programming language" in response
            
            # Verify sources were tracked
            assert len(sources) == 3  # From sample_search_results fixture
            assert sources[0]['display'] == "Introduction to Python - Lesson 1"

    def test_query_general_question_no_search(self):
        """Test that general questions don't trigger unnecessary search"""
        # Setup mocks
        mock_vector_store = MockVectorStore()
        config = MockConfig()
        
        with patch('rag_system.DocumentProcessor'), \
             patch('rag_system.VectorStore', return_value=mock_vector_store), \
             patch('rag_system.SessionManager'), \
             patch('anthropic.Anthropic') as mock_anthropic:
            
            # Setup anthropic mock to NOT use tools
            mock_client = Mock()
            mock_anthropic.return_value = mock_client
            
            # Single call: Claude responds directly without tools
            direct_response = Mock()
            direct_response.stop_reason = "end_turn"
            direct_response.content = [Mock()]
            direct_response.content[0].text = "Hello! I'm here to help you with course materials."
            
            mock_client.messages.create.return_value = direct_response
            
            # Initialize RAG system
            rag_system = RAGSystem(config)
            
            # Execute general query
            response, sources = rag_system.query("Hello, how are you?")
            
            # Verify no search was triggered
            assert mock_vector_store.search_call_count == 0
            
            # Verify response is general
            assert "Hello! I'm here to help you with course materials." in response
            
            # Verify no sources
            assert len(sources) == 0

    def test_query_with_session_management(self, sample_search_results):
        """Test query processing with conversation history"""
        # Setup mocks
        mock_vector_store = MockVectorStore()
        mock_vector_store.set_search_results(sample_search_results)
        
        config = MockConfig()
        
        with patch('rag_system.DocumentProcessor'), \
             patch('rag_system.VectorStore', return_value=mock_vector_store), \
             patch('rag_system.SessionManager') as MockSessionManager, \
             patch('anthropic.Anthropic') as mock_anthropic:
            
            # Setup session manager mock
            mock_session_instance = Mock()
            MockSessionManager.return_value = mock_session_instance
            mock_session_instance.get_conversation_history.return_value = "User: What are variables?\nAssistant: Variables store data."
            
            # Setup anthropic mock
            mock_client = Mock()
            mock_anthropic.return_value = mock_client
            
            # Mock tool use response
            tool_response = Mock()
            tool_response.stop_reason = "tool_use"
            tool_content = Mock()
            tool_content.type = "tool_use"
            tool_content.name = "search_course_content"
            tool_content.id = "tool_1"
            tool_content.input = {"query": "functions in Python"}
            tool_response.content = [tool_content]
            
            final_response = Mock()
            final_response.content = [Mock()]
            final_response.content[0].text = "Based on our discussion about variables, functions in Python are reusable blocks of code."
            
            mock_client.messages.create.side_effect = [tool_response, final_response]
            
            # Initialize RAG system
            rag_system = RAGSystem(config)
            
            # Execute query with session
            response, sources = rag_system.query("What about functions?", session_id="test_session")
            
            # Verify session history was retrieved
            mock_session_instance.get_conversation_history.assert_called_with("test_session")
            
            # Verify conversation was updated
            mock_session_instance.add_exchange.assert_called_once()
            add_call_args = mock_session_instance.add_exchange.call_args[0]
            assert add_call_args[0] == "test_session"
            assert "What about functions?" in add_call_args[1]
            assert "functions in Python are reusable blocks" in add_call_args[2]
            
            # Verify search was still triggered
            assert mock_vector_store.search_call_count == 1

    def test_query_search_error_handling(self):
        """Test handling of search errors in the pipeline"""
        # Setup mocks
        mock_vector_store = MockVectorStore()
        mock_vector_store.set_error("Database connection failed")
        
        config = MockConfig()
        
        with patch('rag_system.DocumentProcessor'), \
             patch('rag_system.VectorStore', return_value=mock_vector_store), \
             patch('rag_system.SessionManager'), \
             patch('anthropic.Anthropic') as mock_anthropic:
            
            # Setup anthropic mock to use tools
            mock_client = Mock()
            mock_anthropic.return_value = mock_client
            
            tool_response = Mock()
            tool_response.stop_reason = "tool_use"
            tool_content = Mock()
            tool_content.type = "tool_use"
            tool_content.name = "search_course_content"
            tool_content.id = "tool_1"
            tool_content.input = {"query": "Python basics"}
            tool_response.content = [tool_content]
            
            # Claude handles the error gracefully
            final_response = Mock()
            final_response.content = [Mock()]
            final_response.content[0].text = "I'm sorry, I'm having trouble accessing the course materials right now."
            
            mock_client.messages.create.side_effect = [tool_response, final_response]
            
            # Initialize RAG system
            rag_system = RAGSystem(config)
            
            # Execute query
            response, sources = rag_system.query("Tell me about Python basics")
            
            # Verify error was handled gracefully
            assert "trouble accessing the course materials" in response
            
            # Verify search was attempted
            assert mock_vector_store.search_call_count == 1
            
            # Verify no sources due to error
            assert len(sources) == 0

    def test_query_empty_search_results(self, empty_search_results):
        """Test handling when search returns no results"""
        # Setup mocks
        mock_vector_store = MockVectorStore()
        mock_vector_store.set_search_results(empty_search_results)
        
        config = MockConfig()
        
        with patch('rag_system.DocumentProcessor'), \
             patch('rag_system.VectorStore', return_value=mock_vector_store), \
             patch('rag_system.SessionManager'), \
             patch('anthropic.Anthropic') as mock_anthropic:
            
            # Setup anthropic mock
            mock_client = Mock()
            mock_anthropic.return_value = mock_client
            
            tool_response = Mock()
            tool_response.stop_reason = "tool_use"
            tool_content = Mock()
            tool_content.type = "tool_use"
            tool_content.name = "search_course_content"
            tool_content.id = "tool_1"
            tool_content.input = {"query": "nonexistent topic"}
            tool_response.content = [tool_content]
            
            final_response = Mock()
            final_response.content = [Mock()]
            final_response.content[0].text = "I couldn't find any course materials on that topic."
            
            mock_client.messages.create.side_effect = [tool_response, final_response]
            
            # Initialize RAG system
            rag_system = RAGSystem(config)
            
            # Execute query
            response, sources = rag_system.query("Tell me about nonexistent topic")
            
            # Verify empty results were handled
            assert "couldn't find any course materials" in response
            
            # Verify no sources
            assert len(sources) == 0

    def test_query_source_tracking_and_reset(self, sample_search_results):
        """Test that sources are properly tracked and reset between queries"""
        # Setup mocks
        mock_vector_store = MockVectorStore()
        mock_vector_store.set_search_results(sample_search_results)
        
        config = MockConfig()
        
        with patch('rag_system.DocumentProcessor'), \
             patch('rag_system.VectorStore', return_value=mock_vector_store), \
             patch('rag_system.SessionManager'), \
             patch('anthropic.Anthropic') as mock_anthropic:
            
            # Setup anthropic mock
            mock_client = Mock()
            mock_anthropic.return_value = mock_client
            
            def create_tool_response_pair(query):
                tool_response = Mock()
                tool_response.stop_reason = "tool_use"
                tool_content = Mock()
                tool_content.type = "tool_use"
                tool_content.name = "search_course_content"
                tool_content.id = "tool_1"
                tool_content.input = {"query": query}
                tool_response.content = [tool_content]
                
                final_response = Mock()
                final_response.content = [Mock()]
                final_response.content[0].text = f"Information about {query}"
                
                return tool_response, final_response
            
            # Initialize RAG system
            rag_system = RAGSystem(config)
            
            # First query
            tool_resp_1, final_resp_1 = create_tool_response_pair("Python")
            mock_client.messages.create.side_effect = [tool_resp_1, final_resp_1]
            
            response_1, sources_1 = rag_system.query("What is Python?")
            
            # Verify sources from first query
            assert len(sources_1) == 3
            
            # Second query - sources should be reset
            tool_resp_2, final_resp_2 = create_tool_response_pair("JavaScript")
            mock_client.messages.create.side_effect = [tool_resp_2, final_resp_2]
            
            response_2, sources_2 = rag_system.query("What is JavaScript?")
            
            # Verify sources from second query (should not contain first query sources)
            assert len(sources_2) == 3
            
            # Verify both queries triggered search
            assert mock_vector_store.search_call_count == 2

    def test_multiple_course_results_formatting(self):
        """Test formatting when search returns results from multiple courses"""
        # Setup multi-course results
        multi_course_results = SearchResults(
            documents=[
                "Python is great for beginners",
                "JavaScript runs in browsers", 
                "Java is object-oriented"
            ],
            metadata=[
                {'course_title': 'Python Basics', 'lesson_number': 1, 'chunk_index': 0},
                {'course_title': 'Web Development', 'lesson_number': 2, 'chunk_index': 1},
                {'course_title': 'Java Programming', 'lesson_number': 1, 'chunk_index': 2}
            ],
            distances=[0.1, 0.2, 0.3]
        )
        
        mock_vector_store = MockVectorStore()
        mock_vector_store.set_search_results(multi_course_results)
        
        config = MockConfig()
        
        with patch('rag_system.DocumentProcessor'), \
             patch('rag_system.VectorStore', return_value=mock_vector_store), \
             patch('rag_system.SessionManager'), \
             patch('anthropic.Anthropic') as mock_anthropic:
            
            # Setup anthropic mock
            mock_client = Mock()
            mock_anthropic.return_value = mock_client
            
            tool_response = Mock()
            tool_response.stop_reason = "tool_use"
            tool_content = Mock()
            tool_content.type = "tool_use"
            tool_content.name = "search_course_content"
            tool_content.id = "tool_1"
            tool_content.input = {"query": "programming languages"}
            tool_response.content = [tool_content]
            
            final_response = Mock()
            final_response.content = [Mock()]
            final_response.content[0].text = "Here's information about various programming languages from different courses."
            
            mock_client.messages.create.side_effect = [tool_response, final_response]
            
            # Initialize RAG system
            rag_system = RAGSystem(config)
            
            # Execute query
            response, sources = rag_system.query("Tell me about programming languages")
            
            # Verify sources from multiple courses
            assert len(sources) == 3
            
            course_names = [source['display'] for source in sources]
            assert "Python Basics - Lesson 1" in course_names
            assert "Web Development - Lesson 2" in course_names
            assert "Java Programming - Lesson 1" in course_names

    def test_course_analytics_functionality(self):
        """Test the get_course_analytics method"""
        # Setup mocks
        mock_vector_store = MockVectorStore()
        
        # Mock the analytics methods
        mock_vector_store.get_course_count = Mock(return_value=3)
        mock_vector_store.get_existing_course_titles = Mock(return_value=["Python Basics", "Web Development", "Data Science"])
        
        config = MockConfig()
        
        with patch('rag_system.DocumentProcessor'), \
             patch('rag_system.VectorStore', return_value=mock_vector_store), \
             patch('rag_system.SessionManager'), \
             patch('rag_system.AIGenerator'):
            
            # Initialize RAG system
            rag_system = RAGSystem(config)
            
            # Get analytics
            analytics = rag_system.get_course_analytics()
            
            # Verify analytics structure
            assert 'total_courses' in analytics
            assert 'course_titles' in analytics
            assert analytics['total_courses'] == 3
            assert len(analytics['course_titles']) == 3
            assert "Python Basics" in analytics['course_titles']