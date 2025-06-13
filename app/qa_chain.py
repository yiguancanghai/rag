"""
问答链模块 - RAG检索增强生成系统
QA Chain Module - RAG Retrieval-Augmented Generation system
"""

import os
from typing import Dict, Any, List, Optional
import logging
import time

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult

logger = logging.getLogger(__name__)


class TokenCounterCallback(BaseCallbackHandler):
    """Token计数回调 - Token counting callback"""
    
    def __init__(self):
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
    
    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:
        """LLM调用结束时的回调 - Callback when LLM call ends"""
        if response.llm_output and 'token_usage' in response.llm_output:
            usage = response.llm_output['token_usage']
            self.total_tokens += usage.get('total_tokens', 0)
            self.prompt_tokens += usage.get('prompt_tokens', 0)
            self.completion_tokens += usage.get('completion_tokens', 0)
    
    def reset(self):
        """重置计数器 - Reset counters"""
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0


class QAChain:
    """RAG问答链管理器 - RAG QA chain manager"""
    
    def __init__(
        self,
        model_name: str = "gpt-4o",
        temperature: float = 0,
        max_tokens: int = 2000,
        strict_mode: bool = True
    ):
        """初始化问答链 - Initialize QA chain
        
        Args:
            model_name: 模型名称 - Model name
            temperature: 温度参数 - Temperature parameter
            max_tokens: 最大token数 - Maximum tokens
            strict_mode: 严格模式 - Strict mode
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.strict_mode = strict_mode
        
        # 初始化LLM - Initialize LLM
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Token计数器 - Token counter
        self.token_counter = TokenCounterCallback()
        
        # 创建自定义提示模板 - Create custom prompt template
        self._setup_prompt_template()
        
        self.qa_chain = None
    
    def _setup_prompt_template(self):
        """Setup prompt template"""
        if self.strict_mode:
            # Strict mode: answer only based on context
            template = """You are a professional document Q&A assistant. Please answer the question strictly based on the provided context information.\n\nImportant rules:\n1. You can only use the context information below to answer the question\n2. If there is not enough information in the context to answer, please reply clearly with \"Insufficient data\"\n3. Do not add information that is not in the context\n4. Cite specific document fragments to support your answer\n5. Keep your answer concise and accurate\n\nContext information:\n{context}\n\nQuestion: {question}\n\nAnswer:"""
        else:
            # Normal mode: allow some reasoning
            template = """You are a professional document Q&A assistant. Please mainly answer based on the provided context information, and make reasonable inferences if necessary.\n\nContext information:\n{context}\n\nQuestion: {question}\n\nPlease answer the question based on the context information. If the context is insufficient, please state so and provide your best judgment:"""
        self.prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def setup_chain(self, retriever):
        """Setup retrieval QA chain
        Args:
            retriever: Document retriever
        """
        if retriever is None:
            logger.error("Retriever is None")
            return False
        try:
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                chain_type_kwargs={
                    "prompt": self.prompt,
                    "verbose": True
                },
                return_source_documents=True,
                callbacks=[self.token_counter]
            )
            logger.info("QA chain setup successful")
            return True
        except Exception as e:
            logger.error(f"QA chain setup failed: {e}")
            return False
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """Ask question and get answer
        Args:
            question: User question
        Returns:
            Dict containing answer, sources, tokens, and timing info
        """
        if self.qa_chain is None:
            return {
                'answer': "QA system not initialized",
                'source_documents': [],
                'token_usage': {},
                'response_time': 0,
                'error': True
            }
        try:
            # Reset token counter
            self.token_counter.reset()
            # Record start time
            start_time = time.time()
            # Execute QA
            logger.info(f"Processing question: {question[:100]}...")
            result = self.qa_chain({"query": question})
            # Calculate response time
            response_time = time.time() - start_time
            # Process answer
            answer = result.get('result', '')
            source_documents = result.get('source_documents', [])
            # Format source documents
            formatted_sources = []
            for i, doc in enumerate(source_documents):
                source_info = {
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'source_id': i + 1,
                    'file_name': doc.metadata.get('file_name', 'Unknown'),
                    'page_num': doc.metadata.get('page_num', 'N/A'),
                    'chunk_id': doc.metadata.get('chunk_id', 'N/A')
                }
                formatted_sources.append(source_info)
            # Token usage statistics
            token_usage = {
                'total_tokens': self.token_counter.total_tokens,
                'prompt_tokens': self.token_counter.prompt_tokens,
                'completion_tokens': self.token_counter.completion_tokens
            }
            result_dict = {
                'answer': answer,
                'source_documents': formatted_sources,
                'token_usage': token_usage,
                'response_time': round(response_time, 2),
                'question': question,
                'model': self.model_name,
                'error': False
            }
            logger.info(f"QA completed in {response_time:.2f}s, tokens: {token_usage['total_tokens']}")
            return result_dict
        except Exception as e:
            logger.error(f"Error during QA: {e}")
            return {
                'answer': f"Error processing question: {str(e)}",
                'source_documents': [],
                'token_usage': {},
                'response_time': 0,
                'error': True
            }
    
    def batch_questions(self, questions: List[str]) -> List[Dict[str, Any]]:
        """Batch process questions
        Args:
            questions: List of questions
        Returns:
            List of QA results
        """
        results = []
        total_start_time = time.time()
        for i, question in enumerate(questions):
            logger.info(f"Processing batch question {i+1}/{len(questions)}")
            result = self.ask_question(question)
            results.append(result)
        total_time = time.time() - total_start_time
        logger.info(f"Batch processing completed in {total_time:.2f}s")
        return results
    
    def update_settings(
        self,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        strict_mode: Optional[bool] = None
    ):
        """Update settings"""
        if model_name is not None:
            self.model_name = model_name
        if temperature is not None:
            self.temperature = temperature
        if max_tokens is not None:
            self.max_tokens = max_tokens
        if strict_mode is not None:
            self.strict_mode = strict_mode
        # Reinitialize LLM
        self.llm = ChatOpenAI(
            model_name=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        # Reset prompt template
        self._setup_prompt_template()
        # Reset QA chain
        self.qa_chain = None
        logger.info("Settings updated")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        return {
            'model_name': self.model_name,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'strict_mode': self.strict_mode,
            'chain_initialized': self.qa_chain is not None,
            'total_tokens_used': self.token_counter.total_tokens
        } 