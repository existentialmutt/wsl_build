# WSL Build

This Sublime Text Package facilitates writing custom builds for projects running in WSL2. It adds a `wsl_exec` target for build commands that does the following:

- execute Linux commands
- provides Linux paths in variables such as $file
- properly set ENV variables for Linux commands

For more information about defining Sublime Text builds see [the official documentation](https://www.sublimetext.com/docs/build_systems.html)

## Defining a Build

Set `"target": "wsl_exec"` and `"cancel": {"kill": true}` to be able to cancel a command.

### Required Keys

#### wsl_cmd

Set `"wsl_cmd"` instead of `"cmd"`.  The command array will be executed through WSL.

> **Note**
> 
> Build variables such as $file have a $unix_file counter part with unix style paths.

### Optional Keys

#### wsl_working_dir

Set `"wsl_working_dir"` instead of `"working_dir"`.

> **Note**
> 
> Build variables such as $file have a $unix_file counter part with unix style paths.

#### wsl_env

Set `"wsl_env"` instead of `"env"` to set environment variables that are available to
the Linux command.

> **Note**
> 
> Build variables such as $file have a $unix_file counter part with unix style paths.

Environment variables can be suffixed by conversion flags
to specify how their values are treated by WSL.

| flag | description
|:----:| ---
| `/p` | This flag indicates that a path should be translated between WSL paths and Win32 paths. Notice in the example below how we set the var in WSL, add it to WSLENV with the `/p` flag, and then read the variable from cmd.exe and the path translates accordingly.
| `/l` | This flag indicates the value is a list of paths. In WSL, it is a colon-delimited list. In Win32, it is a semicolon-delimited list.
| `/u` | This flag indicates the value should only be included when invoking WSL from Win32.
| `/w` | Notice how it does not convert the path automatically—we need to specify the /p flag to do this.

#### Example:
  
    "MY_PATH/p": "C:\\Path\\to\\File"

is converted to:

1. `MY_PATH=/mnt/c/Path/to/File` when running unix commands
2. `MY_PATH=C:\\Path\\to\\File` when running windows commands

### Example Builds for a Rails app in WSL:

```json
"build_systems": [
    {
        "name": "🧪 Run Current Spec",
        "target": "wsl_exec",
        "cancel": {"kill": true},
        "wsl_cmd": [
            "bundle", "exec", "rake", "spec" 
        ],
        "wsl_env": {
            "SPEC/p": "$file"
        },
        "wsl_working_dir": "$unix_folder"
    },
    {
        "name": "🧪 Run All Specs",
        "target": "wsl_exec",
        "cancel": {"kill": true},
        "wsl_cmd": [
            "bundle", "exec", "rake", "spec"
        ],
        "wsl_working_dir": "$unix_folder",
    },
    {
        "name": "🗃️ Run Database Migrations",
        "target": "wsl_exec",
        "cancel": {"kill": true},
        "wsl_cmd": [
            "bundle", "exec", "rake", "db:migrate"
        ],
        "wsl_working_dir": "$unix_folder"
    }
]
```

## Variables

### Default Varables

All default variables are provided in unconverted form
in case a windows command is being executed within WSL2.

| variable              | description
| ---                   | ---
| `$packages`           | The path to the _Packages/_ folder.
| `$platform`           | The platform Sublime Text is running on: "windows", "osx" or "linux".
| `$file`               | The full path, including folder, to the file in the active view.
| `$file_path`          | The path to the folder that contains the file in the active view.
| `$file_name`          | The file name (sans folder path) of the file in the active view.
| `$file_base_name`     | The file name, exluding the extension, of the file in the active view.
| `$file_extension`     | The extension of the file name of the file in the active view.
| `$folder`             | The full path to the first folder open in the side bar.
| `$project`            | The full path to the current project file.
| `$project_path`       | The path to the folder containing the current project file.
| `$project_name`       | The file name (sans folder path) of the current project file.
| `$project_base_name`  | The file name, excluding the extension, of the current project file.
| `$project_extension`  | The extension of the current project file.

see: https://www.sublimetext.com/docs/build_systems.html#variables

### Unix Variables

Converted path variables are provided for unix commands being executed within WSL.

| variable (unix style) | oringinal variable (windows style)
| ---                   | ---
| `$unix_file`          | `$file`
| `$unix_file_path`     | `$file_path`
| `$unix_folder`        | `$folder`
| `$unix_packages`      | `$packages`
| `$unix_project`       | `$project`
| `$unix_project_path`  | `$project_path`

## Acknowledgments

Inspired by OdatNurd's technique here https://github.com/STealthy-and-haSTy/SublimeScraps/blob/master/build_enhancements/custom_build_variables.py
