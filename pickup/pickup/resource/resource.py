from pickup.client.sshclient import SSHClient
import sys

class Resource:
    def __init__(self, **kwargs) -> None:
        self._action = kwargs["action"]
        self._type = kwargs["type"]
        self._scope = kwargs["scope"]
        if "env" in kwargs:
            self._env = kwargs["env"]
        else:
            self._env = {}
        if "name" in kwargs and kwargs["name"]:
            self._name = kwargs["name"]
        else:
            self._name = ".".join([kwargs["scope"], kwargs["type"], kwargs["action"]])
        if "not_if" in kwargs:
            self._not_if = kwargs["not_if"]
        else:
            self._not_if = []
        if "after" in kwargs:
            self._after = kwargs["after"]
        else:
            self._after = []

    def converge(self, client: SSHClient) -> int:
        if self._scope != "not_if":
            print("")
            msg = "Converging resource: {}".format(self._name)
            print(msg)
            print("-" * len(msg))
        # Evaluate "not_if" conditions.
        if self._not_if:
            skip = True
        else:
            skip = False
        for resource in self._not_if:
            if resource.converge(client) != 0:
                skip = False
        if skip:
            self.skip("not_if")
            return 0
        # Convergence current resource.
        method = '_converge_' + self._action
        converge = getattr(self, method)
        exit_status = converge(client)
        if exit_status != 0 and self._scope != "not_if":
            sys.exit("Error: resource failed to converge")
        # Converge "after" resources.
        for resource in self._after:
            if resource.converge(client) != 0:
                sys.exit("Error: resource failed to converge")
        return exit_status

    def skip(self, reason: str="") -> None:
        msg = "Skipped {}".format(self._name)
        if reason:
            msg += ": {}".format(reason)
        print(msg)
