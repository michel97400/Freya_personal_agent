"""
TRM Validator - Utilise DeepSeek R1 1.5B pour valider les appels d'outils
Architecture: LLM Groq → Plan → TRM Validation → Exécution
"""

from llama_cpp import Llama
import json
import os
import re

# Configuration du modèle
MODEL_PATH = os.path.join(os.path.dirname(__file__), "DeepSeek-R1-Distill-Qwen-1.5B-Q8_0.gguf")

# Chemins dangereux à bloquer
DANGEROUS_PATHS = [
    "C:\\Windows",
    "C:\\Program Files",
    "C:\\Program Files (x86)",
    "C:\\Users\\Default",
    "C:\\System32",
]

# Actions qui nécessitent validation TRM (seulement si règles passent)
TRM_VALIDATED_ACTIONS = ["modify_file", "git_push"]  # delete_path géré par règles

# Actions dangereuses qui nécessitent une attention particulière
HIGH_RISK_ACTIONS = ["delete_path", "modify_file", "git_push", "git_workflow"]

class TRMValidator:
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.llm = None
        self._load_model()
    
    def _load_model(self):
        """Charge le modèle TRM."""
        if not self.enabled:
            print("⚠️ TRM Validator désactivé")
            return
        
        if not os.path.exists(MODEL_PATH):
            print(f"⚠️ Modèle TRM non trouvé: {MODEL_PATH}")
            print("   Le validateur fonctionnera en mode règles uniquement.")
            return
        
        try:
            print("🧠 Chargement du TRM (DeepSeek R1 1.5B)...")
            self.llm = Llama(
                model_path=MODEL_PATH,
                n_ctx=1024,      # Contexte réduit pour la validation
                n_threads=4,
                n_gpu_layers=0,  # CPU pour l'instant
                verbose=False
            )
            print("✅ TRM chargé avec succès")
        except Exception as e:
            print(f"⚠️ Erreur chargement TRM: {e}")
            self.llm = None
    
    def validate(self, tool_name: str, arguments: dict, user_request: str) -> dict:
        """
        Valide un appel d'outil avant exécution.
        
        Returns:
            {
                "approved": bool,
                "reason": str,
                "modified_args": dict | None,  # Arguments corrigés si nécessaire
                "warnings": list[str]
            }
        """
        result = {
            "approved": True,
            "reason": "",
            "modified_args": None,
            "warnings": []
        }
        
        # 1. Validation par règles (rapide, sans LLM)
        rule_check = self._check_rules(tool_name, arguments)
        if not rule_check["approved"]:
            return rule_check
        
        result["warnings"].extend(rule_check.get("warnings", []))
        
        # 2. Validation par TRM (si disponible et action sensible)
        if self.llm and tool_name in TRM_VALIDATED_ACTIONS:
            trm_check = self._validate_with_trm(tool_name, arguments, user_request)
            if not trm_check["approved"]:
                return trm_check
            result["warnings"].extend(trm_check.get("warnings", []))
        
        return result
    
    def _check_rules(self, tool_name: str, arguments: dict) -> dict:
        """Validation par règles statiques (rapide)."""
        result = {"approved": True, "reason": "", "warnings": []}
        
        # Vérifier les chemins dangereux
        path_args = ["path", "filename", "target_path"]
        for arg in path_args:
            if arg in arguments:
                path = arguments[arg]
                if isinstance(path, str):
                    # Normaliser le chemin
                    norm_path = os.path.normpath(path).upper()
                    
                    # Vérifier les chemins système
                    for dangerous in DANGEROUS_PATHS:
                        if norm_path.startswith(dangerous.upper()):
                            result["approved"] = False
                            result["reason"] = f"🚫 BLOQUÉ: Chemin système protégé ({dangerous})"
                            return result
                    
                    # Avertissement pour chemins sensibles
                    if "WINDOWS" in norm_path or "SYSTEM32" in norm_path:
                        result["warnings"].append(f"⚠️ Attention: chemin sensible détecté ({path})")
        
        # Vérifier delete_path
        if tool_name == "delete_path":
            path = arguments.get("path", "")
            if path in [".", "/", "\\", "C:\\", "D:\\"]:
                result["approved"] = False
                result["reason"] = "🚫 BLOQUÉ: Tentative de suppression de la racine"
                return result
            
            # Avertir pour les suppressions de dossiers
            if os.path.isdir(path):
                result["warnings"].append(f"⚠️ Suppression d'un dossier: {path}")
        
        # Vérifier write_file sur fichiers de code existants (DANGEREUX - écrase!)
        if tool_name == "write_file":
            filename = arguments.get("filename", "")
            code_extensions = [".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".cs", ".go", ".rs", ".rb", ".php"]
            is_code_file = any(filename.endswith(ext) for ext in code_extensions)
            file_exists = os.path.exists(filename)
            
            if is_code_file and file_exists:
                result["approved"] = False
                result["reason"] = f"🚫 BLOQUÉ: write_file sur fichier de code existant '{filename}'. Utilise modify_file avec action='append' pour ajouter du code!"
                return result
        
        # Vérifier git_push (pas de push sur main sans confirmation)
        if tool_name == "git_push":
            branch = arguments.get("branch", "main")
            if branch == "main":
                result["warnings"].append("⚠️ Push sur la branche main")
        
        # Vérifier les arguments requis
        required_args = {
            "write_file": ["filename", "content"],
            "read_file": ["filename"],
            "delete_path": ["path"],
            "create_folder": ["path"],
            "modify_file": ["filename", "replacement_text"],  # search_text peut être vide pour append
        }
        
        if tool_name in required_args:
            for req in required_args[tool_name]:
                if req not in arguments or not arguments[req]:
                    result["approved"] = False
                    result["reason"] = f"🚫 Argument manquant: {req}"
                    return result
        
        return result
    
    def _validate_with_trm(self, tool_name: str, arguments: dict, user_request: str) -> dict:
        """Validation avec le modèle TRM (pour actions sensibles)."""
        result = {"approved": True, "reason": "", "warnings": []}
        
        # Construire le prompt de validation
        prompt = f"""Validate this action:
User request: "{user_request}"
Tool: {tool_name}
Arguments: {json.dumps(arguments, ensure_ascii=False)}

Is this action safe and matches the user request? Answer ONLY with:
APPROVED - if action is safe and correct
REJECTED: <reason> - if action should be blocked
WARNING: <message> - if action needs attention but can proceed

Answer:"""

        try:
            response = self.llm(
                prompt,
                max_tokens=100,
                temperature=0.1,
                stop=["\\n\\n", "User:", "Validate", "<think>", "</think>"]
            )
            
            output = response["choices"][0]["text"].strip()
            
            # Nettoyer la sortie du modèle (enlever les balises think)
            if "<think>" in output.lower():
                output = output.split("</think>")[-1].strip()
            output = output.upper()
            
            if "REJECTED" in output:
                result["approved"] = False
                # Extraire la raison après REJECTED
                reason_part = output.split("REJECTED")[-1].replace(":", "").strip()
                result["reason"] = reason_part if reason_part else "Action rejetée par TRM"
            elif "WARNING" in output:
                warning_part = output.split("WARNING")[-1].replace(":", "").strip()
                result["warnings"].append(warning_part if warning_part else "Attention requise")
            # APPROVED ou autre = approuvé
            
        except Exception as e:
            # En cas d'erreur TRM, on laisse passer avec warning
            result["warnings"].append(f"⚠️ Validation TRM échouée: {e}")
        
        return result
    
    def validate_plan(self, plan: dict, user_request: str) -> dict:
        """
        Valide un plan d'exécution complet AVANT que Groq ne l'exécute.
        
        Args:
            plan: {
                "steps": [
                    {"action": "list_files", "args": {"path": "..."}},
                    {"action": "delete_path", "args": {"path": "..."}},
                    ...
                ],
                "summary": "Description du plan"
            }
            user_request: La requête originale de l'utilisateur
        
        Returns:
            {
                "approved": bool,
                "corrected_plan": dict | None,  # Plan corrigé si nécessaire
                "blocked_steps": list,  # Étapes bloquées avec raison
                "warnings": list[str],
                "feedback": str  # Message à renvoyer à Groq
            }
        """
        result = {
            "approved": True,
            "corrected_plan": None,
            "blocked_steps": [],
            "warnings": [],
            "feedback": ""
        }
        
        if not plan or "steps" not in plan:
            result["approved"] = False
            result["feedback"] = "Plan invalide: format incorrect. Le plan doit contenir 'steps'."
            return result
        
        corrected_steps = []
        
        for i, step in enumerate(plan.get("steps", [])):
            action = step.get("action", "")
            args = step.get("args", {})
            
            # Valider chaque étape avec les règles
            step_validation = self._check_rules(action, args)
            
            if not step_validation["approved"]:
                result["blocked_steps"].append({
                    "step": i + 1,
                    "action": action,
                    "reason": step_validation["reason"]
                })
                result["approved"] = False
            else:
                # Étape valide, l'ajouter au plan corrigé
                corrected_steps.append(step)
                result["warnings"].extend(step_validation.get("warnings", []))
        
        # Si actions sensibles, valider avec TRM
        has_high_risk = any(
            step.get("action") in HIGH_RISK_ACTIONS 
            for step in plan.get("steps", [])
        )
        
        if self.llm and has_high_risk and result["approved"]:
            trm_validation = self._validate_plan_with_trm(plan, user_request)
            if not trm_validation["approved"]:
                result["approved"] = False
                result["feedback"] = trm_validation.get("feedback", "Plan rejeté par TRM")
            else:
                result["warnings"].extend(trm_validation.get("warnings", []))
                if trm_validation.get("suggestions"):
                    result["feedback"] = trm_validation["suggestions"]
        
        # Construire le plan corrigé
        if corrected_steps:
            result["corrected_plan"] = {
                "steps": corrected_steps,
                "summary": plan.get("summary", "Plan corrigé")
            }
        
        # Construire le feedback pour Groq
        if result["blocked_steps"]:
            blocked_msg = "\n".join([
                f"  ❌ Étape {b['step']} ({b['action']}): {b['reason']}"
                for b in result["blocked_steps"]
            ])
            result["feedback"] = f"⚠️ PLAN PARTIELLEMENT REJETÉ:\n{blocked_msg}\n\nPlan corrigé disponible avec {len(corrected_steps)} étapes valides."
        elif result["warnings"]:
            result["feedback"] = "✅ Plan validé avec avertissements:\n" + "\n".join(result["warnings"])
        else:
            result["feedback"] = "✅ Plan validé - Prêt pour exécution"
        
        return result
    
    def _validate_plan_with_trm(self, plan: dict, user_request: str) -> dict:
        """Validation du plan complet avec TRM."""
        result = {"approved": True, "warnings": [], "suggestions": "", "feedback": ""}
        
        # Construire un résumé du plan pour le TRM
        steps_summary = "\n".join([
            f"{i+1}. {s.get('action')}({json.dumps(s.get('args', {}), ensure_ascii=False)[:100]})"
            for i, s in enumerate(plan.get("steps", []))
        ])
        
        prompt = f"""Analyze this execution plan:
User request: "{user_request}"

Plan steps:
{steps_summary}

Validate:
1. Does the plan match the user's intent?
2. Is the order of steps correct?
3. Are there any security risks?

Answer with ONE line:
APPROVED - if plan is correct
REJECTED: <reason> - if plan should be blocked
SUGGEST: <improvement> - if plan can be improved

Answer:"""

        try:
            response = self.llm(
                prompt,
                max_tokens=150,
                temperature=0.1,
                stop=["\n\n", "User:", "Analyze", "<think>"]
            )
            
            output = response["choices"][0]["text"].strip()
            
            # Nettoyer
            if "<think>" in output.lower():
                output = output.split("</think>")[-1].strip()
            
            output_upper = output.upper()
            
            if "REJECTED" in output_upper:
                result["approved"] = False
                result["feedback"] = output.split("REJECTED")[-1].replace(":", "").strip()
            elif "SUGGEST" in output_upper:
                result["suggestions"] = output.split("SUGGEST")[-1].replace(":", "").strip()
            
        except Exception as e:
            result["warnings"].append(f"⚠️ Validation TRM plan échouée: {e}")
        
        return result
    
    def format_validation_result(self, result: dict) -> str:
        """Formate le résultat de validation pour affichage."""
        if not result["approved"]:
            return f"❌ {result['reason']}"
        
        output = "✅ Action validée"
        if result["warnings"]:
            output += "\\n" + "\\n".join(result["warnings"])
        
        return output


# Instance globale du validateur
_validator = None

def get_validator(enabled=True) -> TRMValidator:
    """Retourne l'instance globale du validateur TRM."""
    global _validator
    if _validator is None:
        _validator = TRMValidator(enabled=enabled)
    return _validator


def validate_tool_call(tool_name: str, arguments: dict, user_request: str = "") -> dict:
    """
    Fonction utilitaire pour valider un appel d'outil.
    
    Usage:
        result = validate_tool_call("delete_path", {"path": "C:/Windows"}, "supprime windows")
        if not result["approved"]:
            print(result["reason"])
    """
    validator = get_validator()
    return validator.validate(tool_name, arguments, user_request)


# Test du module
if __name__ == "__main__":
    print("=" * 50)
    print("🧪 Test du TRM Validator")
    print("=" * 50)
    
    validator = TRMValidator(enabled=True)
    
    # Tests de validation
    test_cases = [
        # (tool_name, arguments, user_request, expected_approved)
        ("write_file", {"filename": "test.py", "content": "print('hello')"}, "crée un fichier test", True),
        ("delete_path", {"path": "C:\\Windows\\System32"}, "supprime system32", False),
        ("delete_path", {"path": "C:\\Users\\Payet\\Desktop\\test.txt"}, "supprime test.txt", True),
        ("delete_path", {"path": "C:\\"}, "supprime tout", False),
        ("read_file", {"filename": "agent.py"}, "lis agent.py", True),
        ("read_file", {}, "lis un fichier", False),  # Argument manquant
        ("git_push", {"branch": "main"}, "push sur main", True),  # Warning attendu
    ]
    
    for tool_name, args, request, expected in test_cases:
        print(f"\n📋 Test: {tool_name}({args})")
        print(f"   Requête: \"{request}\"")
        
        result = validator.validate(tool_name, args, request)
        status = "✅" if result["approved"] == expected else "❌ ÉCHEC"
        
        print(f"   Résultat: {status}")
        if not result["approved"]:
            print(f"   Raison: {result['reason']}")
        if result["warnings"]:
            for w in result["warnings"]:
                print(f"   {w}")
    
    # ========================================
    # Tests de validation de PLANS
    # ========================================
    print("\n" + "=" * 50)
    print("🧪 Test de validation de PLANS")
    print("=" * 50)
    
    plan_test_cases = [
        # Plan valide simple
        {
            "name": "Plan valide - liste fichiers",
            "plan": {
                "summary": "Lister le bureau",
                "steps": [
                    {"action": "list_files", "args": {"path": "C:\\Users\\Payet\\Desktop"}}
                ]
            },
            "request": "liste moi le bureau",
            "expected_approved": True
        },
        # Plan avec chemin système (doit être bloqué)
        {
            "name": "Plan dangereux - suppression Windows",
            "plan": {
                "summary": "Suppression système",
                "steps": [
                    {"action": "delete_path", "args": {"path": "C:\\Windows\\System32"}}
                ]
            },
            "request": "supprime system32",
            "expected_approved": False
        },
        # Plan mixte (certaines étapes valides, d'autres non)
        {
            "name": "Plan mixte - partiellement valide",
            "plan": {
                "summary": "Nettoyage",
                "steps": [
                    {"action": "list_files", "args": {"path": "C:\\Users\\Payet\\Desktop"}},
                    {"action": "delete_path", "args": {"path": "C:\\Windows"}},
                    {"action": "delete_path", "args": {"path": "C:\\Users\\Payet\\Desktop\\temp.txt"}}
                ]
            },
            "request": "nettoie mon pc",
            "expected_approved": False  # Car contient une étape dangereuse
        },
        # Plan sans steps (invalide)
        {
            "name": "Plan invalide - pas de steps",
            "plan": {"summary": "Plan vide"},
            "request": "fais quelque chose",
            "expected_approved": False
        },
    ]
    
    for test in plan_test_cases:
        print(f"\n📋 Test Plan: {test['name']}")
        print(f"   Requête: \"{test['request']}\"")
        
        result = validator.validate_plan(test["plan"], test["request"])
        status = "✅" if result["approved"] == test["expected_approved"] else "❌ ÉCHEC"
        
        print(f"   Résultat: {status}")
        print(f"   Feedback: {result['feedback'][:100]}...")
        
        if result["blocked_steps"]:
            print(f"   Étapes bloquées: {len(result['blocked_steps'])}")
            for b in result["blocked_steps"]:
                print(f"      - Étape {b['step']}: {b['reason']}")
        
        if result["corrected_plan"]:
            print(f"   Plan corrigé: {len(result['corrected_plan']['steps'])} étapes")
    
    print("\n" + "=" * 50)
    print("✅ Tests terminés!")
