"""
Real-world integration tests that caught actual bugs

This test suite contains integration tests that use real components (not mocks)
to identify issues that only surface when components interact with actual dependencies.

CRITICAL BUG DISCOVERED: ChromaDB None Values Error
- Location: vector_store.py add_course_metadata() method
- Issue: ChromaDB requires all metadata values to be non-None, but Course model allows None
- Impact: System crashes when adding courses with missing instructor/course_link data
- Fix: Convert None values to empty strings before passing to ChromaDB

These tests serve as regression tests to ensure the identified bugs are properly fixed.
"""

import pytest
import sys
import os
from unittest.mock import patch
import shutil

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from vector_store import VectorStore
from models import Course, Lesson, CourseChunk


class TestRealWorldBugs:
    """Test cases that expose real issues in the system"""
    
    def test_course_metadata_with_none_values_bug(self):
        """
        Test that demonstrates the critical ChromaDB None values bug.
        This test should FAIL with the current implementation.
        """
        test_path = './test_bug_chroma_db'
        
        # Clean up any existing test database
        if os.path.exists(test_path):
            try:
                shutil.rmtree(test_path)
            except:
                pass
        
        try:
            vs = VectorStore(test_path, 'all-MiniLM-L6-v2', 5)
            
            # Create course with None values (which is valid per the model)
            course = Course(
                title='Test Course',
                instructor=None,  # This is the problem - None value
                course_link=None,  # This is also a problem - None value
                lessons=[
                    Lesson(lesson_number=1, title='Test Lesson', lesson_link=None)
                ]
            )
            
            # This should fail with current implementation
            with pytest.raises(TypeError, match="'NoneType' object cannot be converted"):
                vs.add_course_metadata(course)
                
        finally:
            # Clean up
            if os.path.exists(test_path):
                try:
                    shutil.rmtree(test_path)
                except:
                    pass
    
    def test_search_quality_with_irrelevant_queries(self):
        """
        Test search behavior with completely irrelevant queries.
        This might reveal issues with search result quality.
        """
        test_path = './test_search_quality_db'
        
        if os.path.exists(test_path):
            try:
                shutil.rmtree(test_path)
            except:
                pass
        
        try:
            vs = VectorStore(test_path, 'all-MiniLM-L6-v2', 5)
            
            # Add course with specific content
            course = Course(
                title='Python Programming',
                instructor='Dr. Smith',
                course_link='https://example.com/python',
                lessons=[Lesson(lesson_number=1, title='Basics')]
            )
            
            chunks = [
                CourseChunk(
                    content='Python is a programming language used for web development',
                    course_title='Python Programming',
                    lesson_number=1,
                    chunk_index=0
                )
            ]
            
            vs.add_course_metadata(course)
            vs.add_course_content(chunks)
            
            # Test with completely irrelevant query
            irrelevant_result = vs.search('quantum physics nuclear fusion molecular biology')
            
            # With small datasets, even irrelevant queries might return results
            # This is expected behavior with vector similarity search
            # But we should verify the system handles it gracefully
            assert not irrelevant_result.error
            
            # The result might not be empty due to small dataset size
            # But it should still be properly formatted
            if not irrelevant_result.is_empty():
                assert len(irrelevant_result.documents) > 0
                assert len(irrelevant_result.metadata) == len(irrelevant_result.documents)
                
        finally:
            if os.path.exists(test_path):
                try:
                    shutil.rmtree(test_path)
                except:
                    pass
    
    def test_course_search_tool_with_real_vectorstore(self):
        """Test CourseSearchTool with real VectorStore to catch integration issues"""
        test_path = './test_integration_db'
        
        if os.path.exists(test_path):
            try:
                shutil.rmtree(test_path)
            except:
                pass
        
        try:
            vs = VectorStore(test_path, 'all-MiniLM-L6-v2', 5)
            
            # Add test data with valid non-None values
            course = Course(
                title='JavaScript Fundamentals',
                instructor='Jane Doe',
                course_link='https://example.com/js',
                lessons=[
                    Lesson(lesson_number=1, title='Variables', lesson_link='https://example.com/js/1'),
                    Lesson(lesson_number=2, title='Functions', lesson_link='https://example.com/js/2')
                ]
            )
            
            chunks = [
                CourseChunk(
                    content='JavaScript variables are declared with let, const, or var',
                    course_title='JavaScript Fundamentals',
                    lesson_number=1,
                    chunk_index=0
                ),
                CourseChunk(
                    content='JavaScript functions are reusable blocks of code',
                    course_title='JavaScript Fundamentals', 
                    lesson_number=2,
                    chunk_index=1
                )
            ]
            
            vs.add_course_metadata(course)
            vs.add_course_content(chunks)
            
            # Test CourseSearchTool with real data
            from search_tools import CourseSearchTool
            tool = CourseSearchTool(vs)
            
            # Test successful search
            result = tool.execute('JavaScript variables')
            assert 'JavaScript variables are declared' in result
            assert '[JavaScript Fundamentals - Lesson 1]' in result
            
            # Verify sources are tracked
            assert len(tool.last_sources) > 0
            assert tool.last_sources[0]['display'] == 'JavaScript Fundamentals - Lesson 1'
            assert tool.last_sources[0]['lesson_number'] == 1
            assert 'link' in tool.last_sources[0]
            
        finally:
            if os.path.exists(test_path):
                try:
                    shutil.rmtree(test_path)
                except:
                    pass