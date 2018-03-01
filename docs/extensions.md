# Extensions

Pomito can be extended by authoring `plugin` and `hooks`.
* Plugins provide specific functionality for the app. Currently `ui` and `task`
  plugins are supported. `UI` plugins provides a user interface for the
  application, and the `Task` plugins integrate various todo applications with
  pomito.
* Hooks, on the other hand are listeners to various events in pomito. The
  application is not dependent on hooks for any functionality. However these are
  helpful in various reactionary work, e.g. recording activities, running
  scripts on pomodoro start/stop etc..

## Configuring Extensions

Extensions are configured with `[<type>.<name>]` section. For example, note how
`trello` task plugin is configured below.

```
[plugins]
source = ["myplugin"]
ui = MyUIPlugin
task = Trello

[task.trello]
api_key = xyz
```

### Plugins section
* `packages` is a list of extra plugin packages. Pomito will try to load them
  and invoke the `register` function.
* `ui` setting configures the UI plugin.
* `task` setting configures the Task plugin.

## How extensions work?

Every extension module provides a `register` function.

```python
def register(pomodoro_service):
    # Pass pomodoro_service to the plugins, they could subscribe to any
    # signals in the service.
    ui_plugin = MyUIPlugin(pomodoro_service)
    task_plugin = MyTaskPlugin(pomodoro_service)

    pomodoro_service.register("name", ui_plugin)
    pomodoro_service.register("name", task_plugin)
```

## Writing a Plugin

## Writing a Hook
