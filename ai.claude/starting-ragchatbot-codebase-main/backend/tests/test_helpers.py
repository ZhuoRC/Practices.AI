"""
Test helpers, mock objects, and fixtures for RAG system tests

This module provides comprehensive mock objects and test fixtures to enable
isolated testing of the RAG system components without external dependencies.

Key components:
- MockVectorStore: Simulates VectorStore behavior for CourseSearchTool testing
- MockAnthropicClient: Simulates Claude API responses for AIGenerator testing  
- MockToolManager: Simulates tool execution for integration testing
- Test fixtures for sample courses, lessons, and search results
"""

import pytest
from unittest.mock import Mock, MagicMock
from typing import List, Dict, Any, Optional
import sys
import os

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import Course, Lesson, CourseChunk
from vector_store import SearchResults


class MockVectorStore:
    """Mock VectorStore for testing"""
    
    def __init__(self):
        self.search_results = []
        self.search_call_count = 0
        self.search_calls = []
        self.should_raise_error = False
        self.error_message = "Mock search error"
        
    def search(self, query: str, course_name: Optional[str] = None, 
               lesson_number: Optional[int] = None, limit: Optional[int] = None) -> SearchResults:
        """Mock search method that returns pre-configured results"""
        self.search_call_count += 1
        self.search_calls.append({
            'query': query,
            'course_name': course_name,
            'lesson_number': lesson_number,
            'limit': limit
        })
        
        if self.should_raise_error:
            return SearchResults.empty(self.error_message)
        
        return self.search_results
    
    def set_search_results(self, results: SearchResults):
        """Configure the results to return from search"""
        self.search_results = results
    
    def set_error(self, error_message: str):
        """Configure the mock to return an error"""
        self.should_raise_error = True
        self.error_message = error_message
        
    def reset(self):
        """Reset the mock state"""
        self.search_call_count = 0
        self.search_calls = []
        self.should_raise_error = False
        self.search_results = SearchResults([], [], [])
        
    def get_lesson_link(self, course_title: str, lesson_num: int) -> Optional[str]:
        """Mock lesson link retrieval"""
        return f"https://example.com/{course_title.lower().replace(' ', '-')}/lesson-{lesson_num}"


class MockAnthropicClient:
    """Mock Anthropic client for testing AI responses"""
    
    def __init__(self):
        self.responses = []
        self.call_count = 0
        self.calls = []
        self.should_use_tools = False
        
        # Create messages mock
        self.messages = Mock()
        self.messages.create = self._create_message
        
    def _create_message(self, **kwargs):
        """Mock message creation"""
        self.call_count += 1
        self.calls.append(kwargs)
        
        # Create mock response object
        response = Mock()
        
        if self.should_use_tools and 'tools' in kwargs:
            # Mock tool use response
            response.stop_reason = "tool_use"
            
            # Create mock tool use content
            tool_content = Mock()
            tool_content.type = "tool_use"
            tool_content.name = "search_course_content"
            tool_content.id = "tool_call_1"
            tool_content.input = {"query": "test query"}
            
            response.content = [tool_content]
        else:
            # Mock direct text response
            response.stop_reason = "end_turn"
            text_content = Mock()
            text_content.text = self.responses[0] if self.responses else "Mock AI response"
            response.content = [text_content]
            
        return response
    
    def set_response(self, response_text: str):
        """Set the text response to return"""
        self.responses = [response_text]
        
    def set_tool_use(self, should_use_tools: bool):
        """Configure whether the mock should simulate tool use"""
        self.should_use_tools = should_use_tools


class MockToolManager:
    """Mock ToolManager for testing"""
    
    def __init__(self):
        self.execute_calls = []
        self.tool_results = {}
        self.last_sources = []
        
    def execute_tool(self, tool_name: str, **kwargs) -> str:
        """Mock tool execution"""
        call_info = {'tool_name': tool_name, 'kwargs': kwargs}
        self.execute_calls.append(call_info)
        
        return self.tool_results.get(tool_name, f"Mock result for {tool_name}")
    
    def get_tool_definitions(self) -> List[Dict]:
        """Mock tool definitions"""
        return [{
            "name": "search_course_content",
            "description": "Search course materials",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What to search for"},
                    "course_name": {"type": "string", "description": "Course name filter"},
                    "lesson_number": {"type": "integer", "description": "Lesson number filter"}
                },
                "required": ["query"]
            }
        }]
    
    def get_last_sources(self) -> List[Dict]:
        """Mock source retrieval"""
        return self.last_sources
    
    def reset_sources(self):
        """Mock source reset"""
        self.last_sources = []
    
    def set_tool_result(self, tool_name: str, result: str):
        """Configure result for specific tool"""
        self.tool_results[tool_name] = result
        
    def set_last_sources(self, sources: List[Dict]):
        """Configure sources to return"""
        self.last_sources = sources


# Test Fixtures
@pytest.fixture
def sample_course():
    """Sample course with lessons"""
    return Course(
        title="Introduction to Python",
        instructor="Dr. Smith",
        course_link="https://example.com/python-course",
        lessons=[
            Lesson(lesson_number=1, title="Getting Started", lesson_link="https://example.com/python/lesson1"),
            Lesson(lesson_number=2, title="Variables and Types", lesson_link="https://example.com/python/lesson2"),
            Lesson(lesson_number=3, title="Control Flow", lesson_link="https://example.com/python/lesson3")
        ]
    )

@pytest.fixture
def sample_chunks(sample_course):
    """Sample course chunks for testing"""
    return [
        CourseChunk(
            content="Python is a high-level programming language",
            course_title=sample_course.title,
            lesson_number=1,
            chunk_index=0
        ),
        CourseChunk(
            content="Variables in Python are created by assignment",
            course_title=sample_course.title,
            lesson_number=2,
            chunk_index=1
        ),
        CourseChunk(
            content="Control flow in Python includes if statements and loops",
            course_title=sample_course.title,
            lesson_number=3,
            chunk_index=2
        )
    ]

@pytest.fixture
def sample_search_results(sample_chunks):
    """Sample search results with metadata"""
    documents = [chunk.content for chunk in sample_chunks]
    metadata = [
        {
            'course_title': chunk.course_title,
            'lesson_number': chunk.lesson_number,
            'chunk_index': chunk.chunk_index
        }
        for chunk in sample_chunks
    ]
    distances = [0.1, 0.2, 0.3]
    
    return SearchResults(documents=documents, metadata=metadata, distances=distances)

@pytest.fixture
def empty_search_results():
    """Empty search results for testing no-results scenarios"""
    return SearchResults(documents=[], metadata=[], distances=[])

@pytest.fixture
def error_search_results():
    """Error search results for testing error scenarios"""
    return SearchResults.empty("Test error message")

@pytest.fixture
def mock_vector_store():
    """Pre-configured mock vector store"""
    return MockVectorStore()

@pytest.fixture
def mock_anthropic_client():
    """Pre-configured mock Anthropic client"""
    return MockAnthropicClient()

@pytest.fixture
def mock_tool_manager():
    """Pre-configured mock tool manager"""
    return MockToolManager()


# Assertion Helpers
def assert_search_called_with(mock_store: MockVectorStore, query: str, 
                            course_name: Optional[str] = None, 
                            lesson_number: Optional[int] = None):
    """Assert that search was called with specific parameters"""
    assert mock_store.search_call_count > 0, "Search was not called"
    last_call = mock_store.search_calls[-1]
    assert last_call['query'] == query, f"Expected query '{query}', got '{last_call['query']}'"
    assert last_call['course_name'] == course_name, f"Expected course_name '{course_name}', got '{last_call['course_name']}'"
    assert last_call['lesson_number'] == lesson_number, f"Expected lesson_number '{lesson_number}', got '{last_call['lesson_number']}'"

def assert_tool_called_with(mock_manager: MockToolManager, tool_name: str, **expected_kwargs):
    """Assert that a tool was called with specific parameters"""
    assert len(mock_manager.execute_calls) > 0, "No tools were called"
    
    # Find calls to the specific tool
    tool_calls = [call for call in mock_manager.execute_calls if call['tool_name'] == tool_name]
    assert len(tool_calls) > 0, f"Tool '{tool_name}' was not called"
    
    last_call = tool_calls[-1]
    for key, expected_value in expected_kwargs.items():
        actual_value = last_call['kwargs'].get(key)
        assert actual_value == expected_value, f"Expected {key}='{expected_value}', got '{actual_value}'"

def assert_sources_tracked(sources: List[Dict], expected_count: int):
    """Assert that the correct number of sources were tracked"""
    assert len(sources) == expected_count, f"Expected {expected_count} sources, got {len(sources)}"
    
    for source in sources:
        assert 'display' in source, "Source missing 'display' field"
        assert isinstance(source['display'], str), "Source 'display' should be a string"