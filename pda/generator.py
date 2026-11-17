# StackScope - JSON-Driven DPDA Loader & Catalog
# Loads theoretical DPDAs directly from standard JSON data files.
# Beginner-friendly, plain Python for college TOC viva.
# No __init__.py is used in this project.

from pathlib import Path
from pda.pda_core import PushdownAutomaton

# Absolute path to the data folder (guaranteed to work from anywhere)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


# =====================================================================
# 1. Supported DPDA Catalog (100% Valid DPDA Languages)
#    Maps clean language titles to their JSON data file and description.
# =====================================================================

SUPPORTED_LANGUAGES = {
    # 1. Equal Power
    "a^n b^n (n >= 1)": {
        "description": "Equal a's followed by equal b's (e.g. ab, aabb, aaabbb)",
        "file": "an_bn.json"
    },
    "0^n 1^n (n >= 1)": {
        "description": "Equal 0's followed by equal 1's (e.g. 01, 0011, 000111)",
        "file": "0n_1n.json"
    },
    "a^n b^n (n >= 0)": {
        "description": "Equal a's and b's, including empty string ε",
        "file": "an_bn_empty.json"
    },

    # 2. Multipliers & Ratios
    "a^n b^2n (n >= 1)": {
        "description": "Twice as many b's as a's (e.g. abb, aabbbb)",
        "file": "an_b2n.json"
    },
    "a^2n b^n (n >= 1)": {
        "description": "Twice as many a's as b's (e.g. aab, aaaabb)",
        "file": "a2n_bn.json"
    },
    "a^n b^3n (n >= 1)": {
        "description": "Three times as many b's as a's (e.g. abbb, aabbbbbb)",
        "file": "an_b3n.json"
    },

    # 3. Three-Symbol
    "a^n b^m c^n (n, m >= 1)": {
        "description": "Equal a's and c's separated by any count of b's (e.g. abc, aabbcc)",
        "file": "an_bm_cn.json"
    },
    "a^n b^n c^m (n, m >= 1)": {
        "description": "Equal a's and b's followed by any count of c's (e.g. abc, aabbc)",
        "file": "an_bn_cm.json"
    },
    "a^m b^n c^n (m, n >= 1)": {
        "description": "Any count of a's followed by equal b's and c's (e.g. abc, aabbcc)",
        "file": "am_bn_cn.json"
    },

    # 4. Sum Relations
    "a^n b^m c^(n+m) (n, m >= 1)": {
        "description": "Count of c equals count of a plus b (e.g. abcc, aabbcccc)",
        "file": "sum_an_bm_c.json"
    },
    "a^(n+m) b^m c^n (n, m >= 1)": {
        "description": "Count of a equals count of b plus c (e.g. aaabbc, aabbc)",
        "file": "sum_a_bm_cn.json"
    },

    # 5. Inequalities
    "a^n b^m (n != m)": {
        "description": "Unequal count of a's and b's (accepts n > m or m > n, rejects n = m)",
        "file": "inequality_n_neq_m.json"
    },
    "a^n b^m (n > m)": {
        "description": "Strictly more a's than b's (e.g. aab, aaabb)",
        "file": "inequality_n_greater_m.json"
    },
    "a^n b^m (m > n)": {
        "description": "Strictly more b's than a's (e.g. abb, aabbb)",
        "file": "inequality_m_greater_n.json"
    },

    # 6. Palindromes with Marker
    "w c w^R (over {a, b})": {
        "description": "Palindrome with center marker c (e.g. aca, abcba, aabbcbbaa)",
        "file": "palindrome_c.json"
    },
    "w # w^R (over {0, 1})": {
        "description": "Binary palindrome with center marker # (e.g. 0#0, 01#10)",
        "file": "palindrome_hash.json"
    },

    # 7. Delimiters
    "Balanced Parentheses ()": {
        "description": "Properly nested parentheses: (), (()), ()(), (()())",
        "file": "balanced_parentheses.json"
    },
    "Mixed Brackets () and []": {
        "description": "Properly nested parentheses and square brackets: ([()]), ()[]",
        "file": "mixed_brackets.json"
    }
}

# Alias for compatibility with existing imports
LANGUAGE_CATALOG = SUPPORTED_LANGUAGES


# =====================================================================
# 2. JSON Loader Functions
# =====================================================================

def load_dpda_from_file(filename: str) -> PushdownAutomaton:
    """Reads a DPDA definition from a JSON file in the data folder."""
    filepath = DATA_DIR / filename
    with open(filepath, "r", encoding="utf-8") as f:
        return PushdownAutomaton.from_json(f.read())


def generate_dpda_for_language(language_name: str) -> tuple[PushdownAutomaton, str]:
    """
    Finds the requested language in the catalog and loads its DPDA from JSON.
    Returns (automaton, error_string).
    """
    name = language_name.strip()

    # Theoretical Limits (Guards)
    if "a^n b^n c^n" in name:
        return (None, "Context-Sensitive Language (Non-CFL). A single stack cannot compare 3 independent counts.")

    if "w w" in name:
        return (None, "Language L = { w w } is NOT Context-Free. A LIFO stack cannot verify a forward duplicate string.")

    if "is a palindrome" in name:
        return (None, "Requires Non-deterministic PDA (NPDA) because it has no center marker to indicate the midpoint.")

    # Match exact name or key substring
    for key, meta in SUPPORTED_LANGUAGES.items():
        if key == name or key in name or name in key:
            pda = load_dpda_from_file(meta["file"])
            return (pda, "")

    return (None, f"Language '{language_name}' not found in data catalog.")
