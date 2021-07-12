<img src="./resources/media/logo.png" width=512>

[![Version](https://img.shields.io/badge/latest%20version-0.8.16-blue.svg)](https://github.com/patrick-klein/repository.librarytools)
[![GitHub last commit](https://img.shields.io/github/last-commit/luizoti/script.library.integration.tool.svg)](https://github.com/luizoti/script.library.integration.tool/commits/Matrix)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/2e2794f8e9fc49108aaa541a03c37ec4)](https://www.codacy.com/gh/luizoti/script.library.integration.tool/dashboard?utm_source=github.com\&utm_medium=referral\&utm_content=luizoti/script.library.integration.tool\&utm_campaign=Badge_Grade)

[![](https://raw.githubusercontent.com/appcraftstudio/buymeacoffee/master/Images/snapshot-bmc-button.png)](https://www.buymeacoffee.com/luizoti)
[![](https://foswiki.org/pub/Community/DonationButton/donate-button.png)](https://www.paypal.com/donate?hosted_button_id=JM5MHUEW4W5AC)


</br>

Library Integration Tool is a Kodi addon that lets you integrate content from
any video plugin into your library. Provides tools for you to directly manage
their metadata, and automatically add/remove items based on their current
availability.

Forum Thread:
<https://forum.kodi.tv/showthread.php?tid=327514>

## Requirements

- **Kodi 19+**

## Tested with this streaming addons

- NETFLIX - *Works*
- AMAZON VOD - *Works*
- CRUNCHYROLL - *Works*
- DISNEY+ - *Works*

<!-- * ~~ABC Family - by t1m~~ - *Seems to be broken at the moment*
- Classic Cinema - by Jonathan Beluch (jbel)
- Cooking Channel - by t1m
- Comedy Central - by Lunatixz - _Great content and all videos have episode
  numbers_
- Crackle - by eracknaphobia
- DIY Network - by t1m
- Food Network - by t1m
- HGTV - by t1m
- Popcornflix - by t1m - _Lots of content, but most have low ratings_
- Travel Channel - by t1m
- TV Land - by Lunatixz - _Double check episode numbers before scraping_
- WABC Programs - by t1m - _Do not sync entire directory due to infinite load
  times for some items, but works well with individual TV shows_
- WNBC Programs - by t1m - _Huge amount of content, but slow to update_ -->

## Installation Matrix

1. Download this zip for the
   [Library Integration Tool](https://github.com/luizoti/script.library.integration.tool/archive/refs/heads/Matrix.zip)
2. In Kodi, go to Settings --> Add-ons --> Install from zip file --> then select
   the downloaded zip.
3. Run Library Integration Tool for the first time. You will get a message
   letting you know the managed folder was configured.

NOTE: The default paths for the library (managed dir) are:

- `special://userdata/addon_data/script.library.integration.tool/`
- `/home/username/.kodi/userdata/addon_data/script.library.integration.tool/`

The paths above point to the same place.

### The purpose of LIT

This addon can create and manage .strm files for any video from a plugin, which
Kodi will be able to add to the library and play. New videos that become
available in plugins can automatically be prepared for your library, and
unavailable items will automatically be removed.

The tool will also create a Metadata folder where you can put .nfo files and
artwork for your videos. Whenever you add a streamed video to your library, it
will automatically use your custom metadata.

### The base LIT workflow

LIT works with two base stages, 'staged' (database) and 'managed' (library).

When user add content from a streaming addon, this item is added to staged, 
when user add content to managed, the .strm and .nfo (metadata) will be created.

Current, LIT will create .strm and .nfo following this pattern:

`showtitle` - `spisodeid` - `episodename`.strm

`Invincible (2021) - S01E01 - JÁ ESTAVA NA HORA.strm`

The files will be created inside a folder with show title and season:

`/Invincible (2021)/Season 1/Invincible (2021) - S01E01 - JÁ ESTAVA NA HORA.strm`

The pattern above is based on the pattern used by kodi: https://kodi.wiki/view/Naming_video_files/TV_shows

You can use `tinyMediaManager` to rename files and any other operations, but for now LIT will no longer recognize items that have been renamed.

### Settings options

 - Options to change library path
 - Options to auto add itens to library
 - Options to disable .nfo creation
 - Dev options

<!--  -->

<!-- ### Tutorial - Updating Directories

Now that you've added this content from Crackle to your library, you can
continue to add movies and TV shows from all of your favorite plugins. Refer to
the list at the bottom of the README for several suggested addons that work well
with Library Integration Tool. However, after you've been using this add-on for
a while, the availability of streamed content may change.

To quickly update your directories, open "View Synced Directories" from the main
menu and choose "Update all" at the bottom of the list. This action will reload
all synced directories and automatically find old managed and staged items that
have become unavailable, and new items to stage. Depending on how many
directories need to be loaded, and which plugins you use, this may take a while.
Once the tool is done loading all the items, it will ask for your confirmation
before proceeding.

After the directories are updated, you can review and add your staged items. And
remember to clean and/or update your library! -->

### Tutorial - Blocking Items

After updating, you may notice that you already have a local copy of one of the
new staged movies. Rather than just removing it from staged movies, you should
consider blocking it. If you block an item, it will not be automatically
re-staged when updating directories again.

From "View Staged Movies", select the movie you already have. Choose the option
"Remove and block". You can block episodes and entire TV shows as well. Keep in
mind that any metadata files you've generated for items you block will be
deleted from the Metadata folder.


If you change your mind later, you can select any blocked item from the list and
choose "Remove".
<!-- 
### Other Addons

**Skin Helper Service Widgets BETA** by marcelveldt - *The latest versions
include a new recommendation system that dynamically shows you personalized
content on your homescreen. So if you decide to add every possible directory and
end up with 4000+ new items in your library, this addon will help ensure you
only see the most relevant titles*

**WatchedList** by schapplm - *Because you'll potentially remove and re-add
streamed content several times with Library Integration Tool, WatchedList makes
your watched status persistent by storing it in an independent database*
 -->
## Contributing

The most important way to contribute right now is to use the addon and post a
full debug log in the forums or on GitHub if there are any issues. I would also
appreciate general feedback on performance, user-friendliness, and any feature
requests.

This addon includes full localization support, so you are welcome to submit and
update translated string files.

For all known bugs and planned feature development, refer to inline TODO tags.
And thank you for considering improving this project! Full credit for your
contributions will be given in the release notes and here in the README.

### If you are a Streaming Addon developer:

LIT uses jsonrpc to collect the data that will be used to create the strms and 
nfos, jsonrpc returns a daaaa json, containing the keys below, some are 
mandatory as file and others are very important, such as type, showtitle, 
episode, season year , in fact, by and large they are all essential, so when 
creating the list of items fill in all of these items, by and large this will 
just be part of the process you are already doing, but for LIT to make it easier.


xbmcgui.ListItem: https://codedocs.xyz/AlwinEsch/kodi/group__python__xbmcgui__listitem.html#details

- art
- fanart
- duration
- season
- title
- file
- showtitle
- year
- episode


Thanks.
