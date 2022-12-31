import re
import sublime

from Default.exec import ExecCommand


class WslExecCommand(ExecCommand):
    """
    The class defines a `wsl_exec` sublime build system target to run commands via WSL2.

    - execute Linux commands
    - provides Linux paths in variables such as $file
    - properly set ENV variables for Linux commands

    DEFAULT EXEC VARIABLES
    ===

    Unconverted variables with window file paths are provided
    in case a windows command is being executed within WSL2.

    - `$file`
    - `$file_base_name`
    - `$file_extension`
    - `$file_name`
    - `$file_path`
    - `$folder`
    - `$packages`
    - `$project`
    - `$project_base_name`
    - `$project_extension`
    - `$project_name`
    - `$project_path`
    - `$platform`

    UNIX EXEC VARIABLES
    ===

    Converted path variables are provided for unix commands being executed within WSL.

    - `$unix_file` - unix style `$file`
    - `$unix_file_path` - unix style `$file_path`
    - `$unix_folder` - unix style `$folder`
    - `$unix_packages` - unix style `$packages`
    - `$unix_project` - unix style `$project`
    - `$unix_project_path` - unix style `$project_path`

    REQUIRED PARAMETERS
    ===

    wsl_cmd
    ---

    Set `wsl_cmd` instead of `cmd`.  The command array will be executed through WSL.
    Build variables such as $file have a $unix_file counter part with unix style paths.

    OPTIONAL PARAMETERS
    ===

    wsl_working_dir
    ---

    Set `wsl_working_dir` instead of `working_dir`.
    Build variables such as $file have a $unix_file counter part with unix style paths.

    wsl_env
    ---

    Set `wsl_env` instead of `env` to set environment variables that are available to
    the Linux command. Build variables such as $file will have Linux paths.

    Environment variables can be terminated by conversion flags to specify how their values
    are treated by WSL.

        Example:
            "MY_PATH/p": "C:\\Path\\to\\File"

            is converted to:

            a) MY_PATH=/mnt/c/Path/to/File when running unix commands
            b) MY_PATH=C:\\Path\\to\\File when running windows commands

    `/p` flag
        This flag indicates that a path should be translated between WSL paths and
        Win32 paths. Notice in the example below how we set the var in WSL, add it
        to WSLENV with the `/p` flag, and then read the variable from cmd.exe and
        the path translates accordingly.

    `/l` flag
        This flag indicates the value is a list of paths. In WSL, it is a
        colon-delimited list. In Win32, it is a semicolon-delimited list.

    `/u` flag
        This flag indicates the value should only be included
        when invoking WSL from Win32.

    `/w` flag
        Notice how it does not convert the path automatically—we need to specify
        the /p flag to do this.

    Example Build Systems for a Rails app in WSL:
    ===

    ```jsonc
    "build_systems": [
        {
            "name": "🧪 Run Current Spec",
            "target": "wsl_exec",
            "wsl_cmd": [
                "bundle", "exec", "rake", "spec"
            ],
            "wsl_env": {
                "PLAIN": "untranslated",
                "SPEC": "$file",
                "LIST/l": "%PATH%",
                "PATH/p": "%USERPROFILE%",
                "UNIX/u": "~/",
                "WIN/w": "%USERPROFILE%"
            },
            "wsl_working_dir": "$unix_folder",
            "cancel": {"kill": true},
        },
        {
            "name": "🧪 Run All Specs",
            "target": "wsl_exec",
            "wsl_cmd": [
                "bundle", "exec", "rake", "spec"
            ],
            "wsl_working_dir": "$unix_folder",
            "cancel": {"kill": true},
        },
        {
            "name": "🗃️ Run Database Migrations",
            "target": "wsl_exec",
            "wsl_cmd": [
                "bundle", "exec", "rake", "db:migrate"
            ],
            "wsl_working_dir": "$unix_folder"
            "cancel": {"kill": true},
        }
    ```
    """

    def run(self, wsl_cmd, wsl_working_dir="", wsl_env=None, **kwargs):
        # Drop certain arguments, which should not be passed to super class
        wsl_args = {
            k: v for k, v in kwargs.items()
            if k not in {"env", "shell_cmd", "working_dir"}
        }

        # Translate command paramter to what exec expects
        wsl_args["cmd"] = self.wsl_cmd(wsl_cmd, wsl_working_dir)

        # Translate environment variables
        if wsl_env:
            wsl_args["env"] = self.wsl_env(wsl_env)

        # Add path variables converted to unix format
        variables = self.window.extract_variables()
        for var in {
            "file",
            "file_path",
            "folder",
            "packages",
            "project",
            "project_path",
        }:
            variables["unix_" + var] = self.wsl_path(variables[var])

        # Expanding variables in the arguments given
        wsl_args = sublime.expand_variables(wsl_args, variables)

        super().run(**wsl_args)

    def wsl_cmd(self, cmd, cwd):
        """
        Set working directory within WSL2 and prepend "wsl" command

        Working directory may be given in Windows and Unix style.

        Working directory must be set within WSL via `cd cwd` as normal
        `working_dir` doesn't work for paths within WSL environment
        which start with `\\\\wsl.localhost\\<distro>\\`.

        :param cmd:
            The shell command to execute in WSL2
        :param cwd:
            The working directory to set within WSL2

        :returns:
            The full wsl command value to execute.
        """
        wsl = ["wsl"]
        if cwd:
            wsl += ["cd", self.wsl_path(cwd), ";"]
        return wsl + cmd

    def wsl_env(self, env):
        """
        Publish environment variables to WSL

        The function sets `WSLENV` variable with colon separated list
        of variable names of `env` dictionary and adds it to returned
        `env` dictionary.

        It strips following conversion flags from environment variables.

        :param env:
            The environment variables to share with WSL
        :returns:
            A dict of environment variables to use to execute the command.
        """
        env["WSLENV"] = ":".join(env.keys())
        for key in list(env):
            if key[-2] == "/" and key[-1] in ("l", "p", "u", "w"):
                env[key[:-2]] = env.pop(key)
        return env

    def wsl_path(self, path):
        """
        Convert Windows path to Unix path

        :param path:
            The windows path string to convert

        :returns:
            The converted unix path string
        """
        # remove UNC prefix for paths pointing to WSL environment
        if path.startswith("\\\\"):
            path = re.sub(r"\\\\wsl\.localhost\\[^\\]*", "", path)
        # convert local windows paths to WSL compliant unix format
        elif path[1:3] == ":\\":
            path = "".join(("/mnt/", path[0].lower(), path[2:]))
        return path.replace("\\", "/")
