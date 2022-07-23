import unittest

from sirenity import __main__


class ApplicationTest(unittest.TestCase):
    """Tests for the sirenity application"""

    def test_main(self):
        """Tests that main function can be run"""
        self.assertTrue(callable(__main__.main))
