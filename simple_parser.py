#!/usr/bin/env python3
"""Minimal SAS pattern detector for routing decisions"""

import re
import sys

def detect_sas_patterns(sas_code: str) -> dict:
    """Detect patterns that affect translation strategy"""
    
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
        flags["REASON"] = "RETAIN with BY (no FIRST) - attempt LLM with caution"
    elif flags["COMPLEXITY_SCORE"] >= 3:
        flags["ROUTING"] = "CAUTION"
        flags["REASON"] = f"Multiple patterns detected: score {flags['COMPLEXITY_SCORE']}"
    else:
        flags["ROUTING"] = "AUTO_LLM"
        flags["REASON"] = "Simple pattern - safe for auto-translation"
    
    return flags

def main():
    if len(sys.argv) < 2:
        print("Usage: python simple_parser.py <input.sas>")
        sys.exit(1)
    
    with open(sys.argv[1], 'r') as f:
        sas_code = f.read()
    
    result = detect_sas_patterns(sas_code)
    
    print("\n=== SAS Pattern Detection Results ===")
    for key, value in result.items():
        if not key.startswith("__"):
            print(f"{key:15}: {value}")
    print("=" * 40)

if __name__ == "__main__":
    main()
