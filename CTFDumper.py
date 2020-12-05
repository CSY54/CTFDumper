#!/usr/bin/env python3
banner = r'''
  ____ _____ _____ ____
 / ___|_   _|  ___|  _ \ _   _ _ __ ___  _ __   ___ _ __
| |     | | | |_  | | | | | | | '_ ` _ \| '_ \ / _ \ '__|
| |___  | | |  _| | |_| | |_| | | | | | | |_) |  __/ |
 \____| |_| |_|   |____/ \__,_|_| |_| |_| .__/ \___|_|
                                        |_|
'''
from argparse import ArgumentParser
from requests import Session
from requests.compat import urljoin, urlparse, urlsplit
from typing import Generator, List, Union
from jinja2 import Template
import logging
import logging.config
import re, os

CONFIG = {
    'username': None,
    'password': None,
	'nonce_regex': 'name="nonce"(?:[^<>]+)?value="([0-9a-f]{64})"',
    'base_url': None,
    'no_file': None,
    'no_login': None,
    'template': os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates/default.md'),
    'verbose': logging.INFO,
    'blacklist': r'[^a-zA-Z0-9_\-\. ]',
}

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
})

logger = logging.getLogger(__name__)
session = Session()

def welcome() -> None:
    logger.info(banner)

def setup() -> None:
    parser = ArgumentParser(description='A tool for dumping CTFd challenges')

    parser.add_argument(
        'url',
        help='Platform URL',
    )

    parser.add_argument(
        '-u', '--username',
        help='Platfrom username',
    )

    parser.add_argument(
        '-p', '--password',
        help='Platform password',
    )

    parser.add_argument(
        '--nonce-regex',
        help='Platform nonce regex',
    )

    parser.add_argument(
        '--auth-file',
        help='File containing username and password, seperated by newline',
    )

    parser.add_argument(
        '-n', '--no-login',
        help='Use this option if the platform does not require authentication',
        action='store_true',
    )

    parser.add_argument(
        '--no-file',
        help='Don\'t download files',
        action='store_true',
    )

    parser.add_argument(
        '--trust-all',
        help='Will make directory as the name of the challenge, the slashes(/) character will automatically be replaced with underscores(_)',
        action='store_true',
    )

    parser.add_argument(
        '-t', '--template',
        help='Custom template path',
    )

    parser.add_argument(
        '-v', '--verbose',
        help='Verbose',
        action='store_true',
    )

    args = parser.parse_args()

    CONFIG['base_url'] = args.url
    CONFIG['no_file'] = args.no_file
    CONFIG['no_login'] = args.no_login

    if not args.no_login:
        CONFIG['username'] = args.username
        CONFIG['password'] = args.password

    if args.nonce_regex:
        CONFIG['nonce_regex'] = args.nonce_regex

    if args.auth_file:
        with open(args.auth_file, 'r') as f:
            CONFIG['username'] = f.readline().strip()
            CONFIG['password'] = f.readline().strip()

    if args.trust_all:
        CONFIG['blacklist'] = '/'

    if args.verbose:
        CONFIG['verbose'] = logging.DEBUG

    if args.template:
        CONFIG['template'] = args.template

    logging.basicConfig(
        level=CONFIG['verbose'],
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logging.addLevelName(logging.ERROR, '[-]')
    logging.addLevelName(logging.INFO, '[+]')
    logging.addLevelName(logging.DEBUG, '[*]')

def get_nonce() -> str:
    res = session.get(urljoin(CONFIG['base_url'], '/login'))
    return re.search(CONFIG['nonce_regex'], res.text).group(1)

def login() -> None:
    nonce = get_nonce()
    logger.debug(f'Nonce: {nonce}')

    res = session.post(
        urljoin(CONFIG['base_url'], '/login'),
        data={
            'name': CONFIG['username'],
            'password': CONFIG['password'],
            'nonce': nonce,
        }
    )

    if 'incorrect' in res.text:
        logger.error('Login failed!')
        exit(1)

def logout() -> None:
    logger.info('Done! Logging you out!')
    session.get(urljoin(CONFIG['base_url'], '/logout'))

def fetch(url: str) -> Union[List[dict], dict]:
    logger.debug(f'Fetching {url}')
    res = session.get(url)

    if not res.ok or not res.json()['success']:
        logger.error('Failed fetching challenge!')
        exit(1)

    return res.json()['data']

def fetch_file(filepath: str, filename: str, clean_filename: str) -> None:
    logger.info(f'Downloading {clean_filename} into {filepath}')
    res = session.get(urljoin(CONFIG['base_url'], filename), stream=True)

    with open(os.path.join(filepath, clean_filename), 'wb') as f:
        f.write(res.content)

def get_challenges() -> Generator[dict, None, None]:
    logger.debug('Getting challenges')
    challenges = fetch(urljoin(CONFIG['base_url'], '/api/v1/challenges'))

    for challenge in challenges:
        yield fetch(urljoin(CONFIG['base_url'], f'/api/v1/challenges/{challenge["id"]}'))

def run() -> None:
    hostname = urlparse(CONFIG['base_url']).hostname
    template = Template(open(CONFIG['template']).read())

    for challenge in get_challenges():
        category = re.sub(CONFIG['blacklist'], '', challenge['category']).strip()
        name = re.sub(CONFIG['blacklist'], '', challenge['name']).strip()
        logger.info(f'[{category}] {name}')

        filepath = os.path.join(hostname, category, name)

        if not os.path.exists(filepath):
            logger.info(f'Creating directory {filepath}')
            os.makedirs(filepath)

        with open(os.path.join(filepath, 'README.md'), 'w+') as f:
            rendered = template.render(challenge=challenge)
            f.write(rendered)

        if CONFIG['no_file']:
            continue

        if 'files' in challenge:
            for filename in challenge['files']:
                clean_filename = os.path.basename(urlsplit(filename).path)
                fetch_file(filepath, filename, clean_filename)

def main() -> None:
    setup()
    welcome()

    if CONFIG['no_login']:
        run()
    else:
        login()
        run()
        logout()

if __name__ == '__main__':
    main()
