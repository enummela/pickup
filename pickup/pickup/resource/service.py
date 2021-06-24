from pickup.client.sshclient import SSHClient
from .resource import Resource

class Service(Resource):
    def __init__(self, **kwargs) -> None:
        assert kwargs["type"] == "Service"
        super().__init__(**kwargs)
        self._service = kwargs["service"]

    def _converge_restart(self, client: SSHClient) -> int:
        """Restart a service.

        Args:
            client (SSHClient): SSH client

        Returns:
            int: Set to 0 if service was restarted. Set to non-zero if an error occurred.
        """
        cmd = "service {} restart".format(self._service)
        exit_status, stdin, stdout, stderr = client.run(cmd, self._env)
        return exit_status
