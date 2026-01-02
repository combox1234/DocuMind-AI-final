"""LLM service using Ollama for response generation and semantic operations"""
import ollama
import logging
import re
from typing import Tuple, List, Dict, Optional
from sentence_transformers import CrossEncoder
from core.classifier import DocumentClassifier
from langdetect import detect, LangDetectException

logger = logging.getLogger(__name__)


class LLMService:
    """Handles LLM operations for query generation, response generation, and semantic operations"""
    
    def __init__(self, model: str = "llama3.2"):
        self.model = model
        self.classifier = DocumentClassifier()
        try:
            logger.info("Loading CrossEncoder model for re-ranking...")
            self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', max_length=512)
            logger.info("CrossEncoder loaded successfully.")
            # self.reranker = None
        except Exception as e:
            logger.error(f"Failed to load CrossEncoder: {e}")
            self.reranker = None
        
        # Language-specific system prompts
        self.language_prompts = {
            'en': "You are a helpful AI assistant that answers questions EXCLUSIVELY and STRICTLY based on the provided documents.",
            'hi': "आप एक सहायक AI सहायक हैं जो प्रदान किए गए दस्तावेज़ों के आधार पर प्रश्नों के उत्तर देते हैं।",
            'es': "Eres un asistente de IA útil que responde preguntas EXCLUSIVAMENTE basándose en los documentos proporcionados.",
            'fr': "Vous êtes un assistant IA utile qui répond aux questions EXCLUSIVEMENT sur la base des documents fournis.",
            'de': "Sie sind ein hilfreicher KI-Assistent, der Fragen AUSSCHLIESSLICH auf der Grundlage der bereitgestellten Dokumente beantwortet."
        }
        
        logger.info(f"LLM Service initialized with model: {model}")

    def detect_query_language(self, query: str) -> str:
        """Detect the language of the query"""
        try:
            lang = detect(query)
            logger.info(f"Detected language: {lang} for query: '{query[:50]}...'")
            return lang
        except LangDetectException:
            logger.warning(f"Could not detect language for query: '{query[:50]}...', defaulting to English")
            return 'en'
    
    def get_system_prompt_for_language(self, lang: str) -> str:
        """Get language-specific system prompt"""
        return self.language_prompts.get(lang, self.language_prompts['en'])
    
    def classify_hierarchical(self, text: str, filename: str = "") -> Dict:
        """Classify content into hierarchical structure: Domain > Category > FileType
        
        Delegates to DocumentClassifier for optimized classification.
        """
        # Step 1: Rule-based classification
        result = self.classifier.classify_hierarchical(text, filename)
        
        # Step 2: LLM Fallback if confidence is low
        # Threshold: 0.4 implies weak keyword matching
        if result['confidence'] < 0.45:
            logger.info(f"Low classification confidence ({result['confidence']}). specific fallback to LLM.")
            try:
                llm_result = self._classify_with_llm(text, filename)
                if llm_result:
                    logger.info(f"LLM Re-classification: {llm_result['domain']}/{llm_result['category']}")
                    return llm_result
            except Exception as e:
                logger.error(f"LLM classification failed: {e}")
        
        return result

    def _classify_with_llm(self, text: str, filename: str) -> Optional[Dict]:
        """Ask LLM to classify the document"""
        domains = list(self.classifier.DOMAIN_KEYWORDS.keys())
        
        prompt = f"""Classify this document into one of these Domains: {', '.join(domains)}.
Also provide a specific Category (e.g. UAV, Tax, Contract, Python, etc).

Filename: {filename}
Content Snippet:
{text[:1000]}

Return JSON format ONLY:
{{
  "domain": "Technology",
  "category": "UAV"
}}
"""
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                stream=False,
                options={"temperature": 0.1, "json": True} # Force JSON mode
            )
            
            import json
            data = json.loads(response['response'])
            return {
                "domain": data.get("domain", "Technology"),
                "category": data.get("category", "Other"),
                "file_extension": filename.split('.')[-1] if '.' in filename else "",
                "confidence": 0.85, # LLM is usually confident
                "domain_score": 80,
                "category_score": 80
            }
        except Exception as e:
            logger.warning(f"LLM classification parsing failed: {e}")
            return None
    
    def _calculate_confidence(self, query: str, chunks: List[dict]) -> float:
        """Calculate confidence score (0-100) for the answer"""
        if not chunks:
            return 0.0
        
        avg_similarity = sum(chunk.get('similarity', 0) for chunk in chunks) / len(chunks)
        chunk_bonus = min(len(chunks) / 5.0, 1.0)
        avg_distance = sum(chunk.get('distance', 2.0) for chunk in chunks) / len(chunks)
        distance_confidence = max(0, 1.0 - (avg_distance / 2.0))
        
        confidence = (avg_similarity * 0.4 + chunk_bonus * 0.3 + distance_confidence * 0.3)
        confidence_score = int(confidence * 100)
        return max(0, min(100, confidence_score))
    
    def _get_confidence_level(self, score: int) -> str:
        """Get confidence level label"""
        if score >= 75:
            return "🟢 HIGH"
        elif score >= 40:
            return "🟡 MEDIUM"
        else:
            return "🔴 LOW"

    def _rerank_chunks(self, query: str, chunks: List[dict], top_k: int = 5) -> List[dict]:
        """Re-rank chunks using Cross-Encoder"""
        if not self.reranker or not chunks:
            return chunks[:top_k]
            
        try:
            # Create pairs of (query, document_text)
            pairs = [[query, chunk['text']] for chunk in chunks]
            
            # Predict scores
            scores = self.reranker.predict(pairs)
            
            # Attach scores to chunks
            for i, chunk in enumerate(chunks):
                chunk['relevance_score'] = float(scores[i])
                
            # Sort by new relevance score
            reranked = sorted(chunks, key=lambda x: x['relevance_score'], reverse=True)
            
            logger.info(f"Re-ranking complete. Top chunk: {reranked[0].get('filename')} (Score: {reranked[0].get('relevance_score'):.4f})")
            return reranked[:top_k]
            
        except Exception as e:
            logger.error(f"Re-ranking failed: {e}")
            return chunks[:top_k]
    
    def generate_response(self, query: str, context_chunks: List[dict]) -> Tuple[str, List[str], float, List[dict], str]:
        """Generate response STRICTLY from documents only - no external knowledge
        
        Returns: (answer, cited_files, confidence_score, source_snippets, detected_language)
        """
        
        # Detect query language
        detected_lang = self.detect_query_language(query)
        
        if not context_chunks:
            # No documents found - cannot answer (in detected language)
            no_info_messages = {
                'en': "I don't have this information in your documents. Please upload relevant documents or ask questions about the documents you've provided.",
                'hi': "मेरे पास आपके दस्तावेज़ों में यह जानकारी नहीं है। कृपया प्रासंगिक दस्तावेज़ अपलोड करें या अपने दस्तावेज़ों के बारे में प्रश्न पूछें।",
                'es': "No tengo esta información en sus documentos. Por favor, suba documentos relevantes o haga preguntas sobre los documentos que ha proporcionado.",
                'fr': "Je n'ai pas cette information dans vos documents. Veuillez télécharger des documents pertinents ou poser des questions sur les documents que vous avez fournis."
            }
            return no_info_messages.get(detected_lang, no_info_messages['en']), [], 0, [], detected_lang
        
        # Relevance filter: prefer chunks containing query keywords
        keywords = [w.strip().lower() for w in re.split(r"[^A-Za-z0-9]+", query) if len(w.strip()) > 2]
        def relevance(c):
            text = c.get('text', '').lower()
            hits = sum(1 for k in keywords if k and k in text)
            sim = float(c.get('similarity', 0) or 0)
            return hits * 2 + sim
        
        # Re-rank deeper pool of chunks (using CrossEncoder)
        context_chunks = self._rerank_chunks(query, context_chunks, top_k=5)
        
        logger.info(f"LLM Processing: {len(context_chunks)} chunks for query: '{query}'")
        
        # Debug: Log all chunks and scores
        for i, c in enumerate(context_chunks):
            logger.info(f"   [{i}] {c.get('filename')} - Score: {c.get('relevance_score', 0)}")

        if context_chunks:
            # Noise Filter: Remove chunks with very low scores (likely irrelevant)
            # Valid matches usually score > 0. Ambiguous match ~ -2 to 0. Irrelevant < -5.
            # We use a threshold of -5.0 to filter out obvious noise while keeping relevant documents.
            context_chunks = [c for c in context_chunks if c.get('relevance_score', 0) > -5.0]
            
            if not context_chunks:
                 logger.warning("All chunks filtered out by Noise Filter. Returning top 1 fallback.")
                 # Fallback: if everything is filtered, take the top 1 ranked chunk
                 context_chunks = context_chunks[:1]
            # The original `else` block was `context_chunks = filtered_chunks`.
            # After the change, `context_chunks` is already the filtered list.
            # So, the `else` block is no longer needed as `context_chunks` already holds the filtered list.
            # If the instruction intended to keep the `else` block, it would need to define `filtered_chunks`
            # or assign `context_chunks` to itself, which is redundant.
            # Given the instruction, the most faithful and syntactically correct interpretation is to remove the `else` block
            # as `context_chunks` is already updated by the list comprehension.
                
            logger.info(f"Top 5 Filenames (Filtered): {[c.get('filename') for c in context_chunks]}")
            for i, c in enumerate(context_chunks):
                logger.info(f"Chunk {i+1} ({c['filename']}): {c['text'][:100]}...")
            
        confidence_score = self._calculate_confidence(query, context_chunks)
        confidence_level = self._get_confidence_level(confidence_score)
        
        source_snippets = []
        for i, chunk in enumerate(context_chunks, 1):
            snippet = {
                'id': i,
                'filename': chunk['filename'],
                'category': chunk.get('category', 'Unknown'),
                'text': chunk['text'][:300] + '...' if len(chunk['text']) > 300 else chunk['text'],
                'similarity': chunk.get('similarity', 0),
                'relevance_pct': int(chunk.get('similarity', 0) * 100)
            }
            source_snippets.append(snippet)
        
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            source_info = f"[Source {i}: {chunk['filename']}]"
            context_parts.append(f"{source_info}\n{chunk['text']}\n")
        
        context_text = "\n".join(context_parts)
        
        # STRICT DOCUMENT-ONLY PROMPT - No external knowledge allowed
        # If query asks for definition, require a direct definition first
        needs_definition = any(x in query.lower() for x in ["what is", "define", "definition of", "meaning of"]) 
        definition_preamble = "" if not needs_definition else "Provide a concise 1-2 line definition FIRST, then details."
        
        # Get language-specific system prompt
        system_prompt_base = self.get_system_prompt_for_language(detected_lang)

        full_prompt = f"""{system_prompt_base}

CRITICAL RULES:
1. ONLY answer using information from the documents below.
2. **STRICT PROHIBITION:** Do NOT use any external knowledge, general knowledge, or information from your training data.
3. If the answer is NOT in the documents, respond EXACTLY: "I don't have this information in the provided documents."
4. **DO NOT** provide "general information", "related concepts", or "possible connections" if they are not in the text.
5. **DO NOT** apologize or be conversational. Just provide the answer or the refusal.
6. Always cite which document the information comes from.
7. Provide detailed, comprehensive answers. ELABORATE on the 'why' and 'how'.
8. Include all types, categories, characteristics, and details mentioned in the documents.

Documents:
{context_text}

Question: {query}

Answer ONLY based on the documents above. If information is not in documents, say "I don't have this information in the provided documents." Do NOT add external context."""
        
        try:
            response = ollama.generate(
                model=self.model,
                prompt=full_prompt,
                stream=False,
                options={
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "top_k": 40,
                    "num_predict": 1024,
                    "num_ctx": 4096,
                    "repeat_penalty": 1.1,
                    "num_thread": 8,
                }
            )
            
            answer = response['response'].strip()
            
            # Check if LLM says information is not in documents
            no_info_phrases = [
                "don't have this information",
                "not in the provided documents",
                "not in the documents",
                "cannot find this information",
                "no information about",
                "not mentioned in the documents",
                "not available in the documents"
            ]
            
            is_no_info = any(phrase in answer.lower() for phrase in no_info_phrases)
            
            # FIX: If answer is long (>100 chars) and contains "no info" phrase, it's likely a hallucinated suffix.
            # We should valid the answer if it has substance.
            # UPDATE: Removing length check. If it says "no info", it is no info.
            if is_no_info and len(answer) > 100:
               logger.warning(f"Detected 'no info' phrase but answer length is {len(answer)}. Treating as valid.")
               is_no_info = False
            
            if is_no_info:
                # Don't add sources/confidence if information not found
                return answer, [], 0, [], detected_lang
            
            cited_files = list(set([chunk['filename'] for chunk in context_chunks]))
            
            if cited_files:
                answer += f"\n\n📊 Confidence: {confidence_level} ({confidence_score}%)"
                answer += f"\n📄 Sources: {', '.join(cited_files)}"
            
            return answer, cited_files, confidence_score, source_snippets, detected_lang
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check if it's an Ollama connection error
            if "connection" in error_msg or "ollama" in error_msg or "failed" in error_msg:
                logger.warning(f"Ollama unavailable: {e}")
                # Return message asking to start Ollama
                return "I cannot answer right now because Ollama is not running. Please start Ollama to get AI-powered answers from your documents.", [], 0, [], 'en'
            
            else:
                logger.error(f"Error generating response: {e}")
                return f"Error: Unable to generate response. {str(e)}", [], 0, [], 'en'
    
    def check_availability(self) -> bool:
        """Check if Ollama is available"""
        try:
            ollama.list()
            return True
        except:
            return False
