from pickup.client.sshclient import SSHClient
from .resource import Resource

class Shell(Resource):
    def __init__(self, **kwargs) -> None:
        assert kwargs["type"] == "Shell"
        super().__init__(**kwargs)
        self._command = kwargs["command"]

    def _converge_run(self, client: SSHClient) -> int:
        """Run a shell command.

        Args:
            client (SSHClient): SSH client

        Returns:
            int: Set to 0 if command ran successfully. Set to non-zero if an error occurred.
        """
        cmd = "{}".format(self._command)
        exit_status, stdin, stdout, stderr = client.run(cmd, self._env, self._scope == "not_if")
        return exit_status
