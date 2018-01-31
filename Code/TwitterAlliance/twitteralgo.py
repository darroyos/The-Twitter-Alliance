# -*- coding: utf-8 -*-
import sys
import os
import getopt
import logging
import requests
import json
import tweepy

from enum import Enum

logo = '''
*********************************************************************
*    ______       _ __  __          ___   _____                     *
*   /_  __/    __(_) /_/ /____ ____/ _ | / / (_)__ ____  _______    *
*    / / | |/|/ / / __/ __/ -_) __/ __ |/ / / / _ `/ _ \/ __/ -_)   *
*   /_/  |__,__/_/\__/\__/\__/_/ /_/ |_/_/_/_/\_,_/_//_/\__/\__/    *
*                                                                   *
*                               MADE IN                             *
*                                   Facultad de Informática UCM     *
*********************************************************************
*      Map the relationships between the most followed accounts     *
*********************************************************************
'''
'''
DESCRIPTION:
    Exports to a file the relationships between a list of twitter accounts.

AUTHORS:
    David Arroyo
    Adrián Camacho
    Paula Muñoz
    Carla Paola Peñarrieta

    Facultad de Informática - Universidad Complutense de Madrid

WHAT IT DOES:
    It checks the relationships between a list of twitter accounts.
    The desired set of Twitter accounts are given throught a text file
    that could be generated with the TwitterCounter.com scrapy spider or
    could be a manually generated one.

TODO:
    - More algorithms: only fetch mutual follows, fetch every single follow
                       between the given text file with Twitter accounts, etc.

    - Store more user info like number of followers, followings, location, etc.
'''

#################################################
# Custom defined types
#################################################


class AlgoMode(Enum):
    MUTUAL_FOLLOWS = 1
    ALL_FOLLOWS = 2
    USER_INFO = 3


#################################################
# Global Configuration
#################################################
CONSUMER_TOKEN = ''
CONSUMER_SECRET = ''
GOOGLE_API_KEY = ''

INPUT_FOLER = 'top_users'
EXPORT_FOLER = 'results'
ACCESS_TOKEN_FILE = 'access_token.txt'
FRIENDSHIP_FILE = 'friendships.txt'  # default filename

logging.basicConfig(
    filename="twalgo.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s")
#################################################


def main(argv):
    filename = None
    mode = AlgoMode.MUTUAL_FOLLOWS  # default algorithm mode
    global FRIENDSHIP_FILE  # global keyword needed for changing its value

    try:
        opts, args = getopt.getopt(argv, "hi:", ["help", "input=", "all", "userinfo", ])
    except getopt.GetoptError:
        print(logo)
        sys.exit(1)
    for opt, arg in opts:
        if opt in ("-i", "--input"):
            filename = arg
            FRIENDSHIP_FILE = filename[:-4] + '_friendships.txt'
        elif opt in ("--all"):
            mode = AlgoMode.ALL_FOLLOWS
        elif opt in ("--userinfo"):
            mode = AlgoMode.USER_INFO
        elif opt in ("-h", "--help"):
            print_help()

    if filename:
        print(logo)
        print('Fetching relationships!...')
        run(filename, mode)


def print_help():
    str_help = '''
TWITTERALLIANCE SYNTAX
twitteralgo.py [options]

OPTIONS

* -h, --help: print this help.
* -i, --input: specify the input file with the Twitter accounts to be analyzed.
* --all: change the default algorithm. This mode will extract every follow of
         each user that it's inside the given accounts set. The default mode
         just fetch mutual follows (friendships) between the users.
    '''

    print(logo)
    print(str_help)


def run(filename, mode):
    logging.info("TwitterAlliance has started!")
    auth = authentication()

    api = tweepy.API(auth_handler=auth,
                     retry_count=3,
                     retry_delay=5,
                     wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True)

    top100 = read_accounts_file(filename, api)

    if mode == mode.MUTUAL_FOLLOWS:
        logging.info("Fetching relationships using the mutual follows algorithm")
        fetch_relationships(top100, api)
        save_to_file(top100)
    elif mode == mode.ALL_FOLLOWS:
        logging.info("Fetching relationships using the all follows algorithm")
        fetch_all_relationships(top100, api)
        save_to_file(top100)
    elif mode == mode.USER_INFO:
        save_user_info(top100)


