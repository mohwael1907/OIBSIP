"""
test_generator.py - Unit tests for Password Generator core logic.
"""

import unittest
import string
from generator_core import (
    PasswordGenerator,
    SessionHistoryManager,
    eval_password_strength,
    calculate_entropy,
    AMBIGUOUS_CHARS,
    DEFAULT_UPPERCASE,
    DEFAULT_LOWERCASE,
    DEFAULT_DIGITS,
    DEFAULT_SYMBOLS,
)


class TestPasswordGenerator(unittest.TestCase):

    def test_default_generation(self):
        """Test default password generation (length 16, all character sets)."""
        password, meta = PasswordGenerator.generate(length=16)
        self.assertEqual(len(password), 16)
        self.assertIn("rating", meta)
        self.assertGreater(meta["entropy_bits"], 0)

    def test_guaranteed_character_types(self):
        """Verify password strictly contains at least 1 char from each selected set."""
        for _ in range(20):  # Run 20 times to ensure consistency
            password, _ = PasswordGenerator.generate(
                length=12,
                use_uppercase=True,
                use_lowercase=True,
                use_digits=True,
                use_symbols=True,
            )
            self.assertTrue(any(c in DEFAULT_UPPERCASE for c in password))
            self.assertTrue(any(c in DEFAULT_LOWERCASE for c in password))
            self.assertTrue(any(c in DEFAULT_DIGITS for c in password))
            self.assertTrue(any(c in DEFAULT_SYMBOLS for c in password))

    def test_ambiguous_character_exclusion(self):
        """Test that ambiguous characters (0, O, l, 1, I, |) are strictly excluded."""
        for _ in range(20):
            password, _ = PasswordGenerator.generate(
                length=30,
                exclude_ambiguous=True,
            )
            for amb in AMBIGUOUS_CHARS:
                self.assertNotIn(amb, password)

    def test_invalid_length_or_pools(self):
        """Test ValueError exceptions for invalid configurations."""
        # Length smaller than selected types count
        with self.assertRaises(ValueError):
            PasswordGenerator.generate(
                length=3,
                use_uppercase=True,
                use_lowercase=True,
                use_digits=True,
                use_symbols=True,
            )

        # No character types selected
        with self.assertRaises(ValueError):
            PasswordGenerator.generate(
                length=16,
                use_uppercase=False,
                use_lowercase=False,
                use_digits=False,
                use_symbols=False,
            )

    def test_entropy_and_strength_evaluation(self):
        """Test entropy and strength calculations."""
        # Short weak password
        weak_meta = eval_password_strength("abc", pool_size=26)
        self.assertEqual(weak_meta["rating"], "Weak")
        self.assertEqual(weak_meta["color"], "#FF5252")

        # Long strong password
        strong_meta = eval_password_strength("P@ssw0rd!2026SecureStr#", pool_size=94)
        self.assertIn(strong_meta["rating"], ["Strong", "Very Strong"])

    def test_session_history_limit(self):
        """Test that SessionHistoryManager strictly caps history at max_items (5)."""
        history = SessionHistoryManager(max_items=5)
        for i in range(10):
            pwd = f"pass_{i}"
            meta = {"rating": "Strong", "entropy_bits": 65.0, "color": "#66BB6A"}
            history.add(pwd, meta)

        items = history.get_history()
        self.assertEqual(len(items), 5)
        # Most recent should be pass_9
        self.assertEqual(items[0]["password"], "pass_9")
        self.assertEqual(items[-1]["password"], "pass_5")

    def test_session_history_clear(self):
        """Test clearing history."""
        history = SessionHistoryManager()
        history.add("test", {"rating": "Weak"})
        history.clear()
        self.assertEqual(len(history.get_history()), 0)


if __name__ == "__main__":
    unittest.main()
