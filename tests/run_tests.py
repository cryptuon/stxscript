import unittest
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

if __name__ == '__main__':
    test_suite = unittest.defaultTestLoader.discover('tests', pattern='test_*.py')
    unittest.TextTestRunner().run(test_suite)