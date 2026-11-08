"""Offline, synthetic tests; no weights or network needed."""
import copy
import json
import unittest
from pathlib import Path

from tools.buddy_local_compute_preflight import parse_cgroup_memory_current, parse_cgroup_memory_limit, parse_linux_memavailable, parse_linux_memtotal, report

ROOT = Path(__file__).resolve().parents[1]


class LocalComputePreflightTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "config/buddy-open-weight-candidate-research.json").read_text())

    def test_linux_memory_single_line(self):
        self.assertEqual(parse_linux_memtotal("MemTotal:       8192 kB\nMemFree: 2 kB\n"), 8192 * 1024)

    def test_rejects_ambiguous_memory(self):
        self.assertIsNone(parse_linux_memtotal("MemTotal: 1024 kB\nMemTotal: 2048 kB\n"))
        self.assertIsNone(parse_linux_memtotal("MemTotal: 0 kB\n"))
        self.assertIsNone(parse_linux_memtotal("MemTotal: secret kB\n"))

    def test_linux_available_memory_parser(self):
        self.assertEqual(parse_linux_memavailable("MemTotal: 8192 kB\nMemAvailable: 4096 kB\n"), 4096 * 1024)
        for sample in ("MemAvailable: 0 kB\n", "MemAvailable: nope kB\n",
                       "MemAvailable: 1 kB\nMemAvailable: 2 kB\n"):
            with self.subTest(sample=sample):
                self.assertIsNone(parse_linux_memavailable(sample))

    def test_host_available_is_not_container_fit(self):
        result = report(self.data, 16 * 1024 ** 3, "linux_meminfo", "Linux",
                        2 * 1024 ** 3, "cgroup_v2",
                        12 * 1024 ** 3, "linux_meminfo")
        self.assertEqual(result["observed_host_available_memory_gib"], 12)
        self.assertEqual(result["observed_effective_memory_ceiling_gib"], 2)
        self.assertFalse(result["hardware_suitability_verified"])
        self.assertFalse(result["training_authorized"])

    def test_invalid_host_available_memory_fails_closed(self):
        for available, source, system in (
            (True, "linux_meminfo", "Linux"),
            (0, "linux_meminfo", "Linux"),
            (17 * 1024 ** 3, "linux_meminfo", "Linux"),
            (8 * 1024 ** 3, "unavailable", "Linux"),
            (8 * 1024 ** 3, "linux_meminfo", "Darwin"),
        ):
            with self.subTest(available=available, source=source, system=system):
                with self.assertRaises(ValueError):
                    report(self.data, 16 * 1024 ** 3, "linux_meminfo", system,
                           available_memory_bytes=available, available_memory_source=source)

    def test_cgroup_v2_and_v1_limits(self):
        self.assertEqual(parse_cgroup_memory_limit("4294967296\n"), 4 * 1024 ** 3)
        for value in ("max", "0", "-1", "1.5", "1\n2", str(2 ** 63 - 4096)):
            with self.subTest(value=value):
                self.assertIsNone(parse_cgroup_memory_limit(value))

    def test_cgroup_current_parser_accepts_zero_and_rejects_bad_readings(self):
        self.assertEqual(parse_cgroup_memory_current("0\n"), 0)
        self.assertEqual(parse_cgroup_memory_current("1073741824\n"), 1024 ** 3)
        for value in ("max", "-1", "1.5", "1\n2", str(2 ** 60)):
            with self.subTest(value=value):
                self.assertIsNone(parse_cgroup_memory_current(value))

    def test_cgroup_v2_usage_is_not_model_fit_evidence(self):
        result = report(self.data, 16 * 1024 ** 3, "linux_meminfo", "Linux",
                        4 * 1024 ** 3, "cgroup_v2",
                        cgroup_current_bytes=3 * 1024 ** 3,
                        cgroup_current_source="cgroup_v2")
        self.assertEqual(result["observed_cgroup_current_usage_gib"], 3)
        self.assertEqual(result["observed_cgroup_limit_minus_usage_gib"], 1)
        self.assertFalse(result["hardware_suitability_verified"])
        self.assertFalse(result["training_authorized"])

    def test_over_limit_usage_never_reports_negative_headroom(self):
        result = report(self.data, None, "unavailable", "Linux",
                        2 * 1024 ** 3, "cgroup_v2",
                        cgroup_current_bytes=3 * 1024 ** 3,
                        cgroup_current_source="cgroup_v2")
        self.assertEqual(result["observed_cgroup_limit_minus_usage_gib"], 0)
        self.assertFalse(result["candidate_weight_only_estimates"][0]["fits_in_memory_verified"])

    def test_cgroup_current_requires_matching_v2_provenance(self):
        for limit, limit_source, current, current_source, system in (
            (None, "unavailable", 0, "cgroup_v2", "Linux"),
            (1024, "cgroup_v1", 0, "cgroup_v2", "Linux"),
            (1024, "cgroup_v2", 0, "unavailable", "Linux"),
            (1024, "cgroup_v2", True, "cgroup_v2", "Linux"),
            (1024, "cgroup_v2", -1, "cgroup_v2", "Linux"),
            (1024, "cgroup_v2", 0, "cgroup_v2", "Darwin"),
        ):
            with self.subTest(limit=limit, current=current, source=current_source, system=system):
                with self.assertRaises(ValueError):
                    report(self.data, None, "unavailable", system,
                           limit, limit_source,
                           cgroup_current_bytes=current,
                           cgroup_current_source=current_source)

    def test_cgroup_caps_host_memory_without_claiming_fit(self):
        result = report(self.data, 16 * 1024 ** 3, "linux_meminfo", "Linux",
                        4 * 1024 ** 3, "cgroup_v2")
        self.assertEqual(result["observed_total_memory_gib"], 16)
        self.assertEqual(result["observed_cgroup_limit_gib"], 4)
        self.assertEqual(result["observed_effective_memory_ceiling_gib"], 4)
        self.assertFalse(result["hardware_suitability_verified"])

    def test_host_total_caps_higher_cgroup_limit(self):
        result = report(self.data, 4 * 1024 ** 3, "linux_meminfo", "Linux",
                        16 * 1024 ** 3, "cgroup_v1")
        self.assertEqual(result["observed_effective_memory_ceiling_gib"], 4)

    def test_cgroup_limit_without_host_memory_and_invalid_inputs(self):
        result = report(self.data, None, "unavailable", "Linux",
                        2 * 1024 ** 3, "cgroup_v2")
        self.assertIsNone(result["observed_total_memory_gib"])
        self.assertEqual(result["observed_effective_memory_ceiling_gib"], 2)
        for value in (True, 0, -1, 1.2, 2 ** 60):
            with self.subTest(value=value), self.assertRaises(ValueError):
                report(self.data, None, "unavailable", "Linux", value, "cgroup_v2")
        with self.assertRaises(ValueError):
            report(self.data, None, "unavailable", "Darwin", 1024, "cgroup_v2")

    def test_unknown_memory_is_not_approval(self):
        result = report(self.data, None, "unavailable", "Linux")
        self.assertIsNone(result["observed_total_memory_gib"])
        self.assertFalse(result["hardware_suitability_verified"])
        self.assertFalse(result["training_authorized"])
        self.assertEqual(result["model_runs"], 0)

    def test_weight_only_arithmetic(self):
        result = report(self.data, 16 * 1024 ** 3, "linux_meminfo", "Linux")
        self.assertEqual(result["observed_total_memory_gib"], 16.0)
        self.assertEqual(len(result["candidate_weight_only_estimates"]), 3)
        self.assertAlmostEqual(result["candidate_weight_only_estimates"][0]["approx_fp16_weight_only_gib"], 1.118, places=3)
        self.assertTrue(all(not x["fits_in_memory_verified"] for x in result["candidate_weight_only_estimates"]))

    def test_rejects_fake_memory(self):
        for value in (True, 0, -1, 1.2, "16"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                report(self.data, value, "unavailable", "Linux")

    def test_cannot_promote_candidate(self):
        data = copy.deepcopy(self.data)
        data["candidates"][0]["model_trained"] = True
        with self.assertRaises(ValueError):
            report(data, 16 * 1024 ** 3, "linux_meminfo", "Linux")

    def test_no_host_identifiers(self):
        result = report(self.data, 8 * 1024 ** 3, "linux_meminfo", "Linux")
        serialized = json.dumps(result)
        for sensitive in ("hostname", "serial_number", "username", "mac_address"):
            self.assertNotIn(sensitive, serialized)


if __name__ == "__main__":
    unittest.main()
