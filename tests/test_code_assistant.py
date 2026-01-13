import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from code_assistant import CodeAssistant

class TestCodeAssistant:
    
    @pytest.fixture
    def assistant(self):
        """Create CodeAssistant instance"""
        with patch('code_assistant.OpenAI'):
            return CodeAssistant()
    
    @patch('code_assistant.OpenAI')
    def test_generate_code_rust(self, mock_openai, assistant):
        """Test Rust code generation"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """
fn main() {
    println!("Hello, world!");
}

#[cfg(test)]
mod tests {
    #[test]
    fn test_hello() {
        assert_eq!(2 + 2, 4);
    }
}
"""
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        assistant.client = mock_client
        
        code = assistant.generate_code("hello world", "rust")
        
        assert "fn main()" in code
        assert "#[cfg(test)]" in code
    
    @patch('code_assistant.OpenAI')
    def test_generate_code_python(self, mock_openai, assistant):
        """Test Python code generation"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """
def hello():
    return "Hello, world!"

if __name__ == "__main__":
    print(hello())

import unittest

class TestHello(unittest.TestCase):
    def test_hello(self):
        self.assertEqual(hello(), "Hello, world!")
"""
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        assistant.client = mock_client
        
        code = assistant.generate_code("hello world", "python")
        
        assert "def hello()" in code
        assert "unittest" in code
    
    def test_create_rust_project(self, assistant):
        """Test Rust project creation"""
        code = """
// serde = "1.0"
// tokio = { version = "1.0", features = ["full"] }

