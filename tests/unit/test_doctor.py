import pytest
from octopus.doctor import (
    CheckStatus,
    CheckResult,
    BaseChecker,
    SystemChecker,
    DependencyChecker,
    ConfigurationChecker,
    NetworkChecker,
    Doctor,
)


class TestCheckStatus:
    def test_check_status_values(self):
        assert CheckStatus.PASSED.value == "passed"
        assert CheckStatus.FAILED.value == "failed"
        assert CheckStatus.WARNING.value == "warning"
        assert CheckStatus.SKIPPED.value == "skipped"


class TestCheckResult:
    def test_to_dict(self):
        result = CheckResult(
            check_id="test_1",
            name="Test Check",
            status=CheckStatus.PASSED,
            message="Success",
            details={"key": "value"},
        )
        data = result.to_dict()
        assert data["check_id"] == "test_1"
        assert data["name"] == "Test Check"
        assert data["status"] == "passed"
        assert data["message"] == "Success"
        assert data["details"] == {"key": "value"}
        assert "timestamp" in data


class TestBaseChecker:
    def test_run(self):
        checker = BaseChecker()
        results = checker.run()
        assert isinstance(results, list)
        assert len(results) == 0


class TestSystemChecker:
    def test_run_checks(self):
        checker = SystemChecker()
        results = checker.run()
        assert len(results) >= 4

    def test_python_version(self):
        checker = SystemChecker()
        results = checker.run()
        python_result = [r for r in results if r.check_id == "python_version"][0]
        assert python_result.status in [CheckStatus.PASSED, CheckStatus.FAILED]

    def test_operating_system(self):
        checker = SystemChecker()
        results = checker.run()
        os_result = [r for r in results if r.check_id == "operating_system"][0]
        assert os_result.status == CheckStatus.PASSED

    def test_environment_variables(self):
        checker = SystemChecker()
        results = checker.run()
        env_result = [r for r in results if r.check_id == "environment_variables"][0]
        assert env_result.status == CheckStatus.PASSED

    def test_disk_space(self):
        checker = SystemChecker()
        results = checker.run()
        disk_result = [r for r in results if r.check_id == "disk_space"][0]
        assert disk_result.status in [CheckStatus.PASSED, CheckStatus.WARNING, CheckStatus.FAILED, CheckStatus.SKIPPED]

    def test_memory_usage(self):
        checker = SystemChecker()
        results = checker.run()
        memory_result = [r for r in results if r.check_id == "memory_usage"][0]
        assert memory_result.status in [CheckStatus.PASSED, CheckStatus.SKIPPED]


class TestDependencyChecker:
    def test_run_checks(self):
        checker = DependencyChecker()
        results = checker.run()
        assert len(results) > 0

    def test_required_packages(self):
        checker = DependencyChecker()
        results = checker.run()
        pkg_results = [r for r in results if r.check_id.startswith("pkg_")]
        assert len(pkg_results) > 0

    def test_check_package_installed(self):
        checker = DependencyChecker()
        result = checker._check_package("os", ">=1.0.0")
        assert result.status == CheckStatus.PASSED

    def test_check_package_not_installed(self):
        checker = DependencyChecker()
        result = checker._check_package("nonexistent_package_xyz_123", ">=1.0.0")
        assert result.status == CheckStatus.FAILED


class TestConfigurationChecker:
    def test_run_checks(self):
        checker = ConfigurationChecker()
        results = checker.run()
        assert len(results) >= 3

    def test_config_files(self):
        checker = ConfigurationChecker()
        results = checker.run()
        config_results = [r for r in results if r.check_id.startswith("config_")]
        assert len(config_results) > 0

    def test_logging_config(self):
        checker = ConfigurationChecker()
        results = checker.run()
        logging_result = [r for r in results if r.check_id == "logging_config"][0]
        assert logging_result.status == CheckStatus.PASSED

    def test_data_directories(self):
        checker = ConfigurationChecker()
        results = checker.run()
        data_results = [r for r in results if r.check_id.startswith("data_")]
        assert len(data_results) > 0


class TestNetworkChecker:
    def test_run_checks(self):
        checker = NetworkChecker()
        results = checker.run()
        assert len(results) >= 2

    def test_internet_connectivity(self):
        checker = NetworkChecker()
        results = checker.run()
        net_result = [r for r in results if r.check_id == "internet_connectivity"][0]
        assert net_result.status in [CheckStatus.PASSED, CheckStatus.WARNING]

    def test_dns_resolution(self):
        checker = NetworkChecker()
        results = checker.run()
        dns_result = [r for r in results if r.check_id == "dns_resolution"][0]
        assert dns_result.status in [CheckStatus.PASSED, CheckStatus.WARNING]


class TestDoctor:
    def test_run_all(self):
        doctor = Doctor()
        results = doctor.run_all()
        assert len(results) > 0

    def test_run_checker(self):
        doctor = Doctor()
        results = doctor.run_checker("SystemChecker")
        assert len(results) > 0

    def test_run_checker_not_found(self):
        doctor = Doctor()
        with pytest.raises(ValueError):
            doctor.run_checker("NonexistentChecker")

    def test_get_summary(self):
        doctor = Doctor()
        results = doctor.run_all()
        summary = doctor.get_summary(results)
        assert "total_checks" in summary
        assert "passed" in summary
        assert "failed" in summary
        assert "overall_status" in summary

    def test_format_json(self):
        doctor = Doctor()
        results = doctor.run_all()
        json_output = doctor.format_results(results, "json")
        assert isinstance(json_output, str)
        assert "results" in json_output

    def test_format_text(self):
        doctor = Doctor()
        results = doctor.run_all()
        text_output = doctor.format_results(results, "text")
        assert isinstance(text_output, str)
        assert "Octopus Doctor" in text_output

    def test_format_rich(self):
        doctor = Doctor()
        results = doctor.run_all()
        rich_output = doctor.format_results(results, "rich")
        assert rich_output == ""