#!/usr/bin/env python3
import os
import time
import requests
import json
from typing import List, Dict, Tuple
from dotenv import load_dotenv

# Suppress OpenAI pydantic warning
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore", UserWarning)
    from openai import OpenAI

# Try to import PDF reader, prefer pypdf over PyPDF2
try:
    from pypdf import PdfReader
except ImportError:
    # Suppress the deprecation warning by importing with warnings disabled
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from PyPDF2 import PdfReader

# Try to import chromadb, fall back to simple storage if not available
try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("ChromaDB not available, using simple in-memory storage")

load_dotenv()

class SimpleVectorStore:
    """Simple in-memory vector store fallback"""
    def __init__(self):
        self.documents = []
        self.metadatas = []
        self.ids = []
    
    def add(self, documents, metadatas, ids):
        self.documents.extend(documents)
        self.metadatas.extend(metadatas)
        self.ids.extend(ids)
    
    def query(self, query_texts, n_results=5):
        # Simple keyword matching fallback
        query = query_texts[0].lower()
        scores = []
        
        for i, doc in enumerate(self.documents):
            doc_lower = doc.lower()
            # Simple scoring based on keyword matches
            score = sum(1 for word in query.split() if word in doc_lower)
            scores.append((score, i))
        
        # Sort by score and take top results
        scores.sort(reverse=True)
        top_indices = [idx for _, idx in scores[:n_results]]
        
        return {
            'documents': [[self.documents[i] for i in top_indices]],
            'metadatas': [[self.metadatas[i] for i in top_indices]],
            'distances': [[1.0 - (scores[i][0] / max(1, len(query.split())))] for i in range(len(top_indices))]
        }
    
    def count(self):
        return len(self.documents)

