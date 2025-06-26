from typing import Dict, List, Optional, Tuple
from enum import Enum
import re

from langchain.schema import Document
from langchain_openai import ChatOpenAI

from utils.logger import logger
from utils.config import Config


class QueryType(Enum):
    """Types of queries the system can handle"""
    FACTUAL = "factual"          # Direct fact-based questions
    ANALYTICAL = "analytical"     # Analysis and comparison questions
    SUMMARIZATION = "summarization"  # Summary requests
    PROCEDURAL = "procedural"    # How-to questions
    GENERAL = "general"         # General conversation


class QueryComplexity(Enum):
    """Complexity levels for query processing"""
    SIMPLE = "simple"        # Single document, direct answer
    MEDIUM = "medium"        # Multiple documents, some analysis
    COMPLEX = "complex"      # Deep analysis, multiple sources


class IntelligentRouter:
    """Route queries to optimal processing strategies"""
    
    def __init__(self):
        self.config = Config()
        
        # Simple LLM for query classification
        self.classifier_llm = ChatOpenAI(
            openai_api_key=self.config.OPENAI_API_KEY,
            model_name="gpt-3.5-turbo",
            temperature=0.0,
            max_tokens=100
        )
        
        # Query patterns for rule-based classification
        self.query_patterns = {
            QueryType.FACTUAL: [
                r'\b(what|who|when|where|which|how many|how much)\b',
                r'\b(define|definition|meaning)\b',
                r'\b(is|are|was|were|did|does|do)\b.*\?'
            ],
            QueryType.ANALYTICAL: [
                r'\b(compare|contrast|difference|similar|analyze|analysis)\b',
                r'\b(why|how|explain|reason|cause|effect)\b',
                r'\b(advantages|disadvantages|pros|cons)\b'
            ],
            QueryType.SUMMARIZATION: [
                r'\b(summarize|summary|overview|main points|key points)\b',
                r'\b(tell me about|describe|outline)\b',
                r'\b(what are the.*topics|themes|ideas)\b'
            ],
            QueryType.PROCEDURAL: [
                r'\b(how to|steps|process|procedure|method)\b',
                r'\b(guide|tutorial|instructions)\b',
                r'\b(implement|create|build|setup)\b'
            ]
        }
    
    def analyze_query(self, query: str) -> Dict:
        """Analyze query and determine optimal processing strategy"""
        
        # Classify query type
        query_type = self._classify_query_type(query)
        
        # Determine complexity
        complexity = self._assess_complexity(query, query_type)
        
        # Get processing strategy
        strategy = self._get_processing_strategy(query_type, complexity)
        
        analysis = {
            "query": query,
            "type": query_type,
            "complexity": complexity,
            "strategy": strategy,
            "confidence": self._calculate_classification_confidence(query, query_type)
        }
        
        logger.info(f"Query analysis: {query_type.value}, {complexity.value}")
        return analysis
    
    def _classify_query_type(self, query: str) -> QueryType:
        """Classify query type using pattern matching"""
        
        query_lower = query.lower()
        
        # Score each query type based on pattern matches
        type_scores = {}
        
        for query_type, patterns in self.query_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query_lower))
                score += matches
            type_scores[query_type] = score
        
        # Find the type with highest score
        best_type = max(type_scores, key=type_scores.get)
        
        # If no patterns match, default to GENERAL
        if type_scores[best_type] == 0:
            return QueryType.GENERAL
        
        return best_type
    
    def _assess_complexity(self, query: str, query_type: QueryType) -> QueryComplexity:
        """Assess query complexity based on various factors"""
        
        complexity_indicators = 0
        
        # Length-based complexity
        if len(query.split()) > 15:
            complexity_indicators += 1
        
        # Multiple questions
        if query.count('?') > 1:
            complexity_indicators += 1
        
        # Comparison words
        comparison_words = ['compare', 'contrast', 'versus', 'vs', 'different', 'similar']
        if any(word in query.lower() for word in comparison_words):
            complexity_indicators += 1
        
        # Multiple concepts
        concept_words = ['and', 'or', 'both', 'either', 'multiple', 'various', 'several']
        if any(word in query.lower() for word in concept_words):
            complexity_indicators += 1
        
        # Analysis keywords
        analysis_words = ['analyze', 'evaluate', 'assess', 'relationship', 'impact', 'implications']
        if any(word in query.lower() for word in analysis_words):
            complexity_indicators += 1
        
        # Determine complexity level
        if complexity_indicators >= 3:
            return QueryComplexity.COMPLEX
        elif complexity_indicators >= 1:
            return QueryComplexity.MEDIUM
        else:
            return QueryComplexity.SIMPLE
    
    def _get_processing_strategy(self, query_type: QueryType, complexity: QueryComplexity) -> Dict:
        """Get optimal processing strategy based on query analysis"""
        
        strategy = {
            "retrieval_k": 4,
            "temperature": 0.1,
            "max_tokens": 1500,
            "prompt_template": "default",
            "post_processing": []
        }
        
        # Adjust based on query type
        if query_type == QueryType.FACTUAL:
            strategy.update({
                "retrieval_k": 3,
                "temperature": 0.0,
                "max_tokens": 1000,
                "prompt_template": "factual"
            })
        
        elif query_type == QueryType.ANALYTICAL:
            strategy.update({
                "retrieval_k": 6,
                "temperature": 0.2,
                "max_tokens": 2000,
                "prompt_template": "analytical",
                "post_processing": ["confidence_check"]
            })
        
        elif query_type == QueryType.SUMMARIZATION:
            strategy.update({
                "retrieval_k": 8,
                "temperature": 0.1,
                "max_tokens": 1500,
                "prompt_template": "summary",
                "post_processing": ["structure_check"]
            })
        
        elif query_type == QueryType.PROCEDURAL:
            strategy.update({
                "retrieval_k": 5,
                "temperature": 0.0,
                "max_tokens": 2000,
                "prompt_template": "procedural",
                "post_processing": ["step_validation"]
            })
        
        # Adjust based on complexity
        if complexity == QueryComplexity.COMPLEX:
            strategy["retrieval_k"] = min(strategy["retrieval_k"] + 2, 10)
            strategy["max_tokens"] = min(strategy["max_tokens"] + 500, 3000)
            strategy["post_processing"].append("complexity_validation")
        
        elif complexity == QueryComplexity.SIMPLE:
            strategy["retrieval_k"] = max(strategy["retrieval_k"] - 1, 2)
            strategy["max_tokens"] = max(strategy["max_tokens"] - 300, 800)
        
        return strategy
    
    def _calculate_classification_confidence(self, query: str, classified_type: QueryType) -> float:
        """Calculate confidence in query classification"""
        
        # Simple heuristic based on pattern matches
        if classified_type == QueryType.GENERAL:
            return 0.6  # Low confidence for general queries
        
        patterns = self.query_patterns.get(classified_type, [])
        query_lower = query.lower()
        
        total_matches = sum(len(re.findall(pattern, query_lower)) for pattern in patterns)
        
        # Normalize confidence score
        if total_matches >= 3:
            return 0.9
        elif total_matches >= 2:
            return 0.8
        elif total_matches >= 1:
            return 0.7
        else:
            return 0.5
    
    def get_custom_prompt_template(self, query_type: QueryType) -> str:
        """Get custom prompt template based on query type"""
        
        templates = {
            QueryType.FACTUAL: """
            You are a precise factual assistant. Use the following context to answer the question accurately and concisely.
            
            Context: {context}
            
            Question: {question}
            
            Instructions:
            1. Provide direct, factual answers based only on the context
            2. If the exact answer isn't in the context, state what information is available
            3. Be concise and specific
            4. Cite sources when possible
            
            Answer:
            """,
            
            QueryType.ANALYTICAL: """
            You are an analytical assistant. Use the following context to provide a thoughtful analysis.
            
            Context: {context}
            
            Question: {question}
            
            Instructions:
            1. Analyze the information thoroughly
            2. Identify patterns, relationships, and implications
            3. Compare and contrast different viewpoints if present
            4. Provide reasoning for your conclusions
            5. Acknowledge limitations or areas of uncertainty
            
            Analysis:
            """,
            
            QueryType.SUMMARIZATION: """
            You are a summarization specialist. Use the following context to create a comprehensive summary.
            
            Context: {context}
            
            Question: {question}
            
            Instructions:
            1. Identify and present the main points clearly
            2. Organize information logically
            3. Include key details while maintaining conciseness
            4. Use bullet points or structure when appropriate
            5. Ensure completeness while avoiding redundancy
            
            Summary:
            """,
            
            QueryType.PROCEDURAL: """
            You are a step-by-step guide assistant. Use the following context to provide clear instructions.
            
            Context: {context}
            
            Question: {question}
            
            Instructions:
            1. Break down the process into clear, sequential steps
            2. Number or organize steps logically
            3. Include important details and warnings
            4. Mention prerequisites or requirements
            5. Provide examples when helpful
            
            Steps:
            """
        }
        
        return templates.get(query_type, templates[QueryType.FACTUAL])
    
    def validate_response_quality(self, response: str, query_analysis: Dict) -> Dict:
        """Validate response quality based on query type and complexity"""
        
        validation_result = {
            "is_valid": True,
            "quality_score": 0.8,
            "issues": [],
            "suggestions": []
        }
        
        query_type = query_analysis["type"]
        complexity = query_analysis["complexity"]
        
        # Basic validation checks
        if len(response.strip()) < 50:
            validation_result["issues"].append("Response too short")
            validation_result["quality_score"] -= 0.2
        
        if "I don't know" in response and len(response) < 100:
            validation_result["issues"].append("Response lacks detail")
            validation_result["quality_score"] -= 0.1
        
        # Type-specific validation
        if query_type == QueryType.PROCEDURAL:
            if not any(indicator in response.lower() for indicator in ['step', 'first', 'then', 'next', 'finally']):
                validation_result["issues"].append("Missing step-by-step structure")
                validation_result["quality_score"] -= 0.2
        
        elif query_type == QueryType.SUMMARIZATION:
            if not any(indicator in response.lower() for indicator in ['main', 'key', 'important', 'summary']):
                validation_result["issues"].append("Missing summary indicators")
                validation_result["quality_score"] -= 0.1
        
        # Complexity-based validation
        if complexity == QueryComplexity.COMPLEX and len(response.split()) < 100:
            validation_result["issues"].append("Response may be too brief for complex query")
            validation_result["quality_score"] -= 0.1
        
        # Set overall validity
        validation_result["is_valid"] = validation_result["quality_score"] > 0.5
        
        return validation_result