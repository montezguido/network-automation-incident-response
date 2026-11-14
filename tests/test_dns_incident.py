"""Offline, independently written DNS-incident regression tests."""

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "portfolio_demo"))
from dns_incident import (  # noqa: E402
    ScenarioError, assess, load_scenario, main, parse_scenario, simulate,
)


class DnsIncidentTests(unittest.TestCase):
    def setUp(self):
        self.sample = json.loads((ROOT / "portfolio_demo" / "sample_timeline.json").read_text(encoding="utf-8"))

    def test_sample_opens_only_once_and_recovers(self):
        result = simulate(self.sample)
        self.assertEqual([len(f["events"]) for f in result["frames"]], [0, 2, 0, 2])
        self.assertEqual([e["type"] for e in result["frames"][1]["events"]], ["OPENED", "OPENED"])
        self.assertEqual([e["type"] for e in result["frames"][3]["events"]], ["RECOVERED", "RECOVERED"])
        self.assertEqual(result["final_active_incidents"], [])

    def test_tickets_close_after_recovery(self):
        result = simulate(self.sample)
        self.assertEqual(len(result["tickets"]), 2)
        self.assertEqual({t["status"] for t in result["tickets"]}, {"RESOLVED"})

    def test_simulation_determinism(self):
        self.assertEqual(simulate(self.sample), simulate(self.sample))

    def test_simulation_does_not_mutate_input(self):
        before = copy.deepcopy(self.sample)
        simulate(self.sample)
        self.assertEqual(self.sample, before)

    def test_healthy_baseline(self):
        approved, frames = parse_scenario(self.sample)
        self.assertEqual(assess(approved, frames[0]), {})

    def test_reachable_endpoint_can_have_rogue_resolver(self):
        approved, frames = parse_scenario(self.sample)
        active = assess(approved, frames[1])
        self.assertEqual(active["device/workstation-a/resolver"]["category"], "UNAPPROVED_RESOLVER")
        self.assertNotIn("device/workstation-a/availability", active)

    def test_unreachable_device_is_detected(self):
        self.sample["frames"][0]["devices"][0]["reachable"] = False
        result = simulate(self.sample)
        self.assertIn("device/workstation-a/availability", result["frames"][0]["active_incidents"])

    def test_new_issue_in_later_frame_opens_ticket(self):
        self.sample["frames"][0]["devices"][1]["reachable"] = False
        result = simulate(self.sample)
        self.assertEqual(result["frames"][0]["events"][0]["type"], "OPENED")
        self.assertTrue(any(e["type"] == "RECOVERED" for e in result["frames"][1]["events"]))

    def test_unresolved_ticket_stays_open(self):
        self.sample["frames"] = self.sample["frames"][:3]
        result = simulate(self.sample)
        self.assertEqual({t["status"] for t in result["tickets"]}, {"OPEN"})

    def test_reappearing_issue_creates_new_ticket(self):
        self.sample["frames"].append(copy.deepcopy(self.sample["frames"][1]))
        result = simulate(self.sample)
        self.assertEqual(len(result["tickets"]), 4)  # a new incident creates a new ticket after recovery
        self.assertEqual(len(result["frames"][-1]["events"]), 2)
        self.assertEqual([t["status"] for t in result["tickets"]].count("OPEN"), 2)
        self.assertEqual([t["status"] for t in result["tickets"]].count("RESOLVED"), 2)

    def test_blank_document_rejected(self):
        with self.assertRaises(ScenarioError):
            parse_scenario(None)

    def test_whitespace_only_device_name_rejected(self):
        self.sample["frames"][0]["devices"][0]["id"] = "   "
        with self.assertRaisesRegex(ScenarioError, "nonempty"):
            simulate(self.sample)

    def test_no_approved_resolvers_rejected(self):
        self.sample["approved_resolvers"] = []
        with self.assertRaises(ScenarioError):
            simulate(self.sample)

    def test_duplicate_approved_rejected(self):
        self.sample["approved_resolvers"] = ["192.0.2.53", "192.0.2.53"]
        with self.assertRaisesRegex(ScenarioError, "duplicate"):
            simulate(self.sample)

    def test_invalid_approved_ip_rejected(self):
        self.sample["approved_resolvers"][0] = "localhost"
        with self.assertRaisesRegex(ScenarioError, "invalid IPv4"):
            simulate(self.sample)

    def test_empty_frames_rejected(self):
        self.sample["frames"] = []
        with self.assertRaises(ScenarioError):
            simulate(self.sample)

    def test_missing_service_status_rejected(self):
        del self.sample["frames"][0]["dns_service"]
        with self.assertRaisesRegex(ScenarioError, "dns_service"):
            simulate(self.sample)

    def test_bad_service_status_rejected(self):
        self.sample["frames"][0]["dns_service"] = "unknown"
        with self.assertRaisesRegex(ScenarioError, "dns_service"):
            simulate(self.sample)

    def test_duplicate_endpoint_rejected(self):
        self.sample["frames"][0]["devices"].append(copy.deepcopy(self.sample["frames"][0]["devices"][0]))
        with self.assertRaisesRegex(ScenarioError, "duplicate device"):
            simulate(self.sample)

    def test_boolean_reachability_required(self):
        self.sample["frames"][0]["devices"][0]["reachable"] = "true"
        with self.assertRaisesRegex(ScenarioError, "boolean"):
            simulate(self.sample)

    def test_invalid_resolver_rejected(self):
        self.sample["frames"][0]["devices"][0]["resolver"] = "example.org"
        with self.assertRaisesRegex(ScenarioError, "invalid IPv4"):
            simulate(self.sample)

    def test_invalid_device_identifier_rejected(self):
        self.sample["frames"][0]["devices"][0]["id"] = "../../oops"
        with self.assertRaisesRegex(ScenarioError, "only ASCII"):
            simulate(self.sample)

    def test_empty_devices_rejected(self):
        self.sample["frames"][0]["devices"] = []
        with self.assertRaises(ScenarioError):
            simulate(self.sample)

    def test_missing_device_does_not_imply_recovery(self):
        self.sample["frames"][2]["devices"] = self.sample["frames"][2]["devices"][:1]
        with self.assertRaisesRegex(ScenarioError, "inventory changed"):
            simulate(self.sample)

    def test_extra_device_rejected_in_later_frame(self):
        self.sample["frames"][1]["devices"].append(
            {"id": "new-device", "reachable": True, "resolver": "192.0.2.54"}
        )
        with self.assertRaisesRegex(ScenarioError, "inventory changed"):
            simulate(self.sample)

    def test_non_object_device_rejected(self):
        self.sample["frames"][0]["devices"] = [None]
        with self.assertRaisesRegex(ScenarioError, "expected an object"):
            simulate(self.sample)

    def test_frame_limit_rejected(self):
        self.sample["frames"] = self.sample["frames"] * 17
        with self.assertRaises(ScenarioError):
            simulate(self.sample)

    def test_invalid_json_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "bad.json"
            p.write_text("not JSON", encoding="utf-8")
            with self.assertRaisesRegex(ScenarioError, "valid UTF-8 JSON"):
                load_scenario(p)

    def test_file_size_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "huge.json"
            p.write_bytes(b"x" * (256 * 1024 + 1))
            with self.assertRaisesRegex(ScenarioError, "limit"):
                load_scenario(p)

    def test_json_cli(self):
        with StringIO() as captured:
            with redirect_stdout(captured):
                code = main(["--json"])
            printed = captured.getvalue()
        self.assertEqual(code, 0)
        report = json.loads(printed)
        self.assertEqual(report["mode"], "offline_simulation")

    def test_cli_default_output(self):
        with StringIO() as captured:
            with redirect_stdout(captured):
                code = main([])
            printed = captured.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("no external actions performed", printed)


if __name__ == "__main__":
    unittest.main()
