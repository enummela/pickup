from pickup.client.sftpclient import SFTPClient
import paramiko
import sys

class SSHClient:
    def connect(self, hostname: str, username: str, password: str, port: int=22) -> paramiko.SSHClient:
        """Connect to host via SSH using Paramiko SSH client

        Args:
            hostname (str): IP address or DNS name of the host
            username (str): Username to authenticate as
            password (str): Password to authenticate with
            port (int, optional): Port to connect to. Defaults to 22.

        Returns:
            paramiko.SSHClient: SSH client
        """
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(hostname=hostname, username=username, password=password, port=port)
        except paramiko.ssh_exception.AuthenticationException as err:
            sys.exit("Error: failed to authenticate with host. Check if the provided connection settings are correct.")
        except paramiko.ssh_exception.SSHException as err:
            sys.exit("Error: failed to connect to host. Check if the provided connection settings are correct and if the host is reachable over SSH.")
        self._ssh_client = ssh_client

    def run(self, cmd: str, env: dict={}, quiet=False) -> "tuple[int, paramiko.channel.ChannelStdinFile, paramiko.channel.ChannelFile, paramiko.channel.ChannelStderrFile]":
        """Run command on host using Paramiko SSH client.

        Parameters:
            cmd (str): Command to run
            env (dict): Environment variables to be merged with host's default environment
            quiet (bool): Set to true to disable writing command output to stdout

        Returns:
            tuple: A tuple containing the command's exit status, stdin, stdout, and stderr
        """
        env_str = "\n".join(["export {}={}".format(k, v) for k, v in env.items()])
        cmd_ = env_str + "\n" + cmd
        if not quiet:
            print(cmd)
        # Setting "get_pty" to "True" combines stdout and stderr in stdout
        stdin, stdout, stderr = self._ssh_client.exec_command(cmd_, get_pty=True)
        if not quiet:
            print("".join(stdout.readlines()))
        exit_status = stdout.channel.recv_exit_status()
        return exit_status, stdin, stdout, stderr

    def open_sftp(self) -> SFTPClient:
        """Open an SFTP connection on the host

        Returns:
            SFTPClient: SFTP client
        """
        client = self._ssh_client.open_sftp()
        return SFTPClient(client)

    def close(self):
        """Close the SSH connection"""
        self._ssh_client.close()
