"""
Test du workflow complet: Groq → Plan → TRM → Exécution
"""
from agent import FreyaAgentNL

def test_workflow():
    print("=" * 60)
    print("🧪 TEST DU WORKFLOW AVEC PLANIFICATION TRM")
    print("=" * 60)
    
    freya = FreyaAgentNL()
    
    # Tests à exécuter
    test_cases = [
        # Test 1: Suppression simple (devrait passer par le plan)
        "supprime le fichier test_delete_me.txt sur le bureau",
        
        # Test 2: Listing (workflow standard, pas de plan)
        "liste les fichiers du bureau",
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"📝 TEST {i}: {test}")
        print("="*60)
        
        try:
            response = freya.respond(test)
            print(f"\n📤 RÉPONSE:\n{response[:500]}...")
        except Exception as e:
            print(f"❌ ERREUR: {e}")
        
        print("\n" + "-"*60)
    
    print("\n✅ Tests terminés!")

if __name__ == "__main__":
    test_workflow()