class RAGSystem:
    def __init__(self):
        try:
            self.client = OpenAI(
                base_url=os.getenv("OPENAI_BASE_URL"),
                api_key=os.getenv("OPENAI_API_KEY")
            )
            self.is_mock = False
            print("✅ Using real OpenAI API")
        except Exception as e:
            # Mock OpenAI for Python 3.14 compatibility
            class MockOpenAI:
                def __init__(self, **kwargs):
                    pass
                class Chat:
                    class Completions:
                        def create(self, **kwargs):
                            class MockResponse:
                                def __init__(self):
                                    self.choices = [type('obj', (object,), {
                                        'message': type('obj', (object,), {
                                            'content': "This is a mock response. The RAG system retrieved relevant documents but OpenAI API is not available in Python 3.14. Use Docker for full functionality."
                                        })()
                                    })()]
                            return MockResponse()
                    @property
                    def completions(self):
                        return self.Completions()
                @property
                def chat(self):
                    return self.Chat()
            
            self.client = MockOpenAI()
            self.is_mock = True
            print("⚠️  Using mock responses (OpenAI library incompatible with Python 3.14)")
        
        self.model = os.getenv("MODEL_NAME", "gpt-4")
        
        if CHROMADB_AVAILABLE:
            self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
            self.collection = self.chroma_client.get_or_create_collection("documents")
        else:
            self.collection = SimpleVectorStore()
        
    def download_and_process_pdfs(self):
        urls = [
            "https://www.mrsmuellersworld.com/uploads/1/3/0/5/13054185/lord-of-the-rings-01-the-fellowship-of-the-ring_full_text.pdf"
        ]
        
        for i, url in enumerate(urls):
            try:
                print(f"Downloading PDF {i+1}...")
                response = requests.get(url, timeout=30)
                filename = f"document_{i+1}.pdf"
                
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                self.process_pdf(filename, f"doc_{i+1}")
                os.remove(filename)
                
            except Exception as e:
                print(f"Error processing {url}: {e}")
    
    def process_pdf(self, filename: str, doc_id: str):
        reader = PdfReader(filename)
        chunks = []
        
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            # Split into chunks of ~500 words
            words = text.split()
            for i in range(0, len(words), 500):
                chunk = " ".join(words[i:i+500])
                if len(chunk.strip()) > 50:  # Skip very short chunks
                    chunks.append({
                        "text": chunk,
                        "metadata": {"doc_id": doc_id, "page": page_num, "chunk_id": f"{doc_id}_p{page_num}_c{i//500}"}
                    })
        
        # Add to ChromaDB
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        ids = [chunk["metadata"]["chunk_id"] for chunk in chunks]
        
        # Add in batches to avoid memory issues
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_metadatas = metadatas[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            
            self.collection.add(
                documents=batch_texts,
                metadatas=batch_metadatas,
                ids=batch_ids
            )
        
        print(f"Processed {len(chunks)} chunks from {filename}")
    
    def retrieve(self, query: str, n_results: int = 5) -> List[Dict]:
        start_time = time.time()
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        retrieval_time = (time.time() - start_time) * 1000
        
        retrieved_docs = []
        
        # Check if results exist and have documents
        if results and 'documents' in results and len(results['documents']) > 0 and len(results['documents'][0]) > 0:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if 'metadatas' in results and len(results['metadatas'][0]) > i else {"chunk_id": f"unknown_{i}"}
                score = results['distances'][0][i] if 'distances' in results and len(results['distances'][0]) > i else 0
                
                retrieved_docs.append({
                    "text": doc,
                    "metadata": metadata,
                    "score": score
                })
        
        print(f"Retrieval time: {retrieval_time:.1f}ms")
        return retrieved_docs
    
    def answer_question(self, question: str) -> str:
        # Retrieve relevant documents
        docs = self.retrieve(question)
        
        # Build context
        context = "\n\n".join([f"[{doc['metadata']['chunk_id']}] {doc['text']}" for doc in docs])
        
        prompt = f"""Answer the question based on the provided context. Include inline citations using the chunk IDs.

Context:
{context}

Question: {question}

Answer:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            
            if self.is_mock:
                # Show retrieved context for demo
                print(f"\nRetrieved {len(docs)} relevant documents:")
                for i, doc in enumerate(docs[:2]):  # Show first 2 docs
                    print(f"  [{doc['metadata']['chunk_id']}] {doc['text'][:100]}...")
            
            return answer
            
        except Exception as e:
            return f"Error generating answer: {e}"

def create_test_questions():
    """Create test questions for evaluation"""
    questions = [
        {"question": "Who is Frodo Baggins?", "answer": "Frodo is a hobbit who inherits the One Ring from Bilbo"},
        {"question": "What is the One Ring?", "answer": "The One Ring is a powerful ring created by the Dark Lord Sauron"},
        {"question": "Where does the Fellowship begin their journey?", "answer": "The Fellowship begins their journey from Rivendell"},
        {"question": "Who are the members of the Fellowship?", "answer": "Frodo, Sam, Merry, Pippin, Gandalf, Aragorn, Boromir, Legolas, and Gimli"},
        {"question": "What is Mordor?", "answer": "Mordor is the dark realm of Sauron where the Ring must be destroyed"},
    ]
    
    with open("test_questions.json", "w") as f:
        json.dump(questions, f, indent=2)
    
    return questions

def evaluate_retrieval(rag_system: RAGSystem):
    """Evaluate retrieval accuracy"""
    questions = create_test_questions()
    
    correct = 0
    total = len(questions)
    
    for q in questions:
        try:
            docs = rag_system.retrieve(q["question"])
            if not docs:  # No documents retrieved
                continue
                
            # Simple evaluation: check if any retrieved doc contains key terms from expected answer
            answer_terms = set(q["answer"].lower().split())
            
            for doc in docs:
                doc_terms = set(doc["text"].lower().split())
                if len(answer_terms.intersection(doc_terms)) >= 2:  # At least 2 matching terms
                    correct += 1
                    break
        except Exception as e:
            print(f"Error evaluating question '{q['question']}': {e}")
            continue
    
    accuracy = correct / total if total > 0 else 0
    print(f"Top-5 Retrieval Accuracy: {accuracy:.2%} ({correct}/{total})")
    return accuracy

def main():
    print("🔍 RAG System Demo")
    print("=" * 30)
    
    try:
        rag = RAGSystem()
        
        # Check if we need to ingest documents
        if rag.collection.count() == 0:
            print("Ingesting documents...")
            rag.download_and_process_pdfs()
        else:
            print(f"Found {rag.collection.count()} existing documents")
        
        # Run evaluation
        print("\nRunning retrieval evaluation...")
        evaluate_retrieval(rag)
        
        # Interactive QA
        print("\nQA System ready. Type 'quit' to exit.")
        print("Try asking: 'Who is Frodo?' or 'What is the One Ring?'")
        
        while True:
            question = input("\nQuestion: ")
            if question.lower() == 'quit':
                break
            
            start_time = time.time()
            answer = rag.answer_question(question)
            total_time = (time.time() - start_time) * 1000
            
            print(f"\nAnswer: {answer}")
            print(f"Total time: {total_time:.1f}ms")
            
    except Exception as e:
        print(f"Error initializing RAG system: {e}")
        print("Try using Docker for full functionality: docker-compose up --build")

if __name__ == "__main__":
    main()