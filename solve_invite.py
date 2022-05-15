# This script will brute force solve Discord server invites with partial missing characters.
# Additional configuration needed if the missing characters are not trailing.
#
# The way the files are saved is indeed a bit redundant on purpose.
#
# Happy solving.

import dotenv
import requests
import random
import logging
import pickle
from pathlib import Path  # We're just using this to be able to invoke touch on missing files for ease of use.
import time

CONFIG = dotenv.dotenv_values()

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')


def setup_logger(name, log_file, level=logging.INFO):
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


valid_invites_logger = setup_logger('valid_invites',
                                    './logs/valid_invites_logfile.log')
unknown_invites_logger = setup_logger('unknown_invites',
                                      './logs/unknown_invites_logfile.log')
rate_limited_logger = setup_logger('rate_limited',
                                   './logs/rate_limited_logfile.log')
error_logger = setup_logger('error', './logs/error_logfile.log')

urls_to_try = []
valid_invites = []
unknown_invites = []
error429 = []
proxylist = []


# Making assumption these files exist and are formatted properly.
# The files loaded from .env are the ones that are expected to be
# altered outside of the scope of this script.
def load_state():
    global urls_to_try, unknown_invites, valid_invites, error429

    try:
        with open(CONFIG['URLS_TO_TRY'], 'rb') as fp:
            try:
                urls_to_try = pickle.load(fp)
            except EOFError:
                urls_to_try = []
    except OSError as e:
        exit('Run the generate_permutations.py script first.')

    try:
        with open(CONFIG['PROXIES'], 'r') as fp:
            # Read these line by line so we can update the list with unserialized proxies for ease of use
            for line in fp:
                proxylist.append(line)
    except OSError as e:
        exit(
            'Set up the proxy file. Attempting without proxies is a waste of time.'
        )

    Path('./data/unknown_invites.txt').touch(exist_ok=True)
    with open('./data/unknown_invites.txt', 'rb') as fp:
        try:
            unknown_invites = pickle.load(fp)
        except EOFError:
            unknown_invites = []

    Path('./data/valid_invites.txt').touch(exist_ok=True)
    with open('./data/valid_invites.txt', 'rb') as fp:
        try:
            valid_invites = pickle.load(fp)
        except EOFError:
            valid_invites = []

    Path('./data/error429.txt').touch(exist_ok=True)
    with open('./data/error429.txt', 'rb') as fp:
        try:
            error429 = pickle.load(fp)
        except EOFError:
            error429 = []


def save_state(file, data):
    with open(file, 'wb+') as fp:
        pickle.dump(data, fp)


def get_invite_status(url, timeout):

    apiUrl = f'https://discord.com/api/{CONFIG["API_VERSION"]}/invites/{url}'

    inviteURL = f'https://discord.gg/{url}'

    attempts = 0
    while True:
        proxyused = random.choice(proxylist)
        proxydict = {
            "http": "http://" + proxyused,
            # "https": "https://" + proxyused
        }

        try:
            r = requests.get(apiUrl, proxies=proxydict, timeout=timeout)

            if r.status_code == 200:
                if "guild" in r.text:  # This key in the returned JSON indicates a valid server.
                    valid_invites_logger.info(
                        f"Found a good one: {inviteURL}. Proxy: {proxyused}")
                    print(f'Found a good one: {inviteURL}')
                    valid_invites.append(inviteURL)
                    save_state("./data/valid_invites.txt", valid_invites)
                    return r

            elif r.status_code == 429:
                rate_limited_logger.warning(
                    f"Rate limited on ({inviteURL}). Proxy: {proxyused}")

                attempts += 1
                if attempts > int(CONFIG['MAX_RETRIES']):
                    error429.append(inviteURL)
                    save_state("./data/error429.txt", error429)
                    rate_limited_logger.info(
                        f'Max retries for {inviteURL}. Logging and moving on.')
                    return False

            elif r.status_code == 404:
                unknown_invites_logger.info(
                    f"Invite code ({inviteURL}) doesn't exist. Proxy: {proxyused}"
                )
                unknown_invites.append(inviteURL)
                save_state("./data/unknown_invites.txt", unknown_invites)
                return r

            else:
                error_logger.info(
                    f"{r.status_code} status error. Proxy: {proxyused}")

        except requests.exceptions.RequestException as e:
            # Catch all errors regarding request, log them, and use
            # recursion to re-attempt the same invite code with a new request
            error_logger.error(
                f'Request exception while using proxy: {proxyused}')
            error_logger.error(e)


load_state()

# You can uncomment this line and add a known working invite to the top of the list
# if you want to verify that the proxies and code are working.
urls_to_try.insert(0, 'python')

for url in urls_to_try:
    if any(url in s for s in unknown_invites):
        # print(f"{url} known to be 404")
        continue
    else:
        get_invite_status(url, int(CONFIG['TIMEOUT']))

    time.sleep(float(CONFIG['DELAY']))
