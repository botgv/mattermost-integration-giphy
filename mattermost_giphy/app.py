# -*- coding: utf-8 -*-
import logging
import os
import sys
import json
from urlparse import urlsplit
from urlparse import urlunsplit
from urllib import quote_plus
from urllib import unquote_plus
import base64
'''from urllib import urlsplit
from urllib import urlunsplit'''

import requests
from flask import Flask
from flask import request
from flask import Response
from flask import send_file
from StringIO import StringIO

from mattermost_giphy.settings import *


logging.basicConfig(
    level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')
app = Flask(__name__)


@app.route('/')
def root():
    """
    Home handler
    """

    return "OK"

@app.route('/redirect/<image_url>')
def images_redirect(image_url):
	image_url = image_url[:-4]
	app.logger.info(image_url)
	#r = requests.get(base64.urlsafe_b64decode(image_url.encode("ascii")))
	r = requests.get(base64.urlsafe_b64decode("aHR0cHM6Ly9tZWRpYTMuZ2lwaHkuY29tL21lZGlhL0pES3hSTjBCdm1tMmMvZ2lwaHkuZ2lm"))
	buffer_image = StringIO(r.content)
	buffer_image.seek(0)
	return send_file(buffer_image, mimetype=r.headers['Content-Type'])

@app.route('/new_post', methods=['POST'])
def new_post():
    """
    Mattermost new post event handler
    """
    try:
        # NOTE: common stuff
        slash_command = False
        resp_data = {}
        resp_data['username'] = USERNAME
        resp_data['icon_url'] = ICON_URL

        data = request.form
        channel = data['channel_name']
        app.logger.info(channel)
        app.logger.info(BLACK_LISTED_CHANNELS)
        if channel in BLACK_LISTED_CHANNELS:
            raise Exception('Gif not allowed in channel `{}`'.format(channel))

        if not 'token' in data:
            raise Exception('Missing necessary token in the post data')

        if data['token'] not in MATTERMOST_GIPHY_TOKEN:
            raise Exception('Tokens did not match, it is possible that this request came from somewhere other than Mattermost')

        # NOTE: support the slash command
        if 'command' in data:
            slash_command = True
            resp_data['response_type'] = 'in_channel'

        translate_text = data['text']
        if not slash_command:
            translate_text = data['text'][len(data['trigger_word']):]

        if not translate_text:
            raise Exception("No translate text provided, not hitting Giphy")

        gif_url = giphy_translate(translate_text)
        if not gif_url:
            raise Exception('No gif url found for `{}`'.format(translate_text))

        resp_data['text'] = "`{}` searched for {}\r\n    {}redirect/{}.gif".format(data.get('user_name', 'unknown').title(), translate_text, request.host_url, base64.urlsafe_b64encode(gif_url))
        app.logger.info(resp_data['text'])
    except Exception as err:
        msg = err.message
        logging.error('unable to handle new post :: {}'.format(msg))
        resp_data['text'] = msg
    finally:
        resp = Response(content_type='application/json')
        resp.set_data(json.dumps(resp_data))
        app.logger.info(resp)
        return resp


def giphy_translate(text):
    """
    Giphy translate method, uses the Giphy API to find an appropriate gif url
    """
    try:
        params = {}
        params['s'] = text
        params['rating'] = RATING
        params['api_key'] = GIPHY_API_KEY

        resp = requests.get('{}://api.giphy.com/v1/gifs/translate'.format(SCHEME), params=params, verify=True)

        if resp.status_code is not requests.codes.ok:
            logging.error('Encountered error using Giphy API, text=%s, status=%d, response_body=%s' % (text, resp.status_code, resp.json()))
            return None

        resp_data = resp.json()

        url = list(urlsplit(resp_data['data']['images']['original']['url']))
        url[0] = SCHEME.lower()

        return urlunsplit(url)
    except Exception as err:
        logging.error('unable to translate giphy :: {}'.format(err))
        return None
