"""Run with:  python -m unittest -v

These tests never call a real AI service. The AI path is tested with a mocked
HTTP response, so they verify EcoSort's own logic (validation, parsing,
fallback), not the quality of any particular model.
"""

import json
import os
import unittest
from unittest import mock

import requests

import app as ecosort

AI_ENV = {"AI_API_URL": "http://fake-llm.local/v1/chat/completions", "AI_MODEL": "test-model"}


def fake_llm_reply(content, status=200):
    resp = mock.Mock()
    resp.status_code = status
    resp.json.return_value = {"choices": [{"message": {"content": content}}]}
    return resp


class EcoSortTests(unittest.TestCase):
    def setUp(self):
        ecosort._hits.clear()
        self.client = ecosort.app.test_client()
        # Start every test in Demo Mode unless it opts in to a mocked AI.
        patcher = mock.patch.dict(os.environ, {"AI_API_URL": "", "AI_MODEL": ""})
        patcher.start()
        self.addCleanup(patcher.stop)

    def analyze(self, waste):
        return self.client.post("/api/analyze", json={"waste": waste})

    # ---- health ----
    def test_health(self):
        r = self.client.get("/api/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["status"], "EcoSort AI backend is running")

    # ---- the six sample test cases (Demo Mode) ----
    def test_sample_cases_demo_mode(self):
        cases = {
            "Banana peel": "Organic / Wet Waste",
            "Plastic water bottle": "Recyclable / Dry Waste",
            "Used battery": "Hazardous / Special Waste",
            "Old mobile phone": "E-Waste",
            "Cardboard box": "Recyclable / Dry Waste",
            "Unknown chemical container": "Hazardous / Special Waste",
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                data = self.analyze(text).get_json()
                self.assertTrue(data["success"])
                self.assertEqual(data["category"], expected)
                self.assertEqual(data["mode"], "demo")
                self.assertEqual(data["mode_label"], "Demo Mode \u2013 AI service unavailable")
                for key in ("item", "action", "tip", "explanation", "uncertainty"):
                    self.assertTrue(data[key])

    def test_other_demo_items(self):
        for text, expected in {
            "food waste": "Organic / Wet Waste",
            "glass bottle": "Recyclable / Dry Waste",
            "broken glass": "General / Residual Waste",
            "used batteries": "Hazardous / Special Waste",
        }.items():
            with self.subTest(text=text):
                self.assertEqual(self.analyze(text).get_json()["category"], expected)

    def test_unknown_item(self):
        data = self.analyze("bottle").get_json()
        self.assertTrue(data["success"])
        self.assertTrue(data["needs_more_info"])
        self.assertEqual(data["uncertainty"], ecosort.UNKNOWN_MESSAGE)

    # ---- validation ----
    def test_empty_input(self):
        for bad in ("", "   ", "\n\t"):
            with self.subTest(bad=repr(bad)):
                r = self.analyze(bad)
                self.assertEqual(r.status_code, 400)
                self.assertFalse(r.get_json()["success"])

    def test_invalid_requests(self):
        self.assertEqual(self.client.post("/api/analyze", data="not json").status_code, 400)
        self.assertEqual(self.client.post("/api/analyze", json={"other": 1}).status_code, 400)
        self.assertEqual(self.client.post("/api/analyze", json={"waste": 123}).status_code, 400)
        self.assertEqual(self.client.post("/api/analyze", json=["waste"]).status_code, 400)
        self.assertEqual(self.analyze("12345 !!!").status_code, 400)

    def test_too_long(self):
        self.assertEqual(self.analyze("a" * 201).status_code, 400)

    def test_oversized_body(self):
        r = self.client.post("/api/analyze", json={"waste": "x" * 10000})
        self.assertEqual(r.status_code, 413)

    def test_wrong_method_and_unknown_route(self):
        self.assertEqual(self.client.get("/api/analyze").status_code, 405)
        self.assertEqual(self.client.get("/api/nothing").status_code, 404)
        self.assertEqual(self.client.get("/app.py").status_code, 404)  # source is not served

    def test_rate_limit(self):
        with mock.patch.dict(os.environ, {"RATE_LIMIT_PER_MINUTE": "2"}):
            self.assertEqual(self.analyze("banana peel").status_code, 200)
            self.assertEqual(self.analyze("banana peel").status_code, 200)
            self.assertEqual(self.analyze("banana peel").status_code, 429)

    # ---- AI path (mocked) ----
    def test_ai_success(self):
        reply = json.dumps(
            {
                "item": "Used plastic water bottle",
                "category": "Recyclable / Dry Waste",
                "action": "Empty and rinse it, then place it in recyclable waste.",
                "tip": "Reuse bottles when possible.",
                "explanation": "Plastic bottles can often be recycled.",
                "uncertainty": "Recycling acceptance varies by location.",
            }
        )
        with mock.patch.dict(os.environ, AI_ENV), mock.patch.object(ecosort.requests, "post", return_value=fake_llm_reply(reply)) as post:
            data = self.analyze("used plastic water bottle").get_json()
        self.assertEqual(data["mode"], "ai")
        self.assertEqual(data["model"], "test-model")
        self.assertNotIn("mode_label", data)
        self.assertEqual(data["category"], "Recyclable / Dry Waste")
        sent = post.call_args.kwargs["json"]["messages"]
        self.assertIn("You are EcoSort AI", sent[0]["content"])
        self.assertEqual(sent[1]["role"], "user")

    def test_ai_output_in_code_fence_and_loose_category(self):
        reply = '```json\n{"item":"AA battery","category":"Hazardous","action":"Take to a collection point.","tip":"Use rechargeables.","explanation":"Contains harmful materials.","uncertainty":""}\n```'
        with mock.patch.dict(os.environ, AI_ENV), mock.patch.object(ecosort.requests, "post", return_value=fake_llm_reply(reply)):
            data = self.analyze("aa battery").get_json()
        self.assertEqual(data["mode"], "ai")
        self.assertEqual(data["category"], "Hazardous / Special Waste")
        self.assertTrue(data["uncertainty"])  # default filled in

    def test_ai_says_unknown(self):
        reply = json.dumps({"item": "thing", "category": "Unknown", "action": "", "tip": "", "explanation": "", "uncertainty": "unclear"})
        with mock.patch.dict(os.environ, AI_ENV), mock.patch.object(ecosort.requests, "post", return_value=fake_llm_reply(reply)):
            data = self.analyze("thing").get_json()
        self.assertEqual(data["mode"], "ai")
        self.assertTrue(data["needs_more_info"])
        self.assertEqual(data["uncertainty"], ecosort.UNKNOWN_MESSAGE)

    def test_ai_timeout_falls_back(self):
        with mock.patch.dict(os.environ, AI_ENV), mock.patch.object(ecosort.requests, "post", side_effect=requests.Timeout()):
            data = self.analyze("banana peel").get_json()
        self.assertEqual(data["mode"], "demo")
        self.assertIn("timed out", data["notice"])
        self.assertEqual(data["category"], "Organic / Wet Waste")

    def test_ai_unreachable_and_http_error_fall_back(self):
        with mock.patch.dict(os.environ, AI_ENV):
            with mock.patch.object(ecosort.requests, "post", side_effect=requests.ConnectionError()):
                self.assertEqual(self.analyze("banana peel").get_json()["mode"], "demo")
            with mock.patch.object(ecosort.requests, "post", return_value=fake_llm_reply("", status=401)):
                self.assertEqual(self.analyze("banana peel").get_json()["mode"], "demo")

    def test_invalid_ai_response_falls_back(self):
        for bad in ("I think it is recyclable!", '{"category": "Space junk"}', "[1,2,3]", '{"category":"E-Waste"}'):
            with self.subTest(bad=bad):
                with mock.patch.dict(os.environ, AI_ENV), mock.patch.object(ecosort.requests, "post", return_value=fake_llm_reply(bad)):
                    data = self.analyze("old mobile phone").get_json()
                self.assertEqual(data["mode"], "demo")
                self.assertEqual(data["category"], "E-Waste")

    def test_ai_bad_envelope_falls_back(self):
        resp = mock.Mock(status_code=200)
        resp.json.return_value = {"unexpected": True}
        with mock.patch.dict(os.environ, AI_ENV), mock.patch.object(ecosort.requests, "post", return_value=resp):
            self.assertEqual(self.analyze("banana peel").get_json()["mode"], "demo")

    # ---- frontend + headers ----
    def test_serves_frontend_with_security_headers(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("Content-Security-Policy", r.headers)
        self.assertEqual(r.headers["X-Content-Type-Options"], "nosniff")
        r.close()

    def test_serves_every_page_and_asset(self):
        for name in ("index.html", "analyze.html", "categories.html", "responsible-ai.html", "about.html", "style.css", "script.js"):
            with self.subTest(name=name):
                r = self.client.get("/" + name)
                self.assertEqual(r.status_code, 200)
                r.close()


if __name__ == "__main__":
    unittest.main()
