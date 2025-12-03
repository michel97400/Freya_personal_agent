#!/usr/bin/env python3
"""Test script pour Git push avec message personnalisé"""
from agent import FreyaAgentNL

agent = FreyaAgentNL()

print("=== Test 1: Push simple ===")
response = agent.respond("peut tu push mon projet vers le dépôt")
print(response)

print("\n=== Test 2: Push avec message personnalisé ===")
agent2 = FreyaAgentNL()  # Nouvelle instance pour nouvelle conversation
response = agent2.respond('fais un git push avec le message "Ajout outils web trafilatura"')
print(response)

print("\n✅ Tests terminés!")
