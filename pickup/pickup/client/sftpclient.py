import paramiko
import sys

class SFTPClient:
    def __init__(self, client: paramiko.SFTPClient) -> None:
        self._client = client

    def chmod(self, file: str, mode: int) -> None:
        """Change the mode (permissions) of a file.

        Args:
            file (str): A file system path
            mode (int): A file mode
        """
        self._client.chmod(file, mode)

    def chown(self, file: str, uid: int, gid: int) -> None:
        """Change owner of a file.

        Args:
            file (str): A file system path
            uid (int): A user ID
            gid (int): A group ID
        """
        self._client.chown(file, uid, gid)

    def close(self) -> None:
        """Close the SFTP client connection."""
        self._client.close()

    def listdir(self, dir: str) -> list:
        """List entries in a directory.

        Args:
            dir (str): A file system path

        Returns:
            list: Entries in the directory.
        """
        return self._client.listdir(dir)

    def open(self, file: str, mode: str ) -> paramiko.sftp_handle.SFTPHandle:
        """Open a file on the remote host.

        Args:
            file (str): A file system path
            mode (str): Mode to open the file in

        Returns:
            paramiko.sftp_handle.SFTPHandle: The file handle.
        """
        return self._client.open(file, mode)

    def stat(self, file: str) -> paramiko.sftp_attr.SFTPAttributes:
        """Retrieve information about a file on the remote host.

        Args:
            file (str): A file system path


        Returns:
            paramiko.sftp_attr.SFTPAttributes: The file attributes.
        """
        return self._client.stat(file)
