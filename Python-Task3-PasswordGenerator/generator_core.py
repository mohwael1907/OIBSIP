"""
generator_core.py - Core Security & Password Logic Layer
Uses Python's secrets module for cryptographically secure random password generation.
Enforces security guarantees, strength assessment, and in-memory session history.
"""

import math
import secrets
import string
from collections import deque
from datetime import datetime
from typing import Dict, List, Tuple, Any

# Character Pools
DEFAULT_UPPERCASE = string.ascii_uppercase
DEFAULT_LOWERCASE = string.ascii_lowercase
DEFAULT_DIGITS = string.digits
DEFAULT_SYMBOLS = "!@#$%^&*()_+-=[]{}|;:,.<>?/~"

# Ambiguous characters often confused in print or UI
AMBIGUOUS_CHARS = set("0Ool1I|")


class PasswordGenerator:
    """Cryptographically secure password generator enforcing strict diversity rules."""

    @staticmethod
    def filter_ambiguous(char_set: str, exclude_ambiguous: bool) -> str:
        """Remove ambiguous characters from a given character set if requested."""
        if not exclude_ambiguous:
            return char_set
        return "".join(c for c in char_set if c not in AMBIGUOUS_CHARS)

    @classmethod
    def generate(
        cls,
        length: int = 16,
        use_uppercase: bool = True,
        use_lowercase: bool = True,
        use_digits: bool = True,
        use_symbols: bool = True,
        exclude_ambiguous: bool = False,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a password using the secrets module.
        
        Guarantees:
        - Contains at least 1 character from each active character set.
        - Cryptographically secure randomness using secrets.choice and secrets.SystemRandom().
        - Excludes ambiguous characters if requested.

        Raises:
            ValueError: If no character sets are selected or length is insufficient.
        """
        # Build active pools
        active_pools: List[str] = []
        if use_uppercase:
            pool = cls.filter_ambiguous(DEFAULT_UPPERCASE, exclude_ambiguous)
            if pool:
                active_pools.append(pool)
        if use_lowercase:
            pool = cls.filter_ambiguous(DEFAULT_LOWERCASE, exclude_ambiguous)
            if pool:
                active_pools.append(pool)
        if use_digits:
            pool = cls.filter_ambiguous(DEFAULT_DIGITS, exclude_ambiguous)
            if pool:
                active_pools.append(pool)
        if use_symbols:
            pool = cls.filter_ambiguous(DEFAULT_SYMBOLS, exclude_ambiguous)
            if pool:
                active_pools.append(pool)

        if not active_pools:
            raise ValueError("At least one valid character type must be selected.")

        num_types = len(active_pools)
        if length < num_types:
            raise ValueError(
                f"Password length ({length}) must be at least the number of selected character types ({num_types})."
            )

        # 1. Guarantee at least 1 character from each selected pool
        password_chars: List[str] = [secrets.choice(pool) for pool in active_pools]

        # 2. Combine all pools for remaining character slots
        combined_pool = "".join(active_pools)
        remaining_slots = length - num_types

        for _ in range(remaining_slots):
            password_chars.append(secrets.choice(combined_pool))

        # 3. Cryptographically secure shuffle using SystemRandom
        sys_random = secrets.SystemRandom()
        sys_random.shuffle(password_chars)

        generated_password = "".join(password_chars)
        
        # 4. Calculate strength metrics
        strength_meta = eval_password_strength(
            generated_password,
            use_uppercase=use_uppercase,
            use_lowercase=use_lowercase,
            use_digits=use_digits,
            use_symbols=use_symbols,
            pool_size=len(set(combined_pool)),
        )

        return generated_password, strength_meta


def calculate_entropy(length: int, pool_size: int) -> float:
        """
    Calculate Shannon / Bit Entropy: E = L * log2(N)
    where L = password length, N = total size of unique character pool available.
    """
        if pool_size <= 1 or length <= 0:
            return 0.0
        return length * math.log2(pool_size)


def eval_password_strength(
    password: str,
    use_uppercase: bool = True,
    use_lowercase: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
    pool_size: int = 0,
) -> Dict[str, Any]:
    """
    Evaluates password strength based on entropy (bits) and character diversity.
    Returns dictionary with score, rating, color, feedback tips, and entropy bits.
    """
    length = len(password)
    
    # Calculate effective pool size if not passed
    if pool_size <= 0:
        pool = 0
        if any(c in DEFAULT_UPPERCASE for c in password):
            pool += 26
        if any(c in DEFAULT_LOWERCASE for c in password):
            pool += 26
        if any(c in DEFAULT_DIGITS for c in password):
            pool += 10
        if any(c in DEFAULT_SYMBOLS for c in password):
            pool += len(DEFAULT_SYMBOLS)
        pool_size = max(pool, 1)

    entropy = calculate_entropy(length, pool_size)
    
    # Diversity checks
    has_upper = any(c in DEFAULT_UPPERCASE for c in password)
    has_lower = any(c in DEFAULT_LOWERCASE for c in password)
    has_digit = any(c in DEFAULT_DIGITS for c in password)
    has_symbol = any(c in DEFAULT_SYMBOLS for c in password)
    diversity_count = sum([has_upper, has_lower, has_digit, has_symbol])

    # Determine Rating & Score Percentage (0-100%)
    # Entropy thresholds: <35 Weak, 35-59 Medium, 60-89 Strong, >=90 Very Strong
    if entropy < 35 or length < 8:
        rating = "Weak"
        color = "#FF5252"  # Red
        score_percent = min(35.0, (entropy / 35.0) * 35.0)
    elif entropy < 60 or length < 12 or diversity_count < 2:
        rating = "Medium"
        color = "#FFA726"  # Orange
        score_percent = 35.0 + ((entropy - 35) / 25.0) * 30.0
    elif entropy < 90 or diversity_count < 3:
        rating = "Strong"
        color = "#66BB6A"  # Green
        score_percent = 65.0 + ((entropy - 60) / 30.0) * 25.0
    else:
        rating = "Very Strong"
        color = "#00E676"  # Bright Emerald
        score_percent = min(100.0, 90.0 + ((entropy - 90) / 30.0) * 10.0)

    # Tips for improvement
    tips: List[str] = []
    if length < 16:
        tips.append("Increase length to 16+ characters for maximum security.")
    if not has_upper:
        tips.append("Add uppercase letters.")
    if not has_lower:
        tips.append("Add lowercase letters.")
    if not has_digit:
        tips.append("Add numbers.")
    if not has_symbol:
        tips.append("Add special symbols (!@#$).")
    if not tips:
        tips.append("Excellent password! Highly resistant to brute-force attacks.")

    return {
        "entropy_bits": round(entropy, 1),
        "rating": rating,
        "color": color,
        "score_percent": round(min(100.0, max(5.0, score_percent)), 1),
        "tips": tips,
        "diversity_count": diversity_count,
        "pool_size": pool_size,
    }


class SessionHistoryManager:
    """Manages the last 5 generated passwords strictly in-memory during the active session."""

    def __init__(self, max_items: int = 5):
        self.max_items = max_items
        self._history: deque = deque(maxlen=max_items)

    def add(self, password: str, metadata: Dict[str, Any]) -> None:
        """Add a generated password to history with timestamp."""
        record = {
            "password": password,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "rating": metadata.get("rating", "Unknown"),
            "entropy": metadata.get("entropy_bits", 0.0),
            "color": metadata.get("color", "#888888"),
        }
        # Push to left so newest is first
        self._history.appendleft(record)

    def get_history(self) -> List[Dict[str, Any]]:
        """Return list of recent password records."""
        return list(self._history)

    def clear(self) -> None:
        """Clear session history."""
        self._history.clear()
