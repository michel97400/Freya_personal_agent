#!/usr/bin/env python3
"""Test script pour Git push"""
from agent import FreyaAgentNL

agent = FreyaAgentNL()

print("=== Test: Push du projet ===")
response = agent.respond("peut tu push mon projet vers le dépôt")
print(response)
print("\n✅ Test terminé!")
