import unittest
from unittest.mock import Mock, patch
import tempfile
import os
import json
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import rag_system as rag_system_module
    from rag_system import RAGSystem, create_test_questions, evaluate_retrieval
except ImportError:
    rag_system_module = None
    RAGSystem = None

class TestRAGSystem(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        if rag_system_module is None:
            self.skipTest("RAG system not available - missing dependencies")
    
    def test_simple_vector_store(self):
        """Test simple vector store functionality"""
        if hasattr(rag_system_module, 'SimpleVectorStore'):
            store = rag_system_module.SimpleVectorStore()
            
            # Test adding documents
            store.add(['test doc 1', 'test doc 2'], [{'id': 1}, {'id': 2}], ['doc1', 'doc2'])
            
            # Test querying
            results = store.query(['test'], n_results=1)
            
            self.assertIn('documents', results)
            self.assertIn('metadatas', results)
            self.assertEqual(len(results['documents'][0]), 1)
    
    def test_rag_system_initialization(self):
        """Test RAG system can be initialized"""
        with patch('rag_system.OpenAI'):
            rag = RAGSystem()
            self.assertIsNotNone(rag)
            self.assertIsNotNone(rag.collection)
    
    def test_create_test_questions(self):
        """Test test question creation"""
        questions = create_test_questions()
        
        self.assertGreater(len(questions), 0)
        for q in questions:
            self.assertIn('question', q)
            self.assertIn('answer', q)
        
        # Clean up
        if os.path.exists("test_questions.json"):
            os.remove("test_questions.json")

if __name__ == '__main__':
    unittest.main()