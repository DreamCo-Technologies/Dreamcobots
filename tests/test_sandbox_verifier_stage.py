from importlib import import_module


def test_sandbox_verifier_keeps_container_isolation_flags():
    docker_command = import_module("stages.05_sandbox_verifier.__main__").docker_command
    command = docker_command("/tmp/dreamco-test")
    assert command[command.index("--network") + 1] == "none"
    assert "--read-only" in command
    assert "--cap-drop=ALL" in command
    assert "--security-opt=no-new-privileges" in command
    assert command[command.index("--user") + 1] == "65532:65532"


def test_sandbox_report_omits_raw_container_stdout_and_stderr():
    source = (Path(__file__).resolve().parents[1] / "stages" / "05_sandbox_verifier" / "__main__.py").read_text(encoding="utf-8")
    assert '"output_omitted":True' in source
    assert "stdout_tail" not in source
    assert "stderr_tail" not in source
