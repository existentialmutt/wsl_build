import sublime, sublime_plugin, subprocess, re

from Default.exec import ExecCommand

"""
Adds a "wsl_exec" target for build commands that does the following:

- execute Linux commands
- provides Linux paths in variables such as $file
- properly set ENV variables for Linux commands

REQUIRED
Set "wsl_cmd" instead of "cmd".  The command array will be executed through WSL.
Build variables such as $file will have Linux paths.

OPTIONAL
Set "wsl_working_dir" instead of "working_dir".
Build variables such as $file will have Linux paths.

Set "wsl_env" instead of "env" to set environment variables that are available to
the Linux command. Build variables such as $file will have Linux paths.

Example Build Systems for a Rails app in WSL:
"build_systems": [
    {
        "name": "🧪 Run Current Spec",
        "target": "wsl_exec",
        "wsl_cmd": [
            "bundle", "exec", "rake", "spec" 
        ],
        "wsl_env": {
            "SPEC": "$file"
        },
        "wsl_working_dir": "$folder"
    },
    {
        "name": "🧪 Run All Specs",
        "target": "wsl_exec",
        "wsl_cmd": [
            "bundle", "exec", "rake", "spec"
        ],
        "wsl_working_dir": "$folder",
    },
    {
        "name": "🗃️ Run Database Migrations",
        "target": "wsl_exec",
        "wsl_cmd": [
            "bundle", "exec", "rake", "db:migrate"
        ],
        "wsl_working_dir": "$folder"
    }

"""
class WslExecCommand(ExecCommand):
    def run(self, **kwargs):
        # Convert path variables to their wsl version
        variables = self.window.extract_variables()
        variables["file"] = self.wsl_path(variables["file"])
        variables["file_path"] = self.wsl_path(variables["file_path"])
        variables["folder"] = self.wsl_path(variables["folder"])
        variables["project_path"] = self.wsl_path(variables["project_path"])


        # Create arguments to return by expanding variables in the
        # arguments given.
        args = sublime.expand_variables (kwargs, variables)

        # Rename the command paramter to what exec expects.
        args["cmd"] = ["wsl"] + args.pop("wsl_cmd", [])
        
        if "wsl_working_dir" in args:
            args["working_dir"] = args.pop("wsl_working_dir", [])
        
        if "wsl_env" in args:
            args["env"] = self.wsl_env(args.pop("wsl_env", []))

        super().run(**args)

    def wsl_path(self, string):
        prefix_removed = re.sub("\\\\\\\\wsl.localhost\\\\Ubuntu", "", string)
        return re.sub("\\\\", "/", prefix_removed)

    def wsl_env(self, dict):
        dict["WSLENV"] = ":".join(dict.keys())
        return dict
