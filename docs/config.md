# Configuration

Let's look at customizing pomito.

## Settings store

Pomito stores the configuration and data in a user specific location.

| OS      | Configuration Directory           | Data Directory                       |
|---------|-----------------------------------|--------------------------------------|
| Linux   | `$XDG_CONFIG_HOME` or `~/.config` | `$XDG_DATA_HOME` or `~/.local/share` |
| Windows | `~` or `%USER_PROFILE%`           | `~` or `%USER_PROFILE%`              |

Configuration is stored in `CONFIG_DIR/pomito/config.ini`. Usually
`~/.config/pomito/config.ini` on Linux and `~\pomito\config.ini` on Windows.

Pomodoro data is stored in `DATA_DIR/pomito/pomito.db`. Usually
`~/.local/share/pomito/pomito.db` on Linux and `~\pomito\pomito.db` on Windows.

## User settings

Pomito can be configured in the user interface.

## Configuration file

If you feel at home with command line, you can directly modify the configuration
file. Pomito reads the configuration file at startup. Any edits to the
configuration file will be loaded in the next startup.

Given below is a reference configuration file.

```ini
# Configuration for Pomito

[pomito]
# Duration of a pomodoro session (in minutes). Default = 25
session_duration = 25
# Duration of break in between sessions (in minutes). Default = 5
short_break_duration = 5
# Duration of long break after 4 continuous sessions (in minutes). Default = 15
long_break_duration = 15
# Take a long break after <value> continuous sessions. Default = 4
long_break_frequency = 4

[plugins]
# Specify the default "ui" plugin. This string must match the __plugin_name metadata
ui = qtapp
# Specify the default "task" plugin. This string must match the __plugin_name metadata
task = text

[task.text]
file = "c:\users\me\pomito\todo.txt"
```
