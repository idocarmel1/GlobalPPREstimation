"""Execution provenance describes imported adapter code and rejects mixed workers."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from tools.scientific_helpers.sppr import method_coverage as adapter


class AdapterExecutionIdentityTests(unittest.TestCase):
    def test_evidence_uses_imported_adapter_hash_when_disk_path_changes(self):
        expected = adapter._hash_bytes(Path(adapter.__file__).read_bytes())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            changed = root/'adapter.py'
            changed.write_text('# later disk version\n', encoding='utf-8')
            model = root/'model.json'
            model.write_text('{}', encoding='utf-8')
            with patch.object(adapter, '__file__', str(changed)):
                result = adapter.compute_methods(model, None, ['SPPR_1986'], root/'evidence',
                                                 progress=None, method_timeout=0)
            self.assertEqual(result['adapter_sha256'], expected)

    def test_worker_rejects_different_adapter_before_loading_model(self):
        connection = Mock()
        with patch.object(adapter, '_load', side_effect=AssertionError('Model must not load')):
            adapter._worker(connection, 'unused', {}, {}, '0'*64)
        reply = connection.send.call_args.args[0]
        self.assertEqual(reply['status'], 'constructor_failed')
        self.assertIn('adapter', reply['exception']['message'].lower())
        connection.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
