

import sys
import xbmc
import xbmcgui

import simplejson as json

from resources.lib.contentitem import MovieItem, EpisodeItem
from resources.lib.utils import log_msg, get_items, save_items

if __name__ == '__main__':
    #TODO: add recursive option
    #TODO: rick roll pirates

    # get content type
    container_type = xbmc.getInfoLabel('Container.Content')
    #if container_type=='tvshows':
    #    # if listitem is folder, it must be a tv show
    #    content_type = "tvshow"
    if container_type=='movies':
        # check if contents are movie
        content_type = "movie"
    else:
        # ask user otherwise
        is_show = xbmcgui.Dialog().yesno("Library Integration Tool",
            'Unable to determine content.  Choose content type:',
            yeslabel="TV Shows", nolabel="Movies")
        if is_show:
            content_type = 'tvshow'
        else:
            content_type = 'movie'

    # update synced file
    synced_dirs = get_items('synced.pkl')
    current_dir = {'dir':xbmc.getInfoLabel('Container.FolderPath'), 'mediatype':content_type}
    if current_dir in synced_dirs:
        xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"Current directory already synced.  Looking for new items...\")")
    else:
        synced_dirs.append(current_dir)
    save_items('synced.pkl', synced_dirs)
    log_msg('sync: %s' % current_dir, xbmc.LOGNOTICE)

    # query json-rpc to get files in directory
    # TODO: try xbmcvfs.listdir(path) instead
    results = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory":"%s"}, "id": 1}' % current_dir['dir'])
    dir_items = json.loads(results)["result"]["files"]
    log_msg('dir_items: %s' % dir_items, xbmc.LOGNOTICE)

    if content_type=='movie':

        # loop through all items and get titles and paths and stage them
        staged_items = get_items('staged.pkl')
        staged_paths = [x.get_path() for x in staged_items]
        managed_paths = [x.get_path() for x in get_items('managed.pkl')]
        blocked_items = get_items('blocked.pkl')
        blocked_movies = [x['label'] for x in blocked_items if x['type']=='movie']
        blocked_keywords = [x['label'].lower() for x in blocked_items if x['type']=='keyword']
        items_to_stage = []
        for i, ditem in enumerate(dir_items):
            # get label for item
            label = ditem['label']
            # get path for item
            path = ditem['file']
            # check for duplicate paths
            if (path in staged_paths) or (path in managed_paths):
                continue
            # check for blocked items
            if label in blocked_movies or any(x in label.lower() for x in blocked_keywords):
                continue
            # create ContentItem
            item = MovieItem(path, label, content_type)
            # add to staged
            items_to_stage.append(item)
        staged_items += items_to_stage
        save_items('staged.pkl', staged_items)
        xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"%s movies staged\")" % len(items_to_stage))


    elif content_type=='tvshow':
        #TODO: add fix for smithsonian, so you can add from episode directory

        staged_items = get_items('staged.pkl')
        staged_paths = [x.get_path() for x in staged_items]
        managed_paths = [x.get_path() for x in get_items('managed.pkl')]
        blocked_items = get_items('blocked.pkl')
        blocked_shows = [x['label'] for x in blocked_items if x['type']=='show']
        blocked_episodes = [x['label'] for x in blocked_items if x['type']=='episode']
        blocked_keywords = [x['label'].lower() for x in blocked_items if x['type']=='keyword']
        items_to_stage = []
        for ditem in dir_items:
            # get name of show and skip if blocked
            tvshow_label = ditem['label']
            if tvshow_label in blocked_shows or any(x in tvshow_label.lower() for x in blocked_keywords):
                continue
            # get everything inside tvshow path
            tvshow_path = ditem['file']
            results = json.loads(xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory":"%s"}, "id": 1}' % tvshow_path))
            if not results.has_key('result'):
                continue
            if not results["result"].has_key('files'):
                continue
            show_items = results["result"]["files"]
            # get all items to stage in show
            for shitem in show_items:
                label = shitem['label']
                path = shitem['file']
                if path in staged_paths:
                    continue
                elif path in managed_paths:
                    continue
                elif label in blocked_episodes or any(x in tvshow_label.lower() for x in blocked_keywords):
                    continue
                item = EpisodeItem(path, shitem['label'], content_type, tvshow_label)
                items_to_stage.append(item)
        # add all items from all shows to stage list
        staged_items += items_to_stage
        save_items('staged.pkl', staged_items)
        xbmc.executebuiltin("Notification(\"Library Integration Tool\", \"All TV shows staged. %s episodes added\")" % len(items_to_stage))