fn main() {
    println!("Hello, world!");
}
"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir, clean_code = assistant.create_rust_project(code, temp_dir)
            
            # Check project structure
            assert os.path.exists(os.path.join(project_dir, "Cargo.toml"))
            assert os.path.exists(os.path.join(project_dir, "src", "main.rs"))
            
            # Check Cargo.toml content
            with open(os.path.join(project_dir, "Cargo.toml")) as f:
                cargo_content = f.read()
                assert "serde" in cargo_content
                assert "tokio" in cargo_content
            
            # Check clean code (no comments)
            assert "serde" not in clean_code
            assert "fn main()" in clean_code
    
    @patch('code_assistant.subprocess.run')
    def test_test_rust_code_success(self, mock_run, assistant):
        """Test successful Rust code testing"""
        # Mock check_rust_available to return True
        with patch.object(assistant, 'check_rust_available', return_value=True):
            # Mock successful build and test
            mock_run.side_effect = [
                Mock(returncode=0, stderr=""),  # Build success
                Mock(returncode=0, stderr="")   # Test success
            ]
            
            code = "fn main() { println!('Hello'); }"
            success, output = assistant.test_rust_code(code)
            
            assert success
            assert "All tests passed!" in output
    
    @patch('code_assistant.subprocess.run')
    def test_test_rust_code_build_failure(self, mock_run, assistant):
        """Test Rust code build failure"""
        mock_run.return_value = Mock(returncode=1, stderr="Build error")
        
        code = "invalid rust code"
        success, output = assistant.test_rust_code(code)
        
        assert not success
        assert "Build failed" in output
    
    @patch('code_assistant.subprocess.run')
    def test_test_python_code_success(self, mock_run, assistant):
        """Test successful Python code testing"""
        # Mock get_python_command to avoid subprocess calls in setup
        with patch.object(assistant, 'get_python_command', return_value='python3'):
            mock_run.side_effect = [
                Mock(returncode=0, stderr=""),  # Syntax check
                Mock(returncode=0, stderr="")   # Execution
            ]
            
            code = "print('Hello, world!')"
            success, output = assistant.test_python_code(code)
            
            assert success
            assert "successfully" in output
    
    @patch('code_assistant.subprocess.run')
    def test_test_python_code_syntax_error(self, mock_run, assistant):
        """Test Python syntax error"""
        mock_run.return_value = Mock(returncode=1, stderr="SyntaxError")
        
        code = "print('unclosed string"
        success, output = assistant.test_python_code(code)
        
        assert not success
        assert "Syntax error" in output
    
    @patch('code_assistant.subprocess.run')
    def test_test_python_code_with_tests(self, mock_run, assistant):
        """Test Python code with pytest"""
        # Mock get_python_command to avoid subprocess calls in setup
        with patch.object(assistant, 'get_python_command', return_value='python3'):
            mock_run.side_effect = [
                Mock(returncode=0, stderr=""),  # Syntax check
                Mock(returncode=0, stderr=""),  # Execution
                Mock(returncode=0, stderr="")   # pytest
            ]
            
            code = """
import pytest

def add(a, b):
    return a + b

def test_add():
    assert add(2, 3) == 5
"""
            success, output = assistant.test_python_code(code)
            
            assert success
    
    def test_solve_task_success(self, assistant):
        """Test successful task solving"""
        with patch.object(assistant, 'generate_code') as mock_generate:
            with patch.object(assistant, 'test_python_code') as mock_test:
                mock_generate.return_value = "def hello(): return 'Hello'"
                mock_test.return_value = (True, "Success!")
                
                result = assistant.solve_task("create hello function")
                
                assert result["success"]
                assert result["attempts"] == 1
                assert "def hello()" in result["final_code"]
    
    def test_solve_task_failure_then_success(self, assistant):
        """Test task solving with initial failure then success"""
        with patch.object(assistant, 'generate_code') as mock_generate:
            with patch.object(assistant, 'test_python_code') as mock_test:
                mock_generate.side_effect = [
                    "def hello(): return 'Hello'",  # First attempt
                    "def hello(): return 'Hello, World!'"  # Second attempt
                ]
                mock_test.side_effect = [
                    (False, "Test failed"),  # First test fails
                    (True, "Success!")       # Second test passes
                ]
                
                result = assistant.solve_task("create hello function")
                
                assert result["success"]
                assert result["attempts"] == 2
    
    def test_solve_task_max_attempts_failure(self, assistant):
        """Test task solving with max attempts reached"""
        with patch.object(assistant, 'generate_code') as mock_generate:
            with patch.object(assistant, 'test_python_code') as mock_test:
                mock_generate.return_value = "invalid code"
                mock_test.return_value = (False, "Always fails")
                
                result = assistant.solve_task("impossible task")
                
                assert not result["success"]
                assert result["attempts"] == assistant.max_attempts
                assert "Always fails" in result["final_error"]
    
    def test_language_detection(self, assistant):
        """Test language detection from task description"""
        with patch.object(assistant, 'generate_code') as mock_generate:
            with patch.object(assistant, 'test_rust_code') as mock_test_rust:
                with patch.object(assistant, 'test_python_code') as mock_test_python:
                    with patch.object(assistant, 'check_rust_available') as mock_rust_check:
                        mock_generate.return_value = "fn main() {}"
                        mock_test_rust.return_value = (True, "Success!")
                        mock_test_python.return_value = (True, "Success!")
                        mock_rust_check.return_value = True  # Mock Rust as available
                        
                        # Rust task
                        assistant.solve_task("write quicksort in Rust")
                        mock_test_rust.assert_called()
                        
                        # Python task (default)
                        assistant.solve_task("write quicksort")
                        mock_test_python.assert_called()
    
    @patch('code_assistant.subprocess.run')
    def test_timeout_handling(self, mock_run, assistant):
        """Test timeout handling in code execution"""
        from subprocess import TimeoutExpired
        # Mock get_python_command to avoid subprocess calls in setup
        with patch.object(assistant, 'get_python_command', return_value='python3'):
            mock_run.side_effect = TimeoutExpired("python", 30)
            
            success, output = assistant.test_python_code("while True: pass")
            
            assert not success
            assert "timed out" in output