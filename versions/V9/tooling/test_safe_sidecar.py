import tempfile
import unittest
from pathlib import Path
from safe_sidecar import sidecar_path

class SafeSidecarTests(unittest.TestCase):
    def test_valid_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); f=root/'trace.gz'; f.write_bytes(b'x')
            self.assertEqual(sidecar_path(root, 'trace.gz'), f.resolve())
    def test_invalid_names(self):
        with tempfile.TemporaryDirectory() as temp:
            for name in ('../outside', '/etc/passwd', 'C:\\path', 'nested/a', '..', '.', '', 'x\x00y', None):
                with self.subTest(name=name), self.assertRaises(ValueError):
                    sidecar_path(Path(temp), name)
    def test_symlink_and_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); target=root/'target'; target.write_bytes(b'x')
            (root/'link').symlink_to(target); (root/'directory').mkdir()
            for name in ('link', 'directory'):
                with self.subTest(name=name), self.assertRaises(ValueError):
                    sidecar_path(root, name)
