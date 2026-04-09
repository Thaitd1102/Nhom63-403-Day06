"""
RAG (Retrieval-Augmented Generation) Module
Integrates PDF knowledge into VinFast AI Advisor
"""
from pathlib import Path
from pypdf import PdfReader
import os
import re
from dotenv import load_dotenv

# Load .env NGAY ĐÂY để OPENAI_API_KEY có sẵn khi chạy rag.py trực tiếp
load_dotenv()

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# Configuration
PDF_PATH = Path(__file__).parent / "VINFAST VF1.pdf"
VECTOR_STORE_PATH = Path(__file__).parent / "vector_db"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 200


# Fallback embedding function (hash-based, no API needed)
class SimpleEmbedding:
    """Mock embedding using hash - fallback when API key unavailable"""
    def __init__(self):
        self.dimension = 384
    
    def embed_documents(self, texts):
        """Generate fake embeddings based on text hash"""
        embeddings = []
        for text in texts:
            # Create a deterministic embedding from text hash
            hash_val = hash(text)
            # Convert hash to embedding vector
            embedding = [(hash_val >> (i * 8)) & 0xFF for i in range(self.dimension)]
            # Normalize
            mag = sum(x**2 for x in embedding) ** 0.5
            if mag > 0:
                embedding = [x / mag for x in embedding]
            embeddings.append(embedding)
        return embeddings
    
    def embed_query(self, text):
        """Embed a single query"""
        return self.embed_documents([text])[0]


class RAGVinFastKnowledge:
    """Load and query VinFast knowledge from PDF"""
    
    def __init__(self):
        self.vector_store = None
        self.retriever = None
        self._initialize()
    
    def _initialize(self):
        """Initialize RAG system from PDF"""
        # Check if vector store already exists
        if VECTOR_STORE_PATH.exists():
            print(f"📚 Loading cached knowledge from {VECTOR_STORE_PATH}")
            try:
                # Try to load with OpenAI embeddings first
                self.vector_store = Chroma(
                    persist_directory=str(VECTOR_STORE_PATH),
                    embedding_function=self._get_embeddings()
                )
            except Exception as e:
                print(f"⚠️  Could not load cached vector store: {e}")
                print("   Creating new vector store...")
                self._create_vector_store()
        else:
            self._create_vector_store()
        
        # Create retriever
        if self.vector_store:
            self.retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}  # Return top 3 relevant chunks
            )
    
    def _get_embeddings(self):
        """Get embeddings function - use OpenAI if API key available, else fallback"""
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                print("🔑 Using OpenAI embeddings")
                return OpenAIEmbeddings(api_key=api_key)
            except Exception as e:
                print(f"⚠️  OpenAI embeddings failed: {e}")
                print("   Falling back to simple embeddings")
                return SimpleEmbedding()
        else:
            print("⚠️  OPENAI_API_KEY not set - using fallback embeddings")
            return SimpleEmbedding()
    
    def _create_vector_store(self):
        """Create vector store from PDF"""
        print(f"📖 Reading PDF from {PDF_PATH}...")
        if not PDF_PATH.exists():
            raise FileNotFoundError(f"PDF not found: {PDF_PATH}")
        
        # Extract text from PDF
        pdf_text = self._extract_pdf_text()
        
        # Split into chunks
        print(f"✂️  Splitting into chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
        chunks = self._chunk_text(pdf_text)
        print(f"   → Created {len(chunks)} chunks")
        
        # Create vector store with embeddings
        print(f"🔹 Creating vector store...")
        documents = [
            Document(page_content=chunk, metadata={"source": "VINFAST VF1.pdf"})
            for chunk in chunks
        ]
        self.documents = documents
        
        embedding_fn = self._get_embeddings()
        
        try:
            self.vector_store = Chroma.from_documents(
                documents,
                embedding=embedding_fn,
                persist_directory=str(VECTOR_STORE_PATH)
            )
            print(f"✅ Vector store saved to {VECTOR_STORE_PATH}")
        except Exception as e:
            print(f"❌ Failed to create vector store: {e}")
            self.vector_store = None
    
    def _extract_pdf_text(self) -> str:
        """Extract text from PDF"""
        pdf_reader = PdfReader(PDF_PATH)
        full_text = ""
        
        for page_num, page in enumerate(pdf_reader.pages, 1):
            text = page.extract_text()
            full_text += f"\n\n--- Page {page_num} ---\n{text}"
        
        return full_text
    
    def _chunk_text(self, text: str) -> list[str]:
        """Split text into manageable chunks"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        return splitter.split_text(text)
    
    def query(self, question: str) -> str:
        """
        Query PDF knowledge base
        
        Args:
            question: User question about VinFast vehicles
            
        Returns:
            Concatenated relevant context from PDF
        """
        if self.retriever:
            # Use Chroma vector search (best)
            try:
                docs = self.retriever.invoke(question)
                context = "\n\n---\n\n".join([doc.page_content for doc in docs])
                return context
            except Exception as e:
                print(f"⚠️ Vector search error: {e}")
                pass
        
        if hasattr(self, 'documents') and self.documents:
            # Fallback: keyword-based search
            question_lower = question.lower()
            # Extract meaningful keywords (length > 2)
            keywords = re.findall(r'\b\w{3,}\b', question_lower)
            
            matched_docs = []
            for doc in self.documents:
                content_lower = doc.page_content.lower()
                # Count keyword matches
                matches = sum(1 for kw in keywords if kw in content_lower)
                if matches > 0:
                    matched_docs.append((doc, matches))
            
            # Sort by number of matches, return top 3
            if matched_docs:
                matched_docs.sort(key=lambda x: x[1], reverse=True)
                context = "\n\n---\n\n".join([doc.page_content for doc, _ in matched_docs[:3]])
                if context.strip():
                    return context
        
        return ""
    
    def query_with_scores(self, question: str, k: int = 3) -> list[tuple[str, float]]:
        """
        Query with similarity scores
        
        Returns:
            List of (content, score) tuples
        """
        if not self.vector_store:
            return []
        
        results = self.vector_store.similarity_search_with_score(question, k=k)
        return [(doc.page_content, score) for doc, score in results]


# Global RAG instance
rag_knowledge = None


def initialize_rag():
    """Initialize global RAG instance"""
    global rag_knowledge
    if rag_knowledge is None:
        print("\n🚀 Initializing RAG from PDF...")
        rag_knowledge = RAGVinFastKnowledge()
        print("✅ RAG initialized successfully\n")
    return rag_knowledge


def get_rag_context(question: str) -> str:
    """
    Helper function to get RAG context
    
    Usage in tools:
        from rag import get_rag_context
        context = get_rag_context("VF e34 pin bao nhiêu?")
    """
    global rag_knowledge
    if rag_knowledge is None:
        initialize_rag()
    
    return rag_knowledge.query(question)


if __name__ == "__main__":
    # Test RAG
    rag = initialize_rag()
    
    # Example queries
    test_queries = [
        "VF e34 pin bao nhiêu kWh?",
        "VF8 có bao nhiêu tính năng an toàn?",
        "Giá VF9 là bao nhiêu?",
        "VF3 tầm hoạt động là bao nhiêu km?"
    ]
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        print(f"📖 Context from PDF:")
        context = rag.query(query)
        print(context[:500] + "..." if len(context) > 500 else context)
