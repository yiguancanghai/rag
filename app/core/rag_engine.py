from typing import List, Dict, Optional, Tuple
import chromadb
from chromadb.config import Settings

from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.callbacks.base import BaseCallbackHandler

from utils.logger import logger
from utils.config import Config


class StreamlitCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for Streamlit streaming"""
    
    def __init__(self, container):
        self.container = container
        self.text = ""
        
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)


class RAGEngine:
    """Core RAG (Retrieval-Augmented Generation) engine"""
    
    def __init__(self):
        self.config = Config()
        self.config.validate_config()
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=self.config.OPENAI_API_KEY,
            model="text-embedding-ada-002"
        )
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            openai_api_key=self.config.OPENAI_API_KEY,
            model_name="gpt-4-turbo-preview",
            temperature=self.config.TEMPERATURE,
            max_tokens=self.config.MAX_TOKENS,
            streaming=True
        )
        
        # Initialize vector store
        self.vector_store = None
        self.retrieval_qa = None
        
        # Initialize Chroma client
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.config.VECTOR_DB_DIR)
        )
        
        self._setup_vector_store()
        
    def _setup_vector_store(self):
        """Initialize vector store"""
        try:
            self.vector_store = Chroma(
                client=self.chroma_client,
                collection_name="documents",
                embedding_function=self.embeddings,
                persist_directory=str(self.config.VECTOR_DB_DIR)
            )
            logger.info("Vector store initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Document]) -> bool:
        """Add documents to vector store"""
        try:
            if not documents:
                logger.warning("No documents provided to add")
                return False
            
            # Add documents to vector store
            self.vector_store.add_documents(documents)
            
            logger.info(f"Added {len(documents)} documents to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            return False
    
    def _create_retrieval_qa_chain(self, k: int = 4):
        """Create retrieval QA chain"""
        
        # Custom prompt template for better context handling
        prompt_template = """
        You are an intelligent document assistant. Use the following context to answer the user's question accurately and comprehensively.
        
        Context from documents:
        {context}
        
        Question: {question}
        
        Instructions:
        1. Answer based ONLY on the provided context
        2. If the context doesn't contain enough information to answer the question, say "I don't have enough information in the provided documents to answer this question."
        3. Include relevant details and examples from the context
        4. Cite the source document when possible
        5. Be concise but thorough
        
        Answer:
        """
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create retriever
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )
        
        # Create RetrievalQA chain
        self.retrieval_qa = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )
        
        return self.retrieval_qa
    
    def query(self, question: str, k: int = 4, stream_container=None) -> Dict:
        """Query the RAG system"""
        try:
            if not self.vector_store:
                raise ValueError("Vector store not initialized")
            
            # Check if we have any documents
            collection = self.chroma_client.get_collection("documents")
            if collection.count() == 0:
                return {
                    "answer": "No documents have been uploaded yet. Please upload some documents first.",
                    "source_documents": [],
                    "confidence_score": 0.0
                }
            
            # Create or update retrieval chain
            qa_chain = self._create_retrieval_qa_chain(k=k)
            
            # Add streaming callback if container provided
            callbacks = []
            if stream_container:
                callbacks.append(StreamlitCallbackHandler(stream_container))
            
            # Query the system
            result = qa_chain(
                {"query": question},
                callbacks=callbacks if callbacks else None
            )
            
            # Calculate confidence score based on similarity
            confidence_score = self._calculate_confidence_score(
                question, result.get("source_documents", [])
            )
            
            # Format response
            response = {
                "answer": result["result"],
                "source_documents": self._format_source_documents(
                    result.get("source_documents", [])
                ),
                "confidence_score": confidence_score,
                "question": question
            }
            
            logger.info(f"Query processed: {question[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "answer": f"An error occurred while processing your question: {str(e)}",
                "source_documents": [],
                "confidence_score": 0.0
            }
    
    def _calculate_confidence_score(self, question: str, source_docs: List[Document]) -> float:
        """Calculate confidence score based on document similarity"""
        if not source_docs:
            return 0.0
        
        # Simple heuristic: average of document relevance
        # In a production system, you might use more sophisticated methods
        try:
            # For now, return a score based on number of retrieved documents
            # and their average length (more content = potentially more relevant)
            avg_length = sum(len(doc.page_content) for doc in source_docs) / len(source_docs)
            
            # Normalize score between 0.3 and 0.95
            base_score = min(0.95, 0.3 + (len(source_docs) / 10) + (avg_length / 2000))
            return round(base_score, 2)
            
        except Exception:
            return 0.5
    
    def _format_source_documents(self, source_docs: List[Document]) -> List[Dict]:
        """Format source documents for display"""
        return [
            {
                "content": doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content,
                "source": doc.metadata.get("source_file", "Unknown"),
                "page": doc.metadata.get("page", "N/A"),
                "file_type": doc.metadata.get("file_type", "Unknown")
            }
            for doc in source_docs
        ]
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the document collection"""
        try:
            collection = self.chroma_client.get_collection("documents")
            return {
                "total_documents": collection.count(),
                "collection_name": "documents"
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {"total_documents": 0, "collection_name": "documents"}
    
    def clear_collection(self) -> bool:
        """Clear all documents from the collection"""
        try:
            # Delete the collection and recreate it
            try:
                self.chroma_client.delete_collection("documents")
            except Exception:
                pass  # Collection might not exist
            
            # Recreate vector store
            self._setup_vector_store()
            
            logger.info("Document collection cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            return False
    
    def search_similar(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar documents without generating an answer"""
        try:
            if not self.vector_store:
                return []
            
            # Perform similarity search
            docs = self.vector_store.similarity_search(query, k=k)
            
            return self._format_source_documents(docs)
            
        except Exception as e:
            logger.error(f"Error searching similar documents: {str(e)}")
            return []