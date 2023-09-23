from database.MySQL import MySQL
from pathlib import Path
from instaloader.exceptions import LoginRequiredException
import instaloader
import time
import json
import argparse
import configparser
import logging
import wget
import sys
import os


# Parse args
args_parser = argparse.ArgumentParser(description='Instagram parser')
args_parser.add_argument(
        '-l', '--login',
        type=str,
        dest='login',
        help='login',
        required=True
)
args_parser.add_argument(
        '-p', '--password',
        type=str,
        dest='password',
        help='password',
        required=True
)
args_parser.add_argument(
        '-c', '--count',
        type=int,
        default=12,
        dest='count',
        help='count of posts'
)
args_parser.add_argument(
        '-C', '--config',
        type=str,
        default='instagramarser.conf',
        dest='config',
        help='config file path'
)
args_parser.add_argument(
        '-L', '--log',
        type=str,
        default='instagramparser.log',
        dest='log',
        help='log file path'
)
args_parser.add_argument(
        '-S', '--session',
        type=str,
        default='default.session',
        dest='session',
        help='session file path'
)
args_parser.add_argument(
        '-P', '--proxy',
        type=str,
        default='',
        dest='proxy',
        help='proxy example: socks5://127.0.0.1:9050')
args = args_parser.parse_args()


# Reading config
config = configparser.ConfigParser()
config.read(args.config)


# Logging
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.INFO)
logFormatter = logging.Formatter(
    fmt='[%(asctime)s] [%(threadName)s] [%(levelname)s]  %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

fileHandler = logging.FileHandler(args.log)
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)


# Reading config
rootLogger.info('Reading config...')

USERAGENT = config['client']['USERAGENT']

HOST = config['database']['HOST']
USERNAME = config['database']['USERNAME']
PASSWORD = config['database']['PASSWORD']
DATABASE = config['database']['DATABASE']


# Connecting to database
rootLogger.info('Connecting to database...')

MyDB = MySQL(HOST, USERNAME, PASSWORD, DATABASE)

# Variables
NICK = MyDB.oldest_account()[0]
LOGIN = args.login
PASSWORD = args.password
DIR_NAME = '/var/www/averin.pro/data/www/averin.pro'
COUNT = args.count
SESSION = args.session

proxies = {
    'http': '{args.proxy}',
    'https': '{args.proxy}'
}

L = instaloader.Instaloader(
        quiet=True,
        compress_json=False,
        download_comments=False,
        download_geotags=False,
        filename_pattern='{filename}',
        user_agent=USERAGENT
)

L.context._session.proxies = proxies


# Login
rootLogger.info(f'Login as {LOGIN}')

try:
    L.load_session_from_file(LOGIN, SESSION)
except LoginRequiredException:
    L.login(LOGIN, PASSWORD)
    L.save_session_to_file(SESSION)


# Fetching data
rootLogger.info(f'Fetching data of {NICK}')

profile = instaloader.Profile.from_username(L.context, NICK)
posts = profile.get_posts()

post_count = posts.count
fullName = profile.full_name
followers_count = profile.followers
followees_count = profile.followees
avatar = profile.get_profile_pic_url()


# Dumping account info
rootLogger.info(f'Dumping account info of {NICK}')

account_info = {
    'Posts': post_count,
    'fullName': fullName,
    'Followers': followers_count,
    'Following': followees_count,
    'profilePicture': avatar,
    'medias': {}
}


# Downloading posts
rootLogger.info(f'Downloading posts of {NICK}')

for index, post in enumerate(posts):
    if index >= COUNT:
        break

    account_info['medias'].update({
        index: {
            'id': post.mediaid,
            'shortcode': post.shortcode,
            'typeName': post.typename,
            'link': post.url,
            'caption': post.caption,
            'comments': post.comments,
            'likes': post.likes,
            'video': post.is_video,
            'videoViewCount': post.video_view_count,
            'accessibilityCaption': post.accessibility_caption,
            'hashtags': post.caption_hashtags
        }
    })

    L.download_post(post, Path(f'{DIR_NAME}/widget_pic/{NICK}'))

    json_object = json.dumps(obj=account_info, indent=4)

    with open(f'{DIR_NAME}/widget_json/{NICK}.json', 'w') as outfile:
        outfile.write(json_object)

    os.system(f'rm -f {DIR_NAME}/widget_pic/{NICK}/*.txt')
    os.system(f'rm -f {DIR_NAME}/widget_pic/{NICK}/*.json')
    os.system(f'rm -f {DIR_NAME}/widget_pic/{NICK}/*.mp4')


# Download avatar
rootLogger.info('Downloading avatar')

wget.download(avatar, f'{DIR_NAME}/widget_pic/{NICK}/avatar.jpg', bar=None)


# Updating date of update
rootLogger.info('Updating date of update')

unixtime = int(time.time())

MyDB.update(NICK, unixtime)
