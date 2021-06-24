# pickup

Pickup is a simple configuration management tool that uses SSHv2 and SFTP protocols to make a host's configuration match the desired configuration supplied by the user.

## Install

Run `bootstrap.sh` to install dependencies needed to run Pickup. Pickup only officially supports Ubuntu 18.04 based systems.

## Architecture

Pickup is written using Python 3 and is implemented as a Python module package located at `./pickup/pickup/pickup.py`. A second entry point to Pickup is located at `./pickup/__main__.py` so that Pickup can be run using the command `python3 pickup <config>`, instead of `python3 pickup/pickup.py <config>`, for the user's convenience.

## Architecture: Steps and Configuration

Pickup reads steps provided by the user via a configuration file passed as a CLI argument. The configuration file must contain valid YAML data. Pickup parses the configuration file content, which is expected to produce a list of dictionaries. Each dictionary is treated as a single "step" in the process of configuring the host.

## Architecture: SSH and SFTP

Each step in the configuration is applied to the server using Python implementations of one or both of SSHv2 and SFTP protocols. Pickup uses clients provided by [Paramiko](https://github.com/paramiko/paramiko) to connect to the host using these protocols. Each Paramiko client is wrapped in a pair of lightweight wrapper classes `pickup.client.SSHClient` and `pickup.client.SFTPClient` located in `./pickup/pickup/client/`. From a development perspective, these wrapper classes help hide the implementation details of Paramiko behind a simpler interface. Furthermore, the wrapper classes will reduce how much code would need to be refactored if Pickup were to start using implementations of SSH or SFTP different from Paramiko's implementations.

## Architecture: Resources and Actions

Each step is instantiated as a "resource" object of a class inheriting from `pickup.resource.Resource`. Pickup determines which class it should instantiate based on the value of the `type` item in the step (dictionary). Support for more resources can be added to Pickup by creating a new class called `<Type>` in `./pickup/pickup/resource/<type>.py` and an `import` statement in `./pickup/pickup/resource/__init__.py`. Pickup decides which "action" to perform using the `_action` property of each resource object to dynamically call the object's `_converge_<action>` method. Support for new actions can be added to resources by adding a new method `_converge_<action>` to the resource's class. Some actions, such as the action `install` of the `DebPackage` resource, are idempotent out of the box whereas other actions, such as the action `run` of the `Shell` resource, can be made idempotent using the `not_if` property.

When a `_converge_<action>` method of a resource object is invoked, the `pickup.client.SSHClient` instance is passed to the method as an argument. The method can then use the client to run commands on the host using SSHv2 protocol or open an SFTP connection and interact with the host's file system.

## Usage

You can run Pickup using Python 3. Replace `<config>` with the path of your YAML configuration file. For more information about the environment variables see [Usage: Configuration](#usage-configuration).

```
export PICKUP_HOST=<host>
export PICKUP_PORT=<port>
export PICKUP_USERNAME=<username>
export PICKUP_PASSWORD=<password>

python3 pickup <config>
```

## Usage: Configuration

The settings used to establish SSH and SFTP connections with the host can be configured using the environment variables below.

#### `PICKUP_HOST`

The IP address or DNS name of the host.

#### `PICKUP_PORT`

The port to connect to.

#### `PICKUP_USERNAME`

The username to authenticate as.

#### `PICKUP_PASSWORD`

The password to authenticate with.

## Usage: Steps

A Pickup configuration file must contain one or more steps. Each step is represented as a dictionary and all of the steps together make up a list. This list of steps goes under the `steps` dictionary.

```
# sample-config.yaml
steps:
  - name: hello
    type: Shell
    action: run
    command: echo Hello!
  - name: goodbye
    type: Shell
    action: run
    command: echo Goodbye!
```

Each step represents a different resource or action that should be configured on or applied to the host. All steps support the below keys.

#### `type`

The type of resource to configure.

For more information about which resources Pickup supports jump to [Usage: DebPackage](#usage-debpackage).

#### `action`

The action to take on the resource.

#### `name`

The name of the step. Pickup's output will look best if the name is formatted according to the kebab case naming convention (ex. `my-step`).

#### `env`

Environment variables to merge into the host's default execution environment.

#### `not_if`

Skip taking action on the resource if any `not_if` steps fail (exit code is non-zero). `not_if` takes a list of steps that follow the same format as the top-level `steps` takes.

```
# sample-config.yaml
steps:
  - name: good-morning
    type: Shell
    action: run
    command: echo "Good morning!"
    not_if:
      - type: Shell
        command: "[ `date +%H` -lt 12 ]"
        action: run
  - name: good-afternoon
    type: Shell
    action: run
    command: echo "Good afternoon!"
    not_if:
      - type: Shell
        command: "[ `date +%H` -gt 11 ] && [ `date +%H` -lt 18 ]"
        action: run
  - name: good-night
    type: Shell
    action: run
    command: echo "Good night!"
    not_if:
      - type: Shell
        command: "[ `date +%H` -gt 17 ] && [ `date +%H` -lt 24 ]"
        action: run
```

#### `after`

Steps to perform after the resource has been configured. The `after` steps will only be performed if the resource was not skipped by a `not_if` step and the resource was successfully configured. `after` takes a list of steps that follow the same format as the top-level `steps` takes.

```
# sample-config.yaml
steps:
  - name: hello
    type: Shell
    action: run
    command: echo Hello!
    after:
      - name: goodbye
        type: Shell
        action: run
        command: echo Goodbye!
```

## Usage: DebPackage

The `DebPackage` resource supports two actions: `install` and `remove`.

In addition to the base fields supported by all steps, `DebPackage` also supports the additional fields below.

#### `package`

The name of the package.

## Usage: File

The `File` resource supports two actions: `create` and `delete`.

In addition to the base fields supported by all steps, `File` also supports the additional fields below.

### `create` Action Only

#### `source`

A file in the local file system containing the desired content.

#### `destination`

The path where the file should be created in the remote file system.

#### `mode`

The mode (permissions) the file should have (ex. `0755`).

#### `group`

The group the file should be owned by. The value can be the group's ID or name.

#### `owner`

The user the file should be owned by. The value can be the user's ID or name.

### `delete` Action Only

#### `file`

The path of the file in the remote file system.

## Usage: Service

The `Service` resource supports one action: `restart`.

In addition to the base fields supported by all steps, `Service` also supports the additional fields below.

#### `service`

The name of the service.

## Usage: Shell

The `Shell` resource supports one action: `run`.

In addition to the base fields supported by all steps, `Shell` also supports the additional fields below.

#### `command`

The shell command.
