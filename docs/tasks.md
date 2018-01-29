# Task Integrations

Pomito can link your pomodoros to a task you're working on. It connects to
various _todo_ applications to fetch the tasks. This section will help you
integrate your favorite todo app with pomito.

Refer to [configuration][config.md] section for more details on location of
configuration file and supported sections.

## Trello

Trello integration requires following settings in `config.ini`.

```ini
[plugins]
task = trello

[task.trello]
api_key = abcdef123456789abcdef123456789ab
api_secret = abcdef123456789abcdef123456789abaabcdef123456789abcdef123456789a
board = Work
list = Today
```

* Get the `api_key` from the Trello [developer page][trello-dev] (see **Developer API Keys** section). 
* For `api_secret` you've to replace `REPLACE_ME` in below url and open it in a
  browser:
  ```
  https://trello.com/1/authorize?expiration=never&scope=read,write,account&response_type=token&name=Server%20Token&key=REPLACE_ME
  ```
* `board` is the Trello board to connect
* And `list` is a Trello list inside above board. Pomito will show all tasks
  from this list for linking with a pomodoro

[trello-dev]: https://trello.com/app-key
