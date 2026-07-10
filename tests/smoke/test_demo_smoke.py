"""
Smoke test to verify the demo workflow produces expected outputs.
This ensures we catch regressions early.
"""
import sys
import subprocess
import json


def test_demo_workflow_smoke():
    """
    Smoke test that runs the full workflow demo and verifies key outputs.
    This ensures the decision engine selects an option and completes successfully.
    """
    result = subprocess.run(
        [sys.executable, "-m", "demo.full_workflow_demo"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    
    output = result.stdout
    
    assert "Status: decided" in output, f"Decision engine should report 'decided' status. Output: {output}"
    assert "Selected: " in output, f"Should have selected an option. Output: {output}"
    assert "Selected: None" not in output, f"Should not select 'None'. Output: {output}"
    assert "Execution Intent: True" in output, f"Should create execution intent. Output: {output}"
    assert "Execution Status: success" in output, f"Execution should succeed. Output: {output}"
    assert result.returncode == 0, f"Demo should exit with code 0. Got: {result.returncode}"


if __name__ == "__main__":
    test_demo_workflow_smoke()
    print("Smoke test passed!")