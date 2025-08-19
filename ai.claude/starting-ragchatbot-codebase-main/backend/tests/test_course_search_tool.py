"""
Tests for CourseSearchTool.execute method

This test suite validates the CourseSearchTool's query execution functionality,
including parameter handling, result formatting, source tracking, and error handling.

The tests use MockVectorStore to isolate the tool logic from the actual vector database,
ensuring reliable and fast test execution.

Test coverage:
- Query execution with various filter combinations (course_name, lesson_number)
- Empty result handling with appropriate error messages
- Vector store error propagation  
- Result formatting with course/lesson headers
- Source tracking for UI integration
- Tool definition validation for Claude API integration
"""

import pytest
import sys
import os
from unittest.mock import patch, Mock

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from search_tools import CourseSearchTool
from vector_store import SearchResults
from test_helpers import (
    MockVectorStore, 
    sample_course, 
    sample_chunks, 
    sample_search_results,
    empty_search_results,
    error_search_results,
    mock_vector_store,
    assert_search_called_with,
    assert_sources_tracked
)


class TestCourseSearchToolExecute:
    """Test suite for CourseSearchTool.execute method"""
    
    def test_execute_query_only_success(self, mock_vector_store, sample_search_results):
        """Test execute with query only - successful results"""
        # Setup
        mock_vector_store.set_search_results(sample_search_results)
        tool = CourseSearchTool(mock_vector_store)
        
        # Execute
        result = tool.execute(query="What is Python?")
        
        # Verify search was called correctly
        assert_search_called_with(mock_vector_store, "What is Python?", course_name=None, lesson_number=None)
        
        # Verify result formatting
        assert isinstance(result, str)
        assert "Introduction to Python" in result
        assert "Python is a high-level programming language" in result
        assert "Variables in Python are created by assignment" in result
        assert "Control flow in Python includes if statements and loops" in result
        
        # Verify lesson headers are included
        assert "[Introduction to Python - Lesson 1]" in result
        assert "[Introduction to Python - Lesson 2]" in result  
        assert "[Introduction to Python - Lesson 3]" in result
        
        # Verify sources are tracked
        assert len(tool.last_sources) == 3
        assert tool.last_sources[0]['display'] == "Introduction to Python - Lesson 1"
        assert tool.last_sources[0]['lesson_number'] == 1
        assert tool.last_sources[0]['link'] is not None

    def test_execute_with_course_name_filter(self, mock_vector_store, sample_search_results):
        """Test execute with course name filter"""
        # Setup
        mock_vector_store.set_search_results(sample_search_results)
        tool = CourseSearchTool(mock_vector_store)
        
        # Execute
        result = tool.execute(query="variables", course_name="Introduction to Python")
        
        # Verify search was called with course filter
        assert_search_called_with(mock_vector_store, "variables", course_name="Introduction to Python", lesson_number=None)
        
        # Verify results contain content
        assert "Variables in Python are created by assignment" in result
        
    def test_execute_with_lesson_number_filter(self, mock_vector_store, sample_search_results):
        """Test execute with lesson number filter"""
        # Setup  
        mock_vector_store.set_search_results(sample_search_results)
        tool = CourseSearchTool(mock_vector_store)
        
        # Execute
        result = tool.execute(query="control flow", lesson_number=3)
        
        # Verify search was called with lesson filter
        assert_search_called_with(mock_vector_store, "control flow", course_name=None, lesson_number=3)
        
        # Verify results contain content
        assert "Control flow in Python includes if statements and loops" in result

    def test_execute_with_both_filters(self, mock_vector_store, sample_search_results):
        """Test execute with both course name and lesson number filters"""
        # Setup
        mock_vector_store.set_search_results(sample_search_results)
        tool = CourseSearchTool(mock_vector_store)
        
        # Execute
        result = tool.execute(query="variables", course_name="Introduction to Python", lesson_number=2)
        
        # Verify search was called with both filters
        assert_search_called_with(mock_vector_store, "variables", course_name="Introduction to Python", lesson_number=2)
        
        # Verify results contain content
        assert "Variables in Python are created by assignment" in result

    def test_execute_empty_results_no_filters(self, mock_vector_store, empty_search_results):
        """Test execute with no results and no filters"""
        # Setup
        mock_vector_store.set_search_results(empty_search_results)
        tool = CourseSearchTool(mock_vector_store)
        
        # Execute
        result = tool.execute(query="nonexistent topic")
        
        # Verify appropriate error message
        assert result == "No relevant content found."
        
        # Verify no sources are tracked
        assert len(tool.last_sources) == 0

    def test_execute_empty_results_with_course_filter(self, mock_vector_store, empty_search_results):
        """Test execute with no results and course filter"""
        # Setup
        mock_vector_store.set_search_results(empty_search_results)
        tool = CourseSearchTool(mock_vector_store)
        
        # Execute
        result = tool.execute(query="nonexistent topic", course_name="Nonexistent Course")
        
        # Verify appropriate error message with filter info
        assert result == "No relevant content found in course 'Nonexistent Course'."

    def test_execute_empty_results_with_lesson_filter(self, mock_vector_store, empty_search_results):
        """Test execute with no results and lesson filter"""
        # Setup
        mock_vector_store.set_search_results(empty_search_results)
        tool = CourseSearchTool(mock_vector_store)
        
        # Execute
        result = tool.execute(query="nonexistent topic", lesson_number=5)
        
        # Verify appropriate error message with filter info
        assert result == "No relevant content found in lesson 5."

    def test_execute_empty_results_with_both_filters(self, mock_vector_store, empty_search_results):
        """Test execute with no results and both filters"""
        # Setup
        mock_vector_store.set_search_results(empty_search_results)
        tool = CourseSearchTool(mock_vector_store)
        
        # Execute
        result = tool.execute(query="nonexistent topic", course_name="Nonexistent Course", lesson_number=5)
        
        # Verify appropriate error message with both filter info
        assert result == "No relevant content found in course 'Nonexistent Course' in lesson 5."

    def test_execute_vector_store_error(self, mock_vector_store):
        """Test execute when VectorStore returns error"""
        # Setup
        mock_vector_store.set_error("Database connection failed")
        tool = CourseSearchTool(mock_vector_store)
        
        # Execute
        result = tool.execute(query="test query")
        
        # Verify error is returned
        assert result == "Database connection failed"
        
        # Verify no sources are tracked
        assert len(tool.last_sources) == 0

    def test_execute_malformed_metadata(self, mock_vector_store):
        """Test execute with malformed metadata in search results"""
        # Setup - create results with missing metadata fields
        malformed_results = SearchResults(
            documents=["Test content"],
            metadata=[{}],  # Missing required fields
            distances=[0.1]
        )
        mock_vector_store.set_search_results(malformed_results)
        tool = CourseSearchTool(mock_vector_store)
        
        # Execute
        result = tool.execute(query="test query")
        
        # Verify it handles missing metadata gracefully
        assert isinstance(result, str)
        assert "Test content" in result
        assert "[unknown]" in result  # Should default to 'unknown' for missing course_title

    def test_execute_source_tracking_with_links(self, mock_vector_store):
        """Test that sources are properly tracked with lesson links"""
        # Setup - create results with lesson links
        results = SearchResults(
            documents=["Content from lesson 1"],
            metadata=[{
                'course_title': 'Test Course',
                'lesson_number': 1,
                'chunk_index': 0
            }],
            distances=[0.1]
        )
        mock_vector_store.set_search_results(results)
        tool = CourseSearchTool(mock_vector_store)
        
        # Execute
        result = tool.execute(query="test query")
        
        # Verify source tracking
        assert len(tool.last_sources) == 1
        source = tool.last_sources[0]
        assert source['display'] == 'Test Course - Lesson 1'
        assert source['lesson_number'] == 1
        assert 'link' in source
        
        # Verify the mock lesson link is generated correctly
        expected_link = mock_vector_store.get_lesson_link('Test Course', 1)
        assert source['link'] == expected_link

    def test_execute_source_tracking_without_lesson_number(self, mock_vector_store):
        """Test source tracking when lesson_number is None"""
        # Setup - create results without lesson number
        results = SearchResults(
            documents=["General course content"],
            metadata=[{
                'course_title': 'Test Course',
                'lesson_number': None,
                'chunk_index': 0
            }],
            distances=[0.1]
        )
        mock_vector_store.set_search_results(results)
        tool = CourseSearchTool(mock_vector_store)
        
        # Execute
        result = tool.execute(query="test query")
        
        # Verify source tracking
        assert len(tool.last_sources) == 1
        source = tool.last_sources[0]
        assert source['display'] == 'Test Course'  # No lesson number appended
        assert source['lesson_number'] is None
        assert source['link'] is None  # No lesson link when lesson_number is None

    def test_execute_multiple_results_formatting(self, mock_vector_store):
        """Test formatting of multiple search results"""
        # Setup - create multiple results with different lessons
        results = SearchResults(
            documents=[
                "First result content",
                "Second result content", 
                "Third result content"
            ],
            metadata=[
                {'course_title': 'Course A', 'lesson_number': 1, 'chunk_index': 0},
                {'course_title': 'Course B', 'lesson_number': 2, 'chunk_index': 1},
                {'course_title': 'Course A', 'lesson_number': 3, 'chunk_index': 2}
            ],
            distances=[0.1, 0.2, 0.3]
        )
        mock_vector_store.set_search_results(results)
        tool = CourseSearchTool(mock_vector_store)
        
        # Execute
        result = tool.execute(query="test query")
        
        # Verify all results are included and properly separated
        assert "First result content" in result
        assert "Second result content" in result
        assert "Third result content" in result
        
        # Verify proper course/lesson headers
        assert "[Course A - Lesson 1]" in result
        assert "[Course B - Lesson 2]" in result
        assert "[Course A - Lesson 3]" in result
        
        # Verify results are separated by double newlines
        parts = result.split("\n\n")
        assert len(parts) == 3
        
        # Verify all sources are tracked
        assert len(tool.last_sources) == 3

    def test_get_tool_definition(self, mock_vector_store):
        """Test that tool definition is properly structured"""
        # Setup
        tool = CourseSearchTool(mock_vector_store)
        
        # Execute
        tool_def = tool.get_tool_definition()
        
        # Verify tool definition structure
        assert tool_def['name'] == 'search_course_content'
        assert 'description' in tool_def
        assert 'input_schema' in tool_def
        
        # Verify input schema
        schema = tool_def['input_schema']
        assert schema['type'] == 'object'
        assert 'properties' in schema
        assert 'required' in schema
        
        # Verify required parameters
        assert 'query' in schema['required']
        
        # Verify optional parameters are defined
        properties = schema['properties']
        assert 'query' in properties
        assert 'course_name' in properties
        assert 'lesson_number' in properties
        
        # Verify parameter types
        assert properties['query']['type'] == 'string'
        assert properties['course_name']['type'] == 'string'
        assert properties['lesson_number']['type'] == 'integer'