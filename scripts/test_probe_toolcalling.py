"""Offline tests: never contact a model endpoint."""
import importlib.util
import io
import json
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('probe', Path(__file__).with_name('probe_toolcalling.py'))
assert spec is not None and spec.loader is not None
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


class ProbeTests(unittest.TestCase):
    def test_malformed_is_error(self):
        for payload in ({}, [], {'choices': [{'message': {}}]}, {'choices': [{'message': {'tool_calls': [{}]}}]}):
            with self.subTest(payload=payload):
                self.assertEqual(p.classify(payload), 'ERROR')

    def test_pass_and_text(self):
        call = {'id': 'test-call', 'type': 'function', 'function': {
            'name': 'get_weather_mcp_probe', 'arguments': '{"city":"Munich","date":"next Tuesday"}'}}
        self.assertEqual(p.classify({'choices': [{'message': {'tool_calls': [call]}}]}), 'PASS')
        self.assertEqual(p.classify({'choices': [{'message': {'content': 'I would call weather.'}}]}), 'TEXT-ONLY')

    def test_timeout_retry_does_not_leak(self):
        with patch.object(p.urllib.request, 'urlopen', side_effect=TimeoutError('TESTKEY-secret')) as send, patch.object(p.time, 'sleep'):
            verdict, reason = p.probe('model', 'https://example.invalid/v1/chat/completions', 'TESTKEY-secret')
        self.assertEqual(verdict, 'ERROR')
        self.assertNotIn('TESTKEY-secret', reason)
        self.assertEqual(send.call_count, 2)
        self.assertEqual(send.call_args.kwargs['timeout'], 60)

    def test_request_is_single_message_single_tool(self):
        response = io.BytesIO(json.dumps({'choices': [{'message': {'content': 'No call'}}]}).encode())
        with patch.object(p.urllib.request, 'urlopen', return_value=response) as send:
            self.assertEqual(p.probe('model', 'https://example.invalid/v1/chat/completions', 'TESTKEY-fake')[0], 'TEXT-ONLY')
        body = json.loads(send.call_args.args[0].data)
        self.assertEqual(body['messages'], [{'role': 'user', 'content': p.PROMPT}])
        self.assertEqual(len(body['tools']), 1)


if __name__ == '__main__':
    unittest.main()
