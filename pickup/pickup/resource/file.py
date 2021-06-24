from pickup.client.sshclient import SSHClient
from pickup.client.sftpclient import SFTPClient
from .resource import Resource
import os

class File(Resource):
    def __init__(self, **kwargs) -> None:
        assert kwargs["type"] == "File"
        super().__init__(**kwargs)
        if "source" in kwargs:
            self._source = kwargs["source"]
        if "destination" in kwargs:
            self._destination = kwargs["destination"]
        if "file" in kwargs:
            self._file = kwargs["file"]
        if "group" in kwargs:
            self._group = kwargs["group"]
        if "mode" in kwargs:
            self._mode = kwargs["mode"]
        if "owner" in kwargs:
            self._owner = kwargs["owner"]

    def _converge_delete(self, client: SSHClient) -> int:
        """Delete a file if it exists.

        Args:
            client (SSHClient): SSH client

        Returns:
            int: Set to 0 if file has converged to the desired state. Set to non-zero if an erorr occurred.
        """
        sftp = client.open_sftp()

        if self._file_exists(sftp, self._file, self._file):
            print("Deleting file: {}".format(self._file))
            client.run("rm {}".format(self._file), quiet=True)
        else:
            self.skip("file already deleted: {}".format(self._file))
        return 0

    def _converge_create(self, client: SSHClient) -> int:
        """Create a file if it doesn't exist and update the file's metadata so it converges onto the desired state.

        Args:
            client (SSHClient): SSH client

        Returns:
            int: Set to 0 if file has converged to the desired state. Set to non-zero if an erorr occurred.
        """
        sftp = client.open_sftp()
        gid = uid = None
        skip = True

        # Converge file.
        if not self._file_exists(sftp, self._source, self._destination):
            print("Creating new file: {}".format(self._destination))
            client.run("touch {}".format(self._destination), quiet=True)
            skip = False
        else:
            print("File already exists: {}".format(self._destination))

        # Determine the group ID and owner ID.
        if not self._group.isdigit():
            gid = self._get_gid(client)
        else:
            gid = int(self._group)
        if not self._owner.isdigit():
            uid = self._get_uid(client)
        else:
            uid = int(self._owner)

        dest_stat = sftp.stat(self._destination)

        # Converge mode.
        if oct(dest_stat.st_mode)[-4:] != self._mode:
            print("Updating file mode: {} => 0{}".format(oct(dest_stat.st_mode)[-4:], int(self._mode, 8)))
            # Convert mode to base 8 representation (octal)
            mode = int(self._mode, 8)
            sftp.chmod(self._destination, mode)
            skip = False
        else:
            print("File already has correct mode: {}".format(self._mode))

        # Converge group and owner.
        if dest_stat.st_gid != gid or dest_stat.st_uid != uid:
            print("Updating file owner and group: {}:{} => {}:{}".format(uid, gid, self._owner, self._group))
            sftp.chown(self._destination, uid, gid)
            skip = False
        else:
            print("File already has correct owner and group: {}:{}".format(self._owner, self._group))

        # Converge content.
        if os.path.getsize(self._source) != dest_stat.st_size:
            print("Updating file content")
            self._file_write(sftp)
            skip = False
        else:
            with open(self._source, 'rb') as src:
                with sftp.open(self._destination, mode='rb') as dest:
                    if src.read() == dest.read():
                        print("File already has correct content")
                    else:
                        print("Updating file content")
                        self._file_write(sftp)
                        skip = False
        if skip: self.skip("file already converged to the desired state: {}".format(self._destination))
        sftp.close()
        return 0

    def _file_exists(self, sftp_client: SFTPClient, src: str, dest: str) -> bool:
        """Check if a file exists on a remote file system.

        Args:
            sftp_client (SFTPClient): SFTP client
            src (str): Path to file on host file system
            dest (str): Path to file on remote file system

        Returns:
            bool: Set to True if file exists.
        """
        return os.path.basename(src) in sftp_client.listdir(os.path.dirname(dest))

    def _get_gid(self, ssh_client: SSHClient) -> int:
        """Get the ID of a group on the remote host.

        Args:
            ssh_client (SSHClient): SSH client

        Returns:
            int: The group's ID.
        """
        cmd = "getent group {} | awk -F: '{{printf \"%d\",$3}}'".format(self._group)
        exit_status, stdin, stdout, stderr = ssh_client.run(cmd, quiet=True)
        return int("".join(stdout.readlines()).strip())

    def _get_uid(self, ssh_client: SSHClient) -> int:
        """Get the ID of a user on the remote host.

        Args:
            ssh_client (SSHClient): SSH client

        Returns:
            int: The user's ID.
        """
        cmd = "id -u {}".format(self._owner)
        exit_status, stdin, stdout, stderr = ssh_client.run(cmd, quiet=True)
        return int("".join(stdout.readlines()).strip())

    def _file_write(self, sftp_client: SFTPClient) -> None:
        """Make content in a file on a remote file system match content in a file on the host file system.

        Args:
            sftp_client (SFTPClient): SFTP client
        """
        with open(self._source, 'rb') as src:
            with sftp_client.open(self._destination, 'wb') as dest:
                dest.truncate(0)
                for line in src:
                    dest.write(line)
