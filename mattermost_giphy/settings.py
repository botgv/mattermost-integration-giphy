# -*- coding: utf-8 -*-
import os

# username the bot posts as
USERNAME = os.environ.get('USERNAME', 'giphy')

# display picture the bot posts with
ICON_URL = os.environ.get('ICON_URL', 'https://avatars0.githubusercontent.com/u/3588525?v=3&s=200')

# the maximum parental rating of gifs posted
RATING = os.environ.get('RATING', 'pg-13')

# scheme to be used for the gif url return to mattermost
SCHEME = os.environ.get('SCHEME', 'https')

# the is a public beta key from giphy api
GIPHY_API_KEY = os.environ.get('GIPHY_API_KEY', 'dc6zaTOxFJmzC')

# the Mattermost token or tokens generated when you created your outgoing webhook
# multiple tokens needs to be separated by a colon
MATTERMOST_GIPHY_TOKEN = os.environ.get('MATTERMOST_GIPHY_TOKEN', '').split(':')

BLACK_LISTED_CHANNELS = ['ldev-git--infra','ldev','documentation-projets','red-is-dev-redmine']

RATING_PER_CHANNELS = {"me":"r","pose":"r","wtf":"r"}
