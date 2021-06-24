from pickup.client.sshclient import SSHClient
from .resource import Resource

class DebPackage(Resource):
    def __init__(self, **kwargs) -> None:
        assert kwargs["type"] == "DebPackage"
        super().__init__(**kwargs)
        if "package" in kwargs:
            self._package = kwargs["package"]
        else:
            self._package = kwargs["name"]

    def _converge_install(self, client: SSHClient) -> int:
        """Install a Debian package if not already installed.

        Args:
            client (SSHClient): SSH client

        Returns:
            int: Set to 0 if package has converged to the desired state. Set to non-zero if an erorr occurred.
        """
        if self._package_installed(client):
            self.skip("package already installed")
            return 0
        cmd = "apt-get install -y {}".format(self._package)
        exit_status, stdin, stdout, stderr = client.run(cmd, self._env)
        return exit_status

    def _converge_remove(self, client: SSHClient) -> int:
        """Remove a Debian package if installed.

        Args:
            client (SSHClient): SSH client

        Returns:
            int: Set to 0 if package has converged to the desired state. Set to non-zero if an erorr occurred.
        """
        if not self._package_installed(client):
            self.skip("package not installed")
            return 0

        cmd = "apt-get --purge autoremove -y {}".format(self._package)
        exit_status, stdin, stdout, stderr = client.run(cmd, self._env)
        return exit_status

    def _package_installed(self, client: SSHClient) -> bool:
        """Check if a Debian package is installed.

        Args:
            client (SSHClient): SSH client

        Returns:
            bool: Set to 0 if package is installed. Set to non-zero if package is not installed or an error occurred.
        """
        cmd = "dpkg-query -W --showformat='${{Status}}\n' {} | grep 'install ok installed'"
        exit_status, stdin, stdout, stderr = client.run(cmd.format(self._package), quiet=True)
        return exit_status == 0
