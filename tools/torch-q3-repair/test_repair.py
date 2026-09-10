"""Repair mechanics use synthetic files in temporary directories, never installed Torch."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import repair


class RepairTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.torch = self.root / 'python/Lib/site-packages/torch'
        self.target = self.torch / 'fx/experimental/symbolic_shapes.py'
        self.target.parent.mkdir(parents=True)
        (self.torch / 'version.py').write_text('__version__: str = "test-build"\n')
        self.original = b'value = 1\r\n'
        self.patched = b'value = 2\r\n'
        self.target.write_bytes(self.original)
        spec = {'torch_version': 'test-build', 'original_sha256': repair.digest(self.original),
                'patched_sha256': repair.digest(self.patched),
                'edits': [{'before': 'value = 1\n', 'after': 'value = 2\n'}]}
        mock = patch.object(repair, 'SPEC', spec)
        mock.start()
        self.addCleanup(mock.stop)

    def test_check_apply_idempotence_restore_and_exact_backup(self):
        self.assertEqual(repair.repair(self.root), 'original')
        backup = self.target.with_name(self.target.name + '.iw3-q3-original')
        self.assertFalse(backup.exists())
        self.assertEqual(repair.repair(self.root, 'apply'), 'patched')
        self.assertEqual(self.target.read_bytes(), self.patched)
        self.assertEqual(backup.read_bytes(), self.original)
        self.assertEqual(repair.repair(self.root, 'apply'), 'patched')
        self.assertEqual(repair.repair(self.root), 'patched')
        self.assertEqual(repair.repair(self.root, 'restore'), 'original')
        self.assertEqual(self.target.read_bytes(), self.original)
        self.assertEqual(repair.repair(self.root, 'restore'), 'original')

    def test_unknown_version_source_and_bad_backup_are_refused(self):
        version = self.torch / 'version.py'
        version.write_text('__version__ = "other-build"\n')
        with self.assertRaises(ValueError):
            repair.repair(self.root, 'apply')
        self.assertEqual(self.target.read_bytes(), self.original)
        version.write_text('__version__ = "test-build"\n')
        self.target.write_bytes(b'unknown source\n')
        with self.assertRaises(ValueError):
            repair.repair(self.root, 'apply')
        self.assertEqual(self.target.read_bytes(), b'unknown source\n')
        self.target.write_bytes(self.original)
        backup = self.target.with_name(self.target.name + '.iw3-q3-original')
        backup.write_bytes(b'bad backup\n')
        with self.assertRaises(ValueError):
            repair.repair(self.root, 'apply')
        self.assertEqual(self.target.read_bytes(), self.original)
        self.target.write_bytes(self.patched)
        with self.assertRaises(ValueError):
            repair.repair(self.root, 'restore')
        self.assertEqual(self.target.read_bytes(), self.patched)


if __name__ == '__main__':
    unittest.main()
