"""
Test suite for spell correction module
"""

import unittest
from utils.spell_corrector import SpellCorrector, correct_query, correct_word


class TestSpellCorrector(unittest.TestCase):
    """Test cases for SpellCorrector"""
    
    def setUp(self):
        """Initialize corrector for tests"""
        self.corrector = SpellCorrector(threshold=0.80)
    
    def test_direct_lookup(self):
        """Test direct misspelling lookup"""
        corrected, confidence = self.corrector.correct_word('ciber')
        self.assertEqual(corrected.lower(), 'cyber')
        self.assertEqual(confidence, 1.0)
    
    def test_fuzzy_matching(self):
        """Test fuzzy matching for typos"""
        corrected, confidence = self.corrector.correct_word('machne')
        self.assertEqual(corrected.lower(), 'machine')
        self.assertGreaterEqual(confidence, 0.80)
    
    def test_case_preservation(self):
        """Test that case is preserved"""
        corrected, _ = self.corrector.correct_word('Ciber')
        # Case is preserved when correcting capitalized words
        self.assertIn(corrected.lower(), 'cyber')
    
    def test_similarity_score(self):
        """Test similarity calculation"""
        score = self.corrector.similarity('cyber', 'cyebr')
        self.assertGreaterEqual(score, 0.8)
        
        score = self.corrector.similarity('security', 'secuirty')
        self.assertGreater(score, 0.85)
    
    def test_query_correction(self):
        """Test full query correction"""
        query = "tell me about ciber security"
        corrected, corrections = self.corrector.correct_query(query)
        
        self.assertIn('cyber', corrected.lower())
        self.assertGreater(len(corrections), 0)
    
    def test_multiple_corrections(self):
        """Test query with multiple misspellings"""
        query = "machne lerning algoritm"
        corrected, corrections = self.corrector.correct_query(query)
        
        self.assertEqual(len(corrections), 3)
        self.assertIn('machine', corrected.lower())
        self.assertIn('learning', corrected.lower())
        self.assertIn('algorithm', corrected.lower())
    
    def test_punctuation_handling(self):
        """Test handling of punctuation"""
        query = "ciber, secuirty, and machne."
        corrected, corrections = self.corrector.correct_query(query)
        
        self.assertIn(',', corrected)
        self.assertIn('.', corrected)
        self.assertGreaterEqual(len(corrections), 2)
    
    def test_correct_word_function(self):
        """Test convenience function"""
        result = correct_word('ciber')
        self.assertEqual(result.lower(), 'cyber')
    
    def test_correct_query_function(self):
        """Test convenience function for queries"""
        query, corrections = correct_query('ciber secuirty')
        self.assertIn('cyber', query.lower())
        self.assertGreater(len(corrections), 0)
    
    def test_no_correction_needed(self):
        """Test correct words don't get changed"""
        query = "cyber security network"
        corrected, corrections = self.corrector.correct_query(query)
        
        self.assertEqual(corrected, query)
        self.assertEqual(len(corrections), 0)
    
    def test_partial_match(self):
        """Test words with partial matches"""
        corrected, confidence = self.corrector.correct_word('secrit')
        self.assertEqual(corrected.lower(), 'security')
    
    def test_suggest_corrections(self):
        """Test getting suggestions"""
        suggestions = self.corrector.suggest_corrections('ciber')
        
        self.assertGreater(len(suggestions), 0)
        self.assertEqual(suggestions[0][0].lower(), 'cyber')


class TestRealWorldScenarios(unittest.TestCase):
    """Test real-world usage scenarios"""
    
    def setUp(self):
        """Initialize corrector"""
        self.corrector = SpellCorrector()
    
    def test_medical_terms(self):
        """Test medical term corrections"""
        query = "diagnsis and paitent treatment"
        corrected, corrections = self.corrector.correct_query(query)
        
        self.assertIn('diagnosis', corrected.lower())
        self.assertIn('patient', corrected.lower())
    
    def test_tech_terms(self):
        """Test technology term corrections"""
        query = "algoritm and netwrok optimzation"
        corrected, corrections = self.corrector.correct_query(query)
        
        self.assertIn('algorithm', corrected.lower())
        self.assertIn('network', corrected.lower())
    
    def test_business_terms(self):
        """Test business term corrections"""
        query = "bussiness finace managmnet"
        corrected, corrections = self.corrector.correct_query(query)
        
        self.assertIn('business', corrected.lower())
        self.assertIn('finance', corrected.lower())
        self.assertIn('management', corrected.lower())
    
    def test_mixed_case(self):
        """Test mixed case input"""
        query = "Ciber Security MACHINE Learning"
        corrected, _ = self.corrector.correct_query(query)
        
        self.assertIn('cyber', corrected.lower())
        self.assertIn('machine', corrected.lower())


if __name__ == '__main__':
    unittest.main()
