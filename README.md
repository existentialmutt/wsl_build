# WSL Build

This Sublime Text Package facilitates writing custom builds for projects running in WSL2. It adds a "wsl_exec" target for build commands that does the following:

- execute Linux commands
- provides Linux paths in variables such as $file
- properly set ENV variables for Linux commands

For more information about defining Sublime Text builds see [the official documentation](https://www.sublimetext.com/docs/build_systems.html)

## Defining a Build
set `"target": "wsl_exec"`

### Required Keys
Set `"wsl_cmd"` instead of `"cmd"`.  The command array will be executed through WSL.
Build variables such as `$file` will have Linux paths.

### Optional Keys
Set `"wsl_working_dir"` instead of `"working_dir"`. Build variables such as `$file` will have Linux paths.

Set `"wsl_env"` instead of `"env"` to set environment variables that are available to
the Linux command. Build variables such as `$file` will have Linux paths.

### Example Builds for a Rails app in WSL:
```json
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
```

## Acknowledgments
Inspired by OdatNurd's technique here https://github.com/STealthy-and-haSTy/SublimeScraps/blob/master/build_enhancements/custom_build_variables.py
