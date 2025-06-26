from typing import Dict, List, Optional, Tuple
import re
from dataclasses import dataclass
from enum import Enum

from langchain.schema import Document
from langchain_openai import ChatOpenAI

from utils.logger import logger
from utils.config import Config


class ConfidenceLevel(Enum):
    """Confidence levels for responses"""
    HIGH = "high"       # 0.8 - 1.0
    MEDIUM = "medium"   # 0.6 - 0.8
    LOW = "low"         # 0.4 - 0.6
    VERY_LOW = "very_low"  # 0.0 - 0.4


@dataclass
class QualityMetrics:
    """Quality assessment metrics for responses"""
    relevance_score: float
    completeness_score: float
    accuracy_score: float
    clarity_score: float
    source_quality: float
    overall_score: float
    confidence_level: ConfidenceLevel
    should_respond: bool
    issues: List[str]
    suggestions: List[str]


class QualityAssurance:
    """Ensure high-quality responses and honest uncertainty handling"""
    
    def __init__(self):
        self.config = Config()
        
        # Initialize evaluator LLM
        self.evaluator_llm = ChatOpenAI(
            openai_api_key=self.config.OPENAI_API_KEY,
            model_name="gpt-3.5-turbo",
            temperature=0.0,
            max_tokens=200
        )
        
        # Quality thresholds
        self.response_threshold = 0.6  # Minimum score to provide response
        self.uncertainty_threshold = 0.5  # Below this, express uncertainty
        
        # Pattern recognition for quality issues
        self.quality_patterns = self._initialize_quality_patterns()
    
    def assess_response_quality(self, query: str, response: str, 
                              source_documents: List[Document]) -> QualityMetrics:
        """Comprehensively assess response quality"""
        
        # Individual quality assessments
        relevance_score = self._assess_relevance(query, response)
        completeness_score = self._assess_completeness(query, response)
        accuracy_score = self._assess_accuracy(response, source_documents)
        clarity_score = self._assess_clarity(response)
        source_quality = self._assess_source_quality(source_documents, query)
        
        # Calculate overall score
        weights = {
            'relevance': 0.25,
            'completeness': 0.20,
            'accuracy': 0.25,
            'clarity': 0.15,
            'source_quality': 0.15
        }
        
        overall_score = (
            relevance_score * weights['relevance'] +
            completeness_score * weights['completeness'] +
            accuracy_score * weights['accuracy'] +
            clarity_score * weights['clarity'] +
            source_quality * weights['source_quality']
        )
        
        # Determine confidence level
        confidence_level = self._determine_confidence_level(overall_score)
        
        # Check if we should respond
        should_respond = overall_score >= self.response_threshold
        
        # Identify issues and suggestions
        issues, suggestions = self._identify_issues_and_suggestions(
            query, response, source_documents, overall_score
        )
        
        metrics = QualityMetrics(
            relevance_score=relevance_score,
            completeness_score=completeness_score,
            accuracy_score=accuracy_score,
            clarity_score=clarity_score,
            source_quality=source_quality,
            overall_score=overall_score,
            confidence_level=confidence_level,
            should_respond=should_respond,
            issues=issues,
            suggestions=suggestions
        )
        
        logger.info(f"Quality assessment: {overall_score:.2f}, {confidence_level.value}")
        return metrics
    
    def _assess_relevance(self, query: str, response: str) -> float:
        """Assess how relevant the response is to the query"""
        
        # Extract key terms from query
        query_terms = self._extract_key_terms(query.lower())
        response_lower = response.lower()
        
        # Check term overlap
        matching_terms = sum(1 for term in query_terms if term in response_lower)
        
        if not query_terms:
            return 0.7  # Default score if no key terms
        
        term_overlap_score = matching_terms / len(query_terms)
        
        # Check for direct question addressing
        question_indicators = ['?', 'what', 'how', 'why', 'when', 'where', 'who']
        has_question = any(indicator in query.lower() for indicator in question_indicators)
        
        addresses_question = 0.8
        if has_question:
            # Look for answer patterns
            answer_patterns = ['the answer is', 'because', 'due to', 'this means', 'as a result']
            if any(pattern in response_lower for pattern in answer_patterns):
                addresses_question = 1.0
            elif len(response) < 50:
                addresses_question = 0.5
        
        # Combine scores
        relevance_score = (term_overlap_score * 0.6) + (addresses_question * 0.4)
        
        return min(1.0, relevance_score)
    
    def _assess_completeness(self, query: str, response: str) -> float:
        """Assess how complete the response is"""
        
        # Length-based assessment
        response_length = len(response.split())
        
        if response_length < 20:
            length_score = 0.3
        elif response_length < 50:
            length_score = 0.6
        elif response_length < 100:
            length_score = 0.8
        else:
            length_score = 1.0
        
        # Check for incomplete response indicators
        incomplete_indicators = [
            'i don\'t have enough information',
            'more information needed',
            'cannot determine',
            'unclear from the context',
            'insufficient data'
        ]
        
        has_incomplete_indicators = any(
            indicator in response.lower() for indicator in incomplete_indicators
        )
        
        if has_incomplete_indicators:
            completeness_score = 0.4
        else:
            completeness_score = length_score
        
        # Check for conclusion or summary
        conclusion_indicators = ['in conclusion', 'to summarize', 'overall', 'in summary']
        has_conclusion = any(indicator in response.lower() for indicator in conclusion_indicators)
        
        if has_conclusion:
            completeness_score = min(1.0, completeness_score + 0.1)
        
        return completeness_score
    
    def _assess_accuracy(self, response: str, source_documents: List[Document]) -> float:
        """Assess response accuracy based on source documents"""
        
        if not source_documents:
            return 0.5  # Neutral score if no sources
        
        # Check if response contains information from sources
        source_content = ' '.join(doc.page_content.lower() for doc in source_documents)
        response_lower = response.lower()
        
        # Extract key facts from response
        response_facts = self._extract_key_facts(response_lower)
        
        if not response_facts:
            return 0.7  # Default if no specific facts found
        
        # Check fact alignment with sources
        supported_facts = 0
        for fact in response_facts:
            if any(word in source_content for word in fact.split()):
                supported_facts += 1
        
        accuracy_score = supported_facts / len(response_facts) if response_facts else 0.7
        
        # Penalty for obvious fabrication indicators
        fabrication_indicators = [
            'according to my knowledge',
            'based on my training',
            'i believe',
            'it is likely that'
        ]
        
        has_fabrication = any(indicator in response_lower for indicator in fabrication_indicators)
        if has_fabrication:
            accuracy_score *= 0.8
        
        return min(1.0, accuracy_score)
    
    def _assess_clarity(self, response: str) -> float:
        """Assess response clarity and readability"""
        
        # Check sentence structure
        sentences = response.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        # Optimal sentence length is 15-20 words
        if 10 <= avg_sentence_length <= 25:
            sentence_score = 1.0
        elif 5 <= avg_sentence_length <= 35:
            sentence_score = 0.8
        else:
            sentence_score = 0.6
        
        # Check for clear structure
        structure_indicators = [
            'first', 'second', 'third', 'finally',
            'however', 'therefore', 'moreover',
            'in addition', 'furthermore', 'consequently'
        ]
        
        has_structure = any(indicator in response.lower() for indicator in structure_indicators)
        structure_score = 1.0 if has_structure else 0.8
        
        # Check for jargon or complexity
        complex_words = ['subsequently', 'consequently', 'nevertheless', 'furthermore']
        complexity_penalty = sum(1 for word in complex_words if word in response.lower()) * 0.05
        
        clarity_score = (sentence_score * 0.6) + (structure_score * 0.4) - complexity_penalty
        
        return max(0.3, min(1.0, clarity_score))
    
    def _assess_source_quality(self, source_documents: List[Document], query: str) -> float:
        """Assess the quality and relevance of source documents"""
        
        if not source_documents:
            return 0.0
        
        query_terms = self._extract_key_terms(query.lower())
        
        # Assess each document
        document_scores = []
        
        for doc in source_documents:
            doc_content = doc.page_content.lower()
            
            # Check relevance to query
            matching_terms = sum(1 for term in query_terms if term in doc_content)
            relevance_score = matching_terms / len(query_terms) if query_terms else 0.5
            
            # Check document length (more content = potentially better)
            length_score = min(1.0, len(doc.page_content) / 1000)
            
            # Check for metadata quality
            metadata_score = 0.5
            if doc.metadata.get('source_file'):
                metadata_score += 0.2
            if doc.metadata.get('page') and doc.metadata.get('page') != 'N/A':
                metadata_score += 0.2
            if doc.metadata.get('file_type'):
                metadata_score += 0.1
            
            doc_score = (relevance_score * 0.5) + (length_score * 0.3) + (metadata_score * 0.2)
            document_scores.append(doc_score)
        
        # Return average document quality
        return sum(document_scores) / len(document_scores)
    
    def _determine_confidence_level(self, overall_score: float) -> ConfidenceLevel:
        """Determine confidence level based on overall score"""
        
        if overall_score >= 0.8:
            return ConfidenceLevel.HIGH
        elif overall_score >= 0.6:
            return ConfidenceLevel.MEDIUM
        elif overall_score >= 0.4:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    def _identify_issues_and_suggestions(self, query: str, response: str, 
                                       source_documents: List[Document], 
                                       overall_score: float) -> Tuple[List[str], List[str]]:
        """Identify quality issues and provide suggestions"""
        
        issues = []
        suggestions = []
        
        # Check for common issues
        if overall_score < 0.6:
            issues.append("Overall response quality is below threshold")
            suggestions.append("Consider rephrasing the query or uploading more relevant documents")
        
        if len(response.split()) < 30:
            issues.append("Response is very brief")
            suggestions.append("Ask for more detailed information or context")
        
        if not source_documents:
            issues.append("No source documents available")
            suggestions.append("Upload relevant documents to improve response quality")
        
        if "I don't know" in response or "I don't have" in response:
            issues.append("System expressing uncertainty")
            suggestions.append("Try a more specific question or upload additional documents")
        
        # Check for vague responses
        vague_indicators = ['maybe', 'possibly', 'might be', 'could be', 'seems like']
        if any(indicator in response.lower() for indicator in vague_indicators):
            issues.append("Response contains uncertainty indicators")
            suggestions.append("Look for more specific information in your documents")
        
        return issues, suggestions
    
    def generate_honest_response(self, original_response: str, quality_metrics: QualityMetrics) -> str:
        """Generate an honest response based on quality assessment"""
        
        if not quality_metrics.should_respond:
            return self._generate_uncertainty_response(quality_metrics)
        
        if quality_metrics.confidence_level == ConfidenceLevel.VERY_LOW:
            return self._add_uncertainty_disclaimer(original_response, quality_metrics)
        
        if quality_metrics.confidence_level == ConfidenceLevel.LOW:
            return self._add_confidence_indicator(original_response, quality_metrics)
        
        return original_response
    
    def _generate_uncertainty_response(self, quality_metrics: QualityMetrics) -> str:
        """Generate an honest uncertainty response"""
        
        base_response = "I don't have enough reliable information in the provided documents to answer this question confidently."
        
        if quality_metrics.issues:
            base_response += f"\n\nSpecific issues identified:\n"
            for issue in quality_metrics.issues[:3]:  # Limit to top 3 issues
                base_response += f"• {issue}\n"
        
        if quality_metrics.suggestions:
            base_response += f"\nSuggestions:\n"
            for suggestion in quality_metrics.suggestions[:2]:  # Limit to top 2 suggestions
                base_response += f"• {suggestion}\n"
        
        return base_response
    
    def _add_uncertainty_disclaimer(self, response: str, quality_metrics: QualityMetrics) -> str:
        """Add uncertainty disclaimer to response"""
        
        disclaimer = f"\n\n⚠️ **Confidence Level: {quality_metrics.confidence_level.value.title()}** - This response is based on limited information and may not be complete or fully accurate."
        
        return response + disclaimer
    
    def _add_confidence_indicator(self, response: str, quality_metrics: QualityMetrics) -> str:
        """Add confidence indicator to response"""
        
        confidence_text = f"\n\n📊 **Confidence Level: {quality_metrics.confidence_level.value.title()}** ({quality_metrics.overall_score:.1%})"
        
        return response + confidence_text
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text"""
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'what', 'how', 'when', 'where', 'why', 'who'}
        
        # Extract words (3+ characters, not stop words)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        key_terms = [word for word in words if word not in stop_words]
        
        return list(set(key_terms))  # Remove duplicates
    
    def _extract_key_facts(self, text: str) -> List[str]:
        """Extract key factual statements from text"""
        
        # Simple fact extraction based on sentence patterns
        sentences = text.split('.')
        facts = []
        
        fact_patterns = [
            r'\b\d+\b',  # Numbers
            r'\b(is|are|was|were)\s+\w+',  # "is/are/was/were" statements
            r'\b(contains|includes|has|have)\s+\w+',  # Possession statements
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Minimum length for a fact
                for pattern in fact_patterns:
                    if re.search(pattern, sentence):
                        facts.append(sentence)
                        break
        
        return facts[:5]  # Limit to top 5 facts
    
    def _initialize_quality_patterns(self) -> Dict:
        """Initialize patterns for quality detection"""
        
        return {
            'hedging': [
                r'\b(maybe|perhaps|possibly|might|could|seems|appears)\b',
                r'\b(i think|i believe|it seems|it appears)\b'
            ],
            'uncertainty': [
                r'\b(unclear|uncertain|unknown|unsure)\b',
                r'\b(don\'t know|not sure|can\'t tell)\b'
            ],
            'incomplete': [
                r'\b(more information|additional details|further context)\b',
                r'\b(need to know|would need|requires more)\b'
            ]
        }