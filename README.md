# CTFDumper

A tool for dumping CTFd challenges.

## Usage

```
usage: CTFDumper.py [-h] [-u USERNAME] [-p PASSWORD] [--auth-file AUTH_FILE]
                    [-n] [--no-file] [--trust-all] [-t TEMPLATE] [-v]
                    url

A tool for dumping CTFd challenges

positional arguments:
  url                   Platform URL

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Platfrom username
  -p PASSWORD, --password PASSWORD
                        Platform password
  --auth-file AUTH_FILE
                        File containing username and password, seperated by
                        newline
  -n, --no-login        Use this option if the platform does not require
                        authentication
  --no-file             Don't download files
  --trust-all           Will make directory as the name of the challenge, the
                        slashes(/) character will automatically be replaced
                        with underscores(_)
  -t TEMPLATE, --template TEMPLATE
                        Custom template path
  -v, --verbose         Verbose
```

## Template

The template is rendered with Jinja2.

For [this challenge](https://demo.ctfd.io/challenges#Hej), the template below

```
title: {{ challenge['name'] }}
value: {{ challenge['value'] }}
description: {{ challenge['description'] }}
```

Will generate the following output

```
title: Hej
value: 42
description: Hallo
```

## Notes

- Using `--auth-file` rather than typing your username/password in the command is consider safe.
- `--trust-all` allows non-ASCII characters to be the name of the directory.
