#!/usr/bin/env python3
"""Quick test to verify file sorting/categorization logic"""
from core.llm import LLMService
from pathlib import Path

llm = LLMService()

# Test files
test_files = {
    'test_python_code.py': 'Code',
    'test_business_strategy.txt': 'Business',
    'test_api_documentation.md': 'Documentation'
}

print("\n" + "="*60)
print("FILE CATEGORIZATION TEST")
print("="*60 + "\n")

for filename, expected_category in test_files.items():
    filepath = Path('data/incoming') / filename
    
    if not filepath.exists():
        print(f"❌ {filename}: FILE NOT FOUND")
        continue
    
    # Read file content
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Get category from LLM classifier
    category = llm.classify_content(content)
    
    status = "✅" if category == expected_category else "⚠️"
    print(f"{status} {filename}")
    print(f"   Expected: {expected_category}")
    print(f"   Got: {category}")
    print(f"   Match: {category == expected_category}\n")

print("="*60)
print("✅ Test Complete")
print("="*60 + "\n")