def read_accounts_file(filename, api):
    """
    Fetchs all the accounts to be analyzed from a file.

    Returns: the auxiliary dictionary structure with the keys initialized
             which will store the relationships.
    """

    top100 = {}

    script_dir = os.path.dirname(__file__)  # absolute dir the script is in
    INPUT_FILE = INPUT_FOLER + '/' + filename

    with open(os.path.join(script_dir, INPUT_FILE), 'r') as file:
        for user in file:
            user = user.strip()
            user = user.split()

            username = user[0]
            country = user[1]

            top100[username] = {'country': country}
            fetch_user_info(username, top100, api)

    logging.info("Twitter accounts file '%s' readed. Number of accounts: %i" % (INPUT_FILE, len(top100)))

    return top100


def fetch_user_info(user, top100, api):
    """
    Extract the user's profile info and appends it to the dictionary.
    """
    user_item = api.get_user(screen_name=user)

    dict_user = top100.get(user)

    """
    Dictionary keys
    ----------------------------------
    dict_user['followings']
    dict_user['followers']
    dict_user['tweets']
    dict_user['location']
    dict_user['latitude']
    dict_user['longitude']
    dict_user['favourites']
    dict_user['follows_list'] = []
    """

    logging.info('Country ' + user + ': ' + dict_user['country'])
    dict_user['followings'] = str(user_item.friends_count)
    logging.info('Followings ' + user + ': ' + dict_user['followings'])
    dict_user['followers'] = str(user_item.followers_count)
    logging.info('Followers ' + user + ': ' + dict_user['followers'])
    dict_user['tweets'] = str(user_item.statuses_count)
    logging.info('Tweets ' + user + ': ' + dict_user['tweets'])

    # LOCATION COORDINATES (Google Maps Geolocation API)
    # ------------------------------------------------------------

    dict_user['location'] = user_item.location
    logging.info('Location ' + user + ': ' + dict_user['location'])

    google_maps_url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + dict_user['location'] + '&key=' + GOOGLE_API_KEY
    r = requests.get(google_maps_url)

    jsonresponse = r.json()

    if jsonresponse['results']:
        dict_user['latitude'] = str(jsonresponse['results'][0]['geometry']['location']['lat'])
        logging.info('Latituted ' + user + ': ' + dict_user['latitude'])
        dict_user['longitude'] = str(jsonresponse['results'][0]['geometry']['location']['lng'])
        logging.info('Longitude ' + user + ': ' + dict_user['longitude'])

    # ------------------------------------------------------------

    dict_user['favourites'] = str(user_item.favourites_count)
    logging.info('Favourites ' + user + ': ' + dict_user['favourites'])
    dict_user['follows_list'] = []


def fetch_relationships(top100, api):
    """
    Makes the required API calls to determine the relationships between all the
    given Twitter accounts. Two users are relationated if they are following
    each other.

    The top100 parameter is an input and output parameter. It returns the
    updated dictionary.
    """

    user_accounts = list(top100)
    curr_user_index = 0
    next_user_index = 0
    limit = len(user_accounts)

    while (curr_user_index < limit):
        source_user = user_accounts[curr_user_index]
        logging.info("CURRENT SOURCE USER: %s" % source_user)
        # fetch_user_info(source_user, top100, api)
        while (next_user_index < limit):
            if (curr_user_index != next_user_index):
                target_user = user_accounts[next_user_index]

                target_friends = top100.get(target_user).get('follows_list')
                if target_friends and source_user in target_friends:
                    """
                    Check in the dictionary wether the target user has the
                    source user inside its friendship list. Our goal is to make
                    the least number of API request (rate limit...)
                    """
                    top100.get(source_user).get('follows_list').append(target_user)

                    logging.info("Friendship %s - %s detected!" % (source_user, target_user))
                else:
                    friends = api.show_friendship(source_screen_name=source_user,
                                                  target_screen_name=target_user)

                    # friends[0] => source_user | friends[1] => target_user
                    if friends[0].following and friends[1].following:
                        # they're folling each other
                        top100.get(source_user).get('follows_list').append(target_user)
                        logging.info("Friendship %s - %s detected!" % (source_user, target_user))

            total_completed = ((curr_user_index * limit +
                               next_user_index) / (limit *
                               limit) * 100)

            logging.info('TOTAL COMPLETED: %d%% ' % total_completed)

            next_user_index += 1

        next_user_index = 0
        curr_user_index += 1

    logging.info('TOTAL COMPLETED: 100%')


def fetch_all_relationships(top100, api):
    user_accounts = list(top100)
    curr_user_index = 0
    next_user_index = 0
    limit = len(user_accounts)

    while (curr_user_index < limit):
        source_user = user_accounts[curr_user_index]
        logging.info("CURRENT SOURCE USER: %s" % source_user)
        # fetch_user_info(source_user, top100, api)
        while (next_user_index < limit):
            if (curr_user_index != next_user_index):
                target_user = user_accounts[next_user_index]

                target_friends = top100.get(target_user).get('follows_list')

                if target_friends and source_user not in target_friends:
                    friends = api.show_friendship(source_screen_name=source_user,
                                                  target_screen_name=target_user)

                    if friends[0].following:
                        top100.get(source_user).get('follows_list').append(target_user)
                        logging.info('Source account: %s follows %s' % (source_user, target_user))
                    if friends[1].following:
                        top100.get(target_user).get('follows_list').append(source_user)
                        logging.info('Target account: %s follows %s' % (target_user, source_user))

            total_completed = ((curr_user_index * limit +
                               next_user_index) / (limit *
                               limit) * 100)

            logging.info('TOTAL COMPLETED: %d%% ' % total_completed)

            next_user_index += 1

        next_user_index = 0
        curr_user_index += 1

    logging.info('TOTAL COMPLETED: 100%')


def save_user_info(top100):

    user_accounts = list(top100)

    script_dir = os.path.dirname(__file__)  # absolute dir the script is in

    USERS_FILE = FRIENDSHIP_FILE[:-4] + '_users.txt'
    EXPORT_FILE = EXPORT_FOLER + '/' + USERS_FILE

    with open(os.path.join(script_dir, EXPORT_FILE), 'w+') as file:
        for user in user_accounts:
            user_data = top100.get(user)

            country = user_data.get('country', '0')
            followings = user_data.get('followings', '0')
            followers = user_data.get('followers', '0')
            tweets = user_data.get('tweets', '0')
            location = user_data.get('location', '0')
            latitude = user_data.get('latitude', '0')
            longitude = user_data.get('longitude', '0')
            favourites = user_data.get('favourites', '0')

            file.write(user + ': ')
            file.write(country)
            file.write(' ')
            file.write(followings)
            file.write(' ')
            file.write(followers)
            file.write(' ')
            file.write(tweets)
            file.write(' ')
            # file.write(location)
            # file.write(' ')
            file.write(latitude)
            file.write(' ')
            file.write(longitude)
            file.write(' ')
            file.write(favourites)
            file.write('\n')

        logging.info("Process completed. Exported results: %s" % USERS_FILE)


def save_to_file(top100):
    """
    Exports the top100 dictionary to a file.
    """

    user_accounts = list(top100)

    script_dir = os.path.dirname(__file__)  # absolute dir the script is in
    EXPORT_FILE = EXPORT_FOLER + '/' + FRIENDSHIP_FILE

    with open(os.path.join(script_dir, EXPORT_FILE), 'w+') as file:
        for user in user_accounts:
            friends = top100.get(user).get('follows_list')
            file.write(user + ': ')

            if friends:
                for friend in friends:
                    file.write(friend + ' ')

            file.write('\n')

    logging.info("Process completed. Exported results: %s" % FRIENDSHIP_FILE)

    save_user_info(top100)


def authentication():
    """
    Creates an OAuthHandler instance, we pass our consumer token and secret
    which was given to us and gets token from Twitter.

    Returns: the OAuthHandler instance.
    """

    auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
    auth.secure = True

    ACCESS_TOKEN, ACCESS_TOKEN_SECRET = get_access_tokens(auth)

    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    return auth


def get_access_tokens(auth):
    """
    Checks if we already have the access token from Twitter cached in a file.
    If the token is not cached:
        1. Get a request token from twitter
        2. Query the user for the “verifier code” that twitter will supply them
           after they authorize us.
        3. Exchange the authorized request token for an access token.
        4. Catch the new access token.
    """

    script_dir = os.path.dirname(__file__)  # absolute dir the script is in

    with open(os.path.join(script_dir, ACCESS_TOKEN_FILE), 'r+') as file:
        content = file.readline()

        # if the file has been written before
        if content:
            access_token = content.strip()
            # read a new line
            content = file.readline()
            if content:
                access_token_secret = content.strip()
                token = access_token, access_token_secret
                logging.info('The access token were taken from the cache')
            else:
                logging.critical("No access token secret found!")
        else:  # request a new access token
            try:
                redirect_url = auth.get_authorization_url()

                # Example w/o callback (desktop)
                print("Get your PIN: %s" % redirect_url)
                verifier = input('Verifier:')

                token = auth.get_access_token(verifier)
                logging.info('New access token were requested to Twitter')

                file.write(token[0])
                file.write('\n')
                file.write(token[1])
                logging.info('Caching to a file the requested access token')
            except tweepy.TweepError:
                logging.critical('Error! Failed to get access token.')
                sys.exit(1)

    return token


if __name__ == '__main__':
    main(sys.argv[1:])
