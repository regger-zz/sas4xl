#!/usr/bin/env python3
"""SAS to Python translator with intelligent routing"""

import subprocess
import sys
import re

# ============================================================
# PATTERN DETECTOR (Your logic from simple_parser.py)
# ============================================================

def detect_sas_patterns(sas_code: str) -> dict:
    """Detect patterns and return routing decision"""
    
    flags = {
        "RETAIN": False,
        "BY": False,
        "FIRST_LAST": False,
        "ARRAY": False,
        "MACRO": False,
        "COMPLEXITY_SCORE": 0
    }
    
    if re.search(r'\bretain\b', sas_code, re.IGNORECASE):
        flags["RETAIN"] = True
        flags["COMPLEXITY_SCORE"] += 2
    
    if re.search(r'\bby\s+\w+', sas_code, re.IGNORECASE):
        flags["BY"] = True
        flags["COMPLEXITY_SCORE"] += 1
    
    if re.search(r'\bfirst\.\w+|\blast\.\w+', sas_code, re.IGNORECASE):
        flags["FIRST_LAST"] = True
        flags["COMPLEXITY_SCORE"] += 2
    
    if re.search(r'\barray\b', sas_code, re.IGNORECASE):
        flags["ARRAY"] = True
        flags["COMPLEXITY_SCORE"] += 3
    
    if re.search(r'%', sas_code):
        flags["MACRO"] = True
        flags["COMPLEXITY_SCORE"] += 2
    
    # Routing decision
    if flags["RETAIN"] and flags["BY"] and flags["FIRST_LAST"]:
        flags["ROUTING"] = "MANUAL_REVIEW"
        flags["REASON"] = "Complex RETAIN+BY+FIRST pattern"
    elif flags["RETAIN"] and flags["BY"]:
        flags["ROUTING"] = "CAUTION"
        flags["REASON"] = "RETAIN with BY (no FIRST) - attempt with caution"
    elif flags["COMPLEXITY_SCORE"] >= 3:
        flags["ROUTING"] = "CAUTION"
        flags["REASON"] = f"Multiple patterns detected (score {flags['COMPLEXITY_SCORE']})"
    else:
        flags["ROUTING"] = "AUTO_LLM"
        flags["REASON"] = "Simple pattern - safe for auto-translation"
    
    return flags

# ============================================================
# LLM TRANSLATOR (Only for AUTO_LLM or CAUTION routes)
# ============================================================

def translate_with_ollama(sas_code: str, model: str = "qwen2.5-coder:7b") -> str:
    """Send SAS code to Ollama and return Python translation"""
    
    prompt = f"""Convert this SAS code to Python using polars.
Output only the Python code, no explanations, no markdown formatting.

SAS CODE:
{sas_code}

PYTHON CODE:"""
    
    result = subprocess.run(
        ["ollama", "run", model, prompt],
        capture_output=True,
        text=True,
        timeout=120
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Ollama failed: {result.stderr}")
    
    output = result.stdout
    if "```python" in output:
        output = output.split("```python")[1].split("```")[0]
    elif "```" in output:
        output = output.split("```")[1].split("```")[0]
    
    return output.strip()

# ============================================================
# MAIN
# ============================================================

def main():
    if len(sys.argv) < 2:
        print("Usage: python sas2py_router.py <input.sas> [model]")
        sys.exit(1)
    
    input_path = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "qwen2.5-coder:7b"
    
    with open(input_path, 'r') as f:
        sas_code = f.read()
    
    # Step 1: Detect patterns
    print("🔍 Analyzing SAS code...")
    result = detect_sas_patterns(sas_code)
    
    print(f"\n📊 Pattern Detection:")
    print(f"   RETAIN: {result['RETAIN']}")
    print(f"   BY: {result['BY']}")
    print(f"   FIRST/LAST: {result['FIRST_LAST']}")
    print(f"   Complexity Score: {result['COMPLEXITY_SCORE']}")
    print(f"\n🚦 Routing: {result['ROUTING']}")
    print(f"   Reason: {result['REASON']}")
    
    # Step 2: Route based on complexity
    if result['ROUTING'] == "MANUAL_REVIEW":
        print("\n❌ MANUAL REVIEW REQUIRED")
        print("   This pattern cannot be reliably translated automatically.")
        print(f"   Please translate this code manually or simplify it.")
        
        # Write a placeholder file
        output_path = input_path.replace('.sas', '_MANUAL.py')
        with open(output_path, 'w') as f:
            f.write("# MANUAL REVIEW REQUIRED\n")
            f.write(f"# Reason: {result['REASON']}\n")
            f.write("# Original SAS code:\n")
            for line in sas_code.split('\n'):
                f.write(f"# {line}\n")
            f.write("\n# TODO: Manual translation needed\n")
        
        print(f"📝 Placeholder written to: {output_path}")
        sys.exit(1)
    
    elif result['ROUTING'] == "CAUTION":
        print("\n⚠️ CAUTION - Automatic translation may be incomplete")
        print("   Review output carefully.")
        proceed = input("   Continue? (y/n): ").strip().lower()
        if proceed != 'y':
            print("❌ Aborted.")
            sys.exit(0)
    
    # Step 3: Translate
    print(f"\n🤖 Translating with {model}...")
    python_code = translate_with_ollama(sas_code, model)
    
    # Step 4: Save output
    output_path = input_path.replace('.sas', '.py')
    with open(output_path, 'w') as f:
        f.write("# Generated by sas2py_router\n")
        f.write(f"# Routing: {result['ROUTING']}\n")
        f.write(f"# Reason: {result['REASON']}\n")
        f.write("import polars as pl\n\n")
        f.write(python_code)
    
    print(f"✅ Wrote {output_path}")
    
    if result['ROUTING'] == "CAUTION":
        print("\n⚠️ REMINDER: Review the generated code carefully.")
        print("   The original SAS contained patterns that may not translate perfectly.")

if __name__ == "__main__":
    main()
