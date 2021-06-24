import pickup.client
import pickup.resource as resources
import os
import sys
import yaml

def mk_resource(step: dict, scope: str) -> pickup.resource.Resource:
    """Make a resource object as specified in the step from the configuration.

    Args:
        step (dict): Specification of the resource object.
        scope (str): Scope of the resource specification inside the configuration.

    Returns:
        pickup.resource.Resource: A resource object.
    """
    after = []
    not_if = []
    resource = None
    step_ = {k: v for k, v in step.items() if k != "after" and k != "not_if"}
    if "after" in step:
        after = [mk_resource(step__, "after") for step__ in step["after"]]
    if "not_if" in step:
        not_if = [mk_resource(step__, "not_if") for step__ in step["not_if"]]
    # Create new resource.
    class_ = getattr(resources, step["type"])
    return class_(after=after, not_if=not_if, scope=scope, **step_)

def main(args: list) -> None:
    """Make the remote host converge on the desired state specified in the configuration.

    Args:
        args (list): CLI arguments passed to the application.
    """
    num_args = len(args)
    if num_args != 1:
        sys.exit("Error: expected 1 argument but recieved {}".format(num_args))
    if not os.path.isfile(args[0]):
        sys.exit("Error: configuration file does not exist")

    config = {}
    steps = []

    with open(args[0], "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as err:
            sys.exit(err)

    host = os.getenv("PICKUP_HOST", "localhost")
    port = int(os.getenv("PICKUP_PORT", "22"))
    user = os.getenv("PICKUP_USERNAME", "")
    pw = os.getenv("PICKUP_PASSWORD", "")
    ssh_client = pickup.client.SSHClient()
    print("Connecting to remote host {} over port {} as user {}.".format(host, port, user))
    ssh_client.connect(host, username=user, password=pw, port=port)
    print("Successfully connected to remote host.")

    for step in config["steps"]:
        steps.append(mk_resource(step, "steps"))

    for resource in steps:
        if resource.converge(ssh_client) != 0:
            sys.exit("Error: step failed")

    print("")
    print("Success: all resources have converged to the desired state.")

    ssh_client.close()
    # Exit gracefully. 
    sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])
