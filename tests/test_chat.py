import unittest
from unittest.mock import Mock, patch, MagicMock
import sqlite3
import tempfile
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from chat import ChatBot
except ImportError:
    ChatBot = None

class TestChatBot(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        if ChatBot is None:
            self.skipTest("ChatBot not available - missing dependencies")
        
        # Create temporary database
        fd, self.temp_db_path = tempfile.mkstemp()
        os.close(fd)
        
        # Mock OpenAI import to avoid initialization issues
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            self.bot = ChatBot()
            self.bot.client = mock_client
            self.bot.conn = sqlite3.connect(self.temp_db_path)
            self.bot.init_db()
    
    def tearDown(self):
        """Clean up test fixtures"""
        if hasattr(self, 'bot') and self.bot:
            self.bot.conn.close()
        if hasattr(self, 'temp_db_path'):
            os.unlink(self.temp_db_path)
    
    def test_init_db(self):
        """Test database initialization"""
        cursor = self.bot.conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        self.assertIn('messages', tables)
    
    def test_save_message(self):
        """Test message saving"""
        # Clear any existing messages first
        self.bot.conn.execute("DELETE FROM messages")
        self.bot.conn.commit()
        
        self.bot.save_message("user", "Hello")
        cursor = self.bot.conn.execute("SELECT role, content FROM messages")
        messages = cursor.fetchall()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], ("user", "Hello"))
    
    def test_get_recent_messages(self):
        """Test retrieving recent messages"""
        # Clear any existing messages first
        self.bot.conn.execute("DELETE FROM messages")
        self.bot.conn.commit()
        
        # Add test messages
        for i in range(15):
            self.bot.save_message("user", f"Message {i}")
        
        messages = self.bot.get_recent_messages(10)
        self.assertEqual(len(messages), 10)
        self.assertEqual(messages[-1]["content"], "Message 14")  # Most recent
    
    def test_calculate_cost(self):
        """Test cost calculation"""
        cost = self.bot.calculate_cost(100, 200)
        expected = (100 / 1_000_000) * 5.0 + (200 / 1_000_000) * 15.0
        self.assertEqual(cost, expected)
    
    @patch('openai.OpenAI')
    def test_chat_stream_success(self, mock_openai):
        """Test successful chat streaming"""
        # Mock OpenAI response
        mock_chunk = Mock()
        mock_chunk.choices = [Mock()]
        mock_chunk.choices[0].delta.content = "Hello"
        
        mock_response = [mock_chunk]
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        self.bot.client = mock_client
        
        with patch('builtins.print'):
            self.bot.chat_stream("Hi")
        
        # Verify message was saved
        cursor = self.bot.conn.execute("SELECT COUNT(*) FROM messages")
        count = cursor.fetchone()[0]
        self.assertGreaterEqual(count, 1)
    
    @patch('openai.OpenAI')
    def test_chat_stream_error(self, mock_openai):
        """Test chat streaming with error"""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        self.bot.client = mock_client
        
        with patch('builtins.print') as mock_print:
            self.bot.chat_stream("Hi")
        
        # Verify error was printed
        mock_print.assert_any_call("Error: API Error")


if __name__ == '__main__':
    unittest.main()