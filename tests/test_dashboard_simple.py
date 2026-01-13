import unittest
from unittest.mock import Mock, patch
import sqlite3
import tempfile
import os
import pandas as pd
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dashboard import MetricsDashboard
except ImportError:
    MetricsDashboard = None

class TestMetricsDashboard(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        if MetricsDashboard is None:
            self.skipTest("Dashboard not available - missing dependencies")
    
    def test_simple_dashboard_creation(self):
        """Test dashboard can be created"""
        # Use in-memory database to avoid file issues
        with patch('dashboard.sqlite3.connect') as mock_connect:
            mock_conn = Mock()
            mock_conn.execute.return_value.fetchone.return_value = [0]  # Empty database
            mock_connect.return_value = mock_conn
            
            dashboard = MetricsDashboard()
            self.assertIsNotNone(dashboard)
    
    def test_metrics_structure(self):
        """Test that metrics methods exist"""
        with patch('dashboard.sqlite3.connect') as mock_connect:
            mock_conn = Mock()
            mock_conn.execute.return_value.fetchone.return_value = [0]
            mock_connect.return_value = mock_conn
            
            dashboard = MetricsDashboard()
            
            # Test methods exist
            self.assertTrue(hasattr(dashboard, 'get_chat_metrics'))
            self.assertTrue(hasattr(dashboard, 'get_rag_metrics'))
            self.assertTrue(hasattr(dashboard, 'get_agent_metrics'))

if __name__ == '__main__':
    unittest.main()