# CTFDumper

A tool for dumping CTFd challenges.

## Usage

```
usage: CTFDumper.py [-h] [-u USERNAME] [-p PASSWORD] [-n] [-t TEMPLATE] [-v]
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
  -n, --no-login        Use this option if the platform does not require
                        authentication
  -t TEMPLATE, --template TEMPLATE
                        Custom template path
  -v, --verbose         Verbose
```

## Template

The template is rendered with Jinja2.

For [this challenge](https://demo.ctfd.io/challenges#Hej), the template below

```
title: {{ challenge['name'] }}
description: {{ challenge['description'] }}
value: {{ challenge['value'] }}
```

Will generate the following output

```
title: Hej
description: Hallo
value: 42
```

## Notes

Store you `username` and `password` into a file and use ``python3 CTFDumper.py -u `cat username` -p `cat password` url`` is consider safe.
