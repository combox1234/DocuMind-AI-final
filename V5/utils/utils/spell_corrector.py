"""
Spell Corrector Module
Handles fuzzy matching and spell correction for user queries and document classification.
Corrects typos like "ciber" → "cyber", "machne" → "machine", etc.
"""

from difflib import SequenceMatcher
import re
from typing import Tuple, List, Optional


class SpellCorrector:
    """
    Corrects spelling errors in user queries and category names.
    Uses fuzzy matching with configurable threshold.
    """
    
    # Dictionary of common terms in the knowledge base
    KNOWLEDGE_BASE_TERMS = {
        # Technology & Security
        'cyber': ['ciber', 'cybr', 'cybe'],
        'security': ['secuirty', 'securty', 'secrity', 'securuty'],
        'machine': ['machne', 'machin', 'mashcine'],
        'learning': ['lerning', 'learnng', 'learing'],
        'neural': ['neoral', 'nueral', 'neural'],
        'network': ['netork', 'netwrok', 'netwrk'],
        'database': ['databse', 'datbase', 'databas'],
        'security': ['secuirty', 'securty', 'secrity'],
        'algorithm': ['algoritm', 'algorithn', 'algortithm'],
        'encryption': ['encrypton', 'encription', 'encrypion'],
        
        # Document Types
        'document': ['docment', 'documnt', 'documet'],
        'architecture': ['architecure', 'arquitecture', 'architeure'],
        'optimization': ['optimzation', 'optimisation', 'optimztion'],
        'classification': ['clasification', 'classificaion', 'clasiffication'],
        'processing': ['procesing', 'proceessing', 'proceessing'],
        
        # Medical Terms
        'medical': ['medicl', 'medcal', 'medicail'],
        'healthcare': ['helathcare', 'healthcaree', 'healthecare'],
        'diagnosis': ['diagnsis', 'diagnois', 'diagnsis'],
        'treatment': ['treatmnt', 'treament', 'treatement'],
        'patient': ['paitent', 'patinet', 'patiuent'],
        
        # Business Terms
        'business': ['bussiness', 'bussines', 'bisness'],
        'finance': ['finace', 'finnance', 'finannce'],
        'management': ['managmnet', 'managemetn', 'managment'],
        'analysis': ['analisis', 'analisys', 'analysys'],
        
        # Research Terms
        'research': ['reserch', 'reseach', 'reserarch'],
        'experiment': ['experment', 'experiement', 'experimet'],
        'hypothesis': ['hypothsis', 'hypothess', 'hipothesis'],
        'methodology': ['metodology', 'methodolgy', 'metholodogy'],
        
        # Programming Terms
        'programming': ['programing', 'programm', 'programmin'],
        'software': ['sofware', 'softwar', 'softwre'],
        'development': ['developmnt', 'developement', 'develpment'],
        'framework': ['framwork', 'framewrok', 'framwework'],
        'library': ['libary', 'libray', 'libarary'],
        'debugging': ['debuging', 'debuggng', 'debuggin'],
        
        # General Terms
        'system': ['systm', 'sytem', 'systrm'],
        'analysis': ['analisis', 'analisys', 'analysys'],
        'performance': ['perfomance', 'performence', 'performence'],
        'quality': ['qualiy', 'qualty', 'qualitty'],
        'maintenance': ['maintenence', 'maintenence', 'maintanence'],
    }
    
    # Common misspellings dictionary (reverse mapping)
    MISSPELLINGS = {}
    
    def __init__(self, threshold: float = 0.80):
        """
        Initialize spell corrector.
        
        Args:
            threshold: Similarity threshold (0-1) for accepting corrections
                      0.80 means 80% similarity required
        """
        self.threshold = threshold
        self._build_misspellings_index()
    
    def _build_misspellings_index(self):
        """Build reverse index for fast lookup of misspellings."""
        for correct_word, misspellings in self.KNOWLEDGE_BASE_TERMS.items():
            for misspelled in misspellings:
                self.MISSPELLINGS[misspelled.lower()] = correct_word.lower()
    
    def similarity(self, word1: str, word2: str) -> float:
        """
        Calculate similarity between two words (0-1).
        
        Args:
            word1: First word
            word2: Second word
            
        Returns:
            Similarity score (0 = no match, 1 = perfect match)
        """
        word1 = word1.lower().strip()
        word2 = word2.lower().strip()
        
        if word1 == word2:
            return 1.0
        
        return SequenceMatcher(None, word1, word2).ratio()
    
    def correct_word(self, word: str) -> Tuple[str, float]:
        """
        Correct a single misspelled word.
        
        Args:
            word: The word to correct
            
        Returns:
            Tuple of (corrected_word, confidence_score)
        """
        word_lower = word.lower().strip()
        
        # Direct lookup in misspellings dictionary
        if word_lower in self.MISSPELLINGS:
            return self.MISSPELLINGS[word_lower], 1.0
        
        # Fuzzy matching against known terms
        best_match = word
        best_score = 0.0
        
        for correct_word in self.KNOWLEDGE_BASE_TERMS.keys():
            score = self.similarity(word_lower, correct_word)
            
            if score > best_score and score >= self.threshold:
                best_score = score
                best_match = correct_word
        
        # Preserve original case
        if best_match != word and best_score > 0:
            if word[0].isupper():
                best_match = best_match.capitalize()
        
        return best_match, best_score
    
    def correct_query(self, query: str) -> Tuple[str, List[Tuple[str, str, float]]]:
        """
        Correct spelling errors in entire user query.
        
        Args:
            query: User input query with potential spelling errors
            
        Returns:
            Tuple of (corrected_query, list_of_corrections)
            where each correction is (original_word, corrected_word, confidence)
        """
        # Split query into words while preserving punctuation
        words = query.split()
        corrected_words = []
        corrections = []
        
        for word in words:
            # Separate punctuation
            punctuation = ''
            clean_word = word
            
            while clean_word and not clean_word[-1].isalnum():
                punctuation = clean_word[-1] + punctuation
                clean_word = clean_word[:-1]
            
            while clean_word and not clean_word[0].isalnum():
                punctuation = clean_word[0] + punctuation
                clean_word = clean_word[1:]
            
            if clean_word:
                corrected, confidence = self.correct_word(clean_word)
                
                # Only record if correction was made
                if corrected.lower() != clean_word.lower() and confidence >= self.threshold:
                    corrections.append((clean_word, corrected, confidence))
                
                corrected_words.append(corrected + punctuation)
            else:
                corrected_words.append(word)
        
        corrected_query = ' '.join(corrected_words)
        return corrected_query, corrections
    
    def suggest_corrections(self, text: str, top_n: int = 5) -> List[Tuple[str, float]]:
        """
        Suggest possible corrections for ambiguous words.
        
        Args:
            text: Input text
            top_n: Number of suggestions to return
            
        Returns:
            List of (suggestion, confidence) tuples
        """
        words = text.lower().split()
        suggestions = []
        
        for word in words:
            clean_word = re.sub(r'[^a-z0-9]', '', word)
            
            if clean_word:
                scores = {}
                for correct_word in self.KNOWLEDGE_BASE_TERMS.keys():
                    score = self.similarity(clean_word, correct_word)
                    if score >= (self.threshold - 0.1):  # Slightly lower threshold for suggestions
                        scores[correct_word] = score
                
                # Sort by score and return top N
                sorted_suggestions = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                suggestions.extend(sorted_suggestions[:top_n])
        
        # Remove duplicates and sort
        unique_suggestions = {}
        for word, score in suggestions:
            if word not in unique_suggestions or score > unique_suggestions[word]:
                unique_suggestions[word] = score
        
        return sorted(unique_suggestions.items(), key=lambda x: x[1], reverse=True)[:top_n]


# Singleton instance for easy access
_corrector = None

def get_corrector(threshold: float = 0.80) -> SpellCorrector:
    """Get or create the spell corrector instance."""
    global _corrector
    if _corrector is None:
        _corrector = SpellCorrector(threshold=threshold)
    return _corrector


def correct_query(query: str) -> Tuple[str, List[Tuple[str, str, float]]]:
    """
    Convenience function to correct query spelling.
    
    Args:
        query: User input query
        
    Returns:
        Tuple of (corrected_query, corrections_made)
    """
    corrector = get_corrector()
    return corrector.correct_query(query)


def correct_word(word: str) -> str:
    """
    Convenience function to correct single word.
    
    Args:
        word: Word to correct
        
    Returns:
        Corrected word
    """
    corrector = get_corrector()
    corrected, _ = corrector.correct_word(word)
    return corrected
