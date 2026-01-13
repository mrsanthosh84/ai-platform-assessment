#!/usr/bin/env python3
import os
import time
import json
import sqlite3
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

# Mock OpenAI client for Python 3.14 compatibility
class MockOpenAI:
    def __init__(self, base_url=None, api_key=None):
        self.base_url = base_url
        self.api_key = api_key
        
    class Chat:
        def __init__(self):
            self.completions = self.Completions()
            
        class Completions:
            def create(self, model=None, messages=None, stream=False, **kwargs):
                last_message = messages[-1]["content"].lower() if messages else ""
                
                if "hello" in last_message:
                    response_text = "Hello! I'm a demo AI assistant. How can I help you today?"
                elif "weather" in last_message:
                    response_text = "I'm a demo version and can't check real weather, but it's probably nice somewhere!"
                elif "time" in last_message:
                    response_text = f"The current time is {time.strftime('%H:%M:%S')}"
                else:
                    response_text = f"I'm a demo AI assistant. You said: '{messages[-1]['content']}'. This is a mock response for Python 3.14 compatibility."
                
                if stream:
                    class MockChunk:
                        def __init__(self, content):
                            self.choices = [type('obj', (object,), {
                                'delta': type('obj', (object,), {'content': content})()
                            })()]
                    
                    words = response_text.split()
                    for i, word in enumerate(words):
                        if i == 0:
                            yield MockChunk(word)
                        else:
                            yield MockChunk(" " + word)
                        time.sleep(0.05)
                    yield MockChunk(None)
    
    @property
    def chat(self):
        return self.Chat()

class ChatBot:
    def __init__(self):
        try:
            # Suppress OpenAI pydantic warning
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                from openai import OpenAI
            
            self.client = OpenAI(
                base_url=os.getenv("OPENAI_BASE_URL"),
                api_key=os.getenv("OPENAI_API_KEY")
            )
            self.is_mock = False
            print("✅ Using real OpenAI API")
        except Exception as e:
            self.client = MockOpenAI(
                base_url=os.getenv("OPENAI_BASE_URL"),
                api_key=os.getenv("OPENAI_API_KEY")
            )
            self.is_mock = True
            print("Using mock AI (OpenAI library incompatible with Python 3.14)")
            print("   Use Docker for full functionality: docker-compose up --build")
        
        self.model = os.getenv("MODEL_NAME", "gpt-4")
        self.init_db()
        
    def init_db(self):
        self.conn = sqlite3.connect("chat_history.db")
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                role TEXT,
                content TEXT,
                timestamp REAL
            )
        """)
        self.conn.commit()
    
    def get_recent_messages(self, n=10) -> List[Dict]:
        cursor = self.conn.execute(
            "SELECT role, content FROM messages ORDER BY timestamp DESC LIMIT ?", (n,)
        )
        messages = [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]
        return list(reversed(messages))
    
    def save_message(self, role: str, content: str):
        self.conn.execute(
            "INSERT INTO messages (role, content, timestamp) VALUES (?, ?, ?)",
            (role, content, time.time())
        )
        self.conn.commit()
    
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        # GPT-4o pricing: $5/1M input, $15/1M output
        input_cost = (prompt_tokens / 1_000_000) * 5.0
        output_cost = (completion_tokens / 1_000_000) * 15.0
        return input_cost + output_cost
    
    def estimate_tokens(self, text: str) -> int:
        """Simple token estimation (fallback when tiktoken not available)"""
        # Rough approximation: ~1.3 tokens per word
        return int(len(text.split()) * 1.3)
    
    def chat_stream(self, user_input: str):
        self.save_message("user", user_input)
        messages = self.get_recent_messages()
        messages.append({"role": "user", "content": user_input})
        
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True
            )
            
            assistant_response = ""
            for chunk in response:
                if hasattr(chunk.choices[0], 'delta') and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    assistant_response += content
            
            print()  # New line after streaming
            
            # Get usage info from final chunk
            latency = int((time.time() - start_time) * 1000)
            
            # Estimate tokens (rough approximation)
            prompt_tokens = sum(self.estimate_tokens(msg["content"]) for msg in messages)
            completion_tokens = self.estimate_tokens(assistant_response)
            cost = self.calculate_cost(int(prompt_tokens), int(completion_tokens))
            
            if self.is_mock:
                print(f"[demo stats] prompt={int(prompt_tokens)} completion={int(completion_tokens)} cost=${cost:.6f} latency={latency}ms")
            else:
                print(f"[stats] prompt={int(prompt_tokens)} completion={int(completion_tokens)} cost=${cost:.6f} latency={latency}ms")
            
            self.save_message("assistant", assistant_response)
            
        except Exception as e:
            print(f"Error: {e}")

def main():
    print("AI Platform Chat")
    print("=" * 30)
    
    bot = ChatBot()
    print("Chat started. Type 'quit' to exit.")
    if bot.is_mock:
        print("Try: 'hello', 'what's the weather?', 'what time is it?'")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit':
            break
        bot.chat_stream(user_input)

if __name__ == "__main__":
    main()