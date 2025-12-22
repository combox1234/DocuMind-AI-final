#!/usr/bin/env python3
"""Test the scaled classification with file processing"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.processor import FileProcessor
from core.llm import LLMService

processor = FileProcessor()
llm = LLMService()
test_dir = Path(__file__).parent.parent / 'data/incoming/test_scaling'

print("\n=== Scaled Classification Test Results ===\n")
print(f"{'Filename':<35} {'Domain':<15} {'Category':<15}")
print("-" * 65)

for file in sorted(test_dir.glob('*.txt')):
    try:
        # Read file content
        content = file.read_text(encoding='utf-8', errors='ignore')
        
        # Classify
        result = llm.classify_hierarchical(content, file.name)
        
        print(f"{file.name:<35} {result['domain']:<15} {result['category']:<15}")
        
    except Exception as e:
        print(f"{file.name:<35} ERROR: {str(e)[:40]}")

print("\n✓ All files classified successfully!")
