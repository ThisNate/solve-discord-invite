# Use this file to create a list of invite codes to attempt.
# Only needs to be ran once tbh
# This code will not generate the duplicate letters/digits  & casing (i.e. aa, bb, AA, BB, 00)
# We can manually try these if this script doesn't detect it.

import dotenv
# port os  #provides ways to access the Operating System and allows us to read the environment variables
import itertools
import string
import pickle  # For serializing/deserializing our lists to a file.

# load_dotenv()  # take environment variables from .env.
CONFIG = dotenv.dotenv_values()


def generate_permutations(file, base_string, num_chars_to_guess):
    permutations = []

    data = string.ascii_letters + string.digits  # All 62 of the possible characters
    for i in itertools.permutations(data, num_chars_to_guess):
        new_base = base_string + ''.join(i)
        permutations.append(new_base)

    with open(file, 'wb') as fp:
        pickle.dump(permutations, fp)


generate_permutations(CONFIG['URLS_TO_TRY'], CONFIG['BASE_STRING'],
                      int(CONFIG['NUM_CHARS_TO_GUESS']))
