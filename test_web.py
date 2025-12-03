#!/usr/bin/env python3
"""Test script pour les outils web avec trafilatura"""
from tools import search_web, fetch_webpage, search_and_summarize

# Test 1: Recherche web simple
print("=== Test 1: Recherche 'Python trafilatura' ===")
result = search_web("Python trafilatura", 3)
print(result)

# Test 2: Récupérer le contenu d'une page
print("\n=== Test 2: Fetch github.com ===")
result = fetch_webpage("https://github.com")
print(result[:500] + "..." if len(result) > 500 else result)

# Test 3: Recherche et résumé
print("\n=== Test 3: Recherche et résumé 'machine learning' ===")
result = search_and_summarize("machine learning introduction")
print(result[:500] + "..." if len(result) > 500 else result)

print("\n✅ Tests web terminés!")
