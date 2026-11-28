from importlib import import_module


def test_sandbox_verifier_keeps_container_isolation_flags():
    docker_command = import_module("stages.05_sandbox_verifier.__main__").docker_command
    command = docker_command("/tmp/dreamco-test")
    assert command[command.index("--network") + 1] == "none"
    assert "--read-only" in command
    assert "--cap-drop=ALL" in command
    assert "--security-opt=no-new-privileges" in command
    assert command[command.index("--user") + 1] == "65532:65532"
