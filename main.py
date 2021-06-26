# Module: main
# Author: Roman V. M.
# Created on: 28.11.2014
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
"""
Copyright THE F:L:I:X:Y Authors
"""
import sys
from urllib.parse import urlencode, parse_qsl
import xbmcgui
import xbmcplugin
import six
import re
import requests
import time
import web_pdb
import socket
import threading
import os
from datetime import datetime
import uuid


# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])


CATEGORIES = [
    {"name": "Live TV Channels", "id": 1, "data": "https://flixyrepo.github.io/data/c.json",
        "thumb": "https://flixyrepo.github.io/img/c.png"},
    {"name": "Movies", "id": 2, "data": "https://flixyrepo.github.io/data/a.json",
        "thumb": "https://flixyrepo.github.io/img/m.png"},
    {"name": "Web Series", "id": 3, "data": "https://flixyrepo.github.io/data/b.json",
        "thumb": "https://flixyrepo.github.io/img/s.png"}
]



def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :return: plugin call URL
    :rtype: str
    """
    return '{0}?{1}'.format(_url, urlencode(kwargs))


def get_videos(category):
    """
    Get the list of videofiles/streams.

    Here you can insert some parsing code that retrieves
    the list of video streams in the given category from some site or API.

    .. note:: Consider using `generators functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.

    :param category: Category name
    :type category: str
    :return: the list of videos in the category
    :rtype: list
    """
    return requests.get(CATEGORIES[int(category)-1]["data"]).json()


def list_categories():
    """
    Create the list of video categories in the Kodi interface.
    """

    xbmcplugin.setPluginCategory(_handle, 'ALL')

    xbmcplugin.setContent(_handle, 'videos')

    categories = CATEGORIES
    for category in categories:
        list_item = xbmcgui.ListItem(label=category["name"])

        list_item.setArt({'thumb': category["thumb"],
                          'icon': category["thumb"],
                          'fanart': category["thumb"]})

        list_item.setInfo('video', {'title': category["name"],
                                    'genre': category["name"],
                                    'plot': category["name"],
                                    'mediatype': 'video'})

        url = get_url(action='listing', category=category["id"])

        is_folder = True

        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

    xbmcplugin.endOfDirectory(_handle)





def list_videos(category):
    """
    Create the list of playable videos in the Kodi interface.

    :param category: Category name
    :type category: str
    """

    xbmcplugin.setPluginCategory(_handle, CATEGORIES[int(category)-1]["name"])
    xbmcplugin.setContent(_handle, 'videos')
    videos = get_videos(category)

    # print(videos)
    if isinstance(videos, list):
        # Iterate through videos.
        for video in videos:
              list_item = xbmcgui.ListItem(label=video['name'])
       
              list_item.setInfo('video', {'title': video['name'],
                                        'genre': video['genre'],
                                        'plot': video['des'],
                                        'mediatype': 'video'})
     
              list_item.setArt(
                {'thumb': video['thumb'], 'icon': video['thumb'], 'fanart': video['cover']})

              list_item.setProperty('IsPlayable', 'true')

              url = get_url(action='play', video=video['video'])

              is_folder = False
              xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
        xbmcplugin.endOfDirectory(_handle)
    
    else:
    # Iterate through categories
      for category in videos:
         list_item = xbmcgui.ListItem(label=category)

         list_item.setArt({'thumb': videos[category][0]["thumb"],
                          'icon': videos[category][0]["thumb"],
                          'fanart': videos[category][0]["cover"]})
     
         list_item.setInfo('video', {'title': category,
                                    'genre': category,
                                    'mediatype': 'video'})
         url = get_url(action='serie', serie=category)
         is_folder = True
         xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
         # xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)

      xbmcplugin.endOfDirectory(_handle)       
        
         

def list_serie(serie):
    """
    Create the list of playable Series in the Kodi interface.

    :param category: Serie name
    :type category: str
    """

    xbmcplugin.setPluginCategory(_handle, serie)

    xbmcplugin.setContent(_handle, 'videos')
    videos = get_videos(3)
    videos = videos[serie];

        # Iterate through videos.
    for video in videos:
       list_item = xbmcgui.ListItem(label=video['name'])

       list_item.setInfo('video', {'title': video['name'],
                                        'genre': video['genre'],
                                        'mediatype': 'video'})

       list_item.setArt(
                {'thumb': video['thumb'], 'icon': video['thumb'], 'fanart': video['cover']})

       list_item.setProperty('IsPlayable', 'true')

       url = get_url(action='play', video=video['video'])

       is_folder = False
       xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    xbmcplugin.endOfDirectory(_handle)


def play_video(path):
    """
    Play a video by the provided path.

    :param path: Fully-qualified video URL
    :type path: str
    """
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=path)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'listing':
            # Display the list of videos in a provided category.
            list_videos(params['category'])

        elif params['action'] == 'play':
            # Play a video from a provided URL.
            play_video(params['video'])
        
        elif params['action'] == 'serie':
            # Play a video from a provided URL.
            list_serie(params['serie'])            
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_categories()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
