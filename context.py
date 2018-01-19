

import sys
import os
import xbmc
import xbmcgui
import xbmcaddon

import simplejson as json

from resources.lib.contentitem import MovieItem, EpisodeItem
from resources.lib.utils import log_msg, get_items, save_items

if __name__ == '__main__':
    #TODO: don't add items already in library
    #TODO: add "single movie" or "single tvshows" synced directory so they're correctly updated/pruned

    addon = xbmcaddon.Addon()
    str_addon_name = addon.getAddonInfo('name')
    str_choose_content_type = addon.getLocalizedString(32100)
    str_tv_show = addon.getLocalizedString(32101)
    str_movie = addon.getLocalizedString(32102)
    str_item_is_already_staged = addon.getLocalizedString(32103)
    str_item_is_already_managed = addon.getLocalizedString(32104)
    str_movie_staged = addon.getLocalizedString(32105)
    str_i_new_episodes_i_already_staged_i_aleady_managed = addon.getLocalizedString(32106)
    str_i_new_episodes_staged = addon.getLocalizedString(32107)

    # get content type
    container_type = xbmc.getInfoLabel('Container.Content')
    if container_type=='tvshows':
        # if listitem is folder, it must be a tv show
        content_type = "tvshow"
    elif container_type=='movies':
        # check if contents are movie
        content_type = "movie"
    else:
        # ask user otherwise
        is_show = xbmcgui.Dialog().yesno(str_addon_name,
            str_choose_content_type,
            yeslabel=str_tv_show, nolabel=str_movie)
        if is_show:
            content_type = 'tvshow'
        else:
            content_type = 'movie'

    # stage single item for movie
    if content_type=='movie':

        # get content info
        label = sys.listitem.getLabel()
        path = sys.listitem.getPath()

        # prepare to stage
        staged_items = get_items('staged.pkl')
        staged_paths = [x.get_path() for x in staged_items]
        managed_paths = [x.get_path() for x in get_items('managed.pkl')]

        # check for duplicate
        if path in staged_paths:
            xbmc.executebuiltin('Notification("{0}", "{1}")'.format(str_addon_name, str_item_is_already_staged))
        elif path in managed_paths:
            xbmc.executebuiltin('Notification("{0}", "{1}")'.format(str_addon_name, str_item_is_already_managed))
        else:
            # stage item
            item = MovieItem(path, label, content_type)
            staged_items.append(item)
            save_items('staged.pkl', staged_items)
            xbmc.executebuiltin('Notification("{0}", "{1}")'.format(str_addon_name, str_movie_staged))

    # stage multiple episodes for tvshow
    elif content_type=='tvshow':
        #TODO: progress bar

        # get name and path of tvshow
        tvshow_label = sys.listitem.getLabel()
        tvshow_path = sys.listitem.getPath()

        # get everything inside tvshow path
        results = json.loads(xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory":"%s"}, "id": 1}' % tvshow_path))
        if results.has_key('result'):
            dir_items = results["result"]["files"]
        else:
            dir_items = []
        log_msg('show_items: %s' % dir_items, xbmc.LOGNOTICE)

        # get all items to stage
        staged_items = get_items('staged.pkl')
        staged_paths = [x.get_path() for x in staged_items]
        managed_paths = [x.get_path() for x in get_items('managed.pkl')]
        blocked_items = get_items('blocked.pkl')
        blocked_episodes = [x['label'] for x in blocked_items if x['type']=='episode']
        blocked_keywords = [x['label'].lower() for x in blocked_items if x['type']=='keyword']
        items_to_stage = []
        num_already_staged = 0
        num_already_managed = 0
        for ditem in dir_items:
            label = ditem['label']
            path = ditem['file']
            if path in staged_paths:
                num_already_staged += 1
                continue
            elif path in managed_paths:
                num_already_managed += 1
                continue
            elif label in blocked_episodes or any(x in label.lower() for x in blocked_keywords):
                continue
            #TODO: this is where i'd get episode id
            #   consider pulling airdate as well
            item = EpisodeItem(path, label, content_type, tvshow_label)
            items_to_stage.append(item)

        # add all items to stage list
        staged_items += items_to_stage
        save_items('staged.pkl', staged_items)

        if num_already_staged>0 or num_already_managed>0:
            xbmc.executebuiltin('Notification("{0}", "{1}}")'.format(str_addon_name,
                str_i_new_episodes_i_already_staged_i_aleady_managed % (len(items_to_stage), num_already_staged, num_already_managed) )
        else:
            xbmc.executebuiltin('Notification("{0}", "{1}")' % (str_addon_name, str_i_new_episodes_staged % len(items_to_stage)))
