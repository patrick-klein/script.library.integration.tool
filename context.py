

import sys
import os
import xbmc
import xbmcgui

import simplejson as json

from resources.lib.contentitem import MovieItem, EpisodeItem
from resources.lib.utils import log_msg, get_items, save_items

if __name__ == '__main__':
    #TODO: don't add items already in library
    #TODO: add "single movie" or "single tvshows" synced directory so they're correctly updated/pruned

    # Manual warning
    #proceed = xbmcgui.Dialog().yesno("Library Integration Tool",
    #    'Manually added items will not be automatically cleaned from library if they become unavailable. Proceed with action?')
    #if not proceed:
    #    sys.exit()

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
        is_show = xbmcgui.Dialog().yesno("Library Integration Tool",
            'Unable to determine content.  Choose content type:',
            yeslabel="TV Show", nolabel="Movie")
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
            xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"Item is already staged\")")
        elif path in managed_paths:
            xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"Item is already managed\")")
        else:
            # stage item
            item = MovieItem(path, label, content_type)
            staged_items.append(item)
            save_items('staged.pkl', staged_items)
            xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"Movie staged\")")

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
            xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"%s new episodes staged.  %s were already staged, and %s were already managed\")"
                % (len(items_to_stage), num_already_staged, num_already_managed) )
        else:
            xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"%s new episodes staged\")" % len(items_to_stage))
