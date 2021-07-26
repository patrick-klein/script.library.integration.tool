<img src="./resources/media/logo.png" width=512>

[![Version](https://img.shields.io/badge/latest%20version-0.8.19-blue.svg)](https://github.com/luizoti/repository.melies)
[![GitHub last commit](https://img.shields.io/github/last-commit/luizoti/script.library.integration.tool.svg)](https://github.com/luizoti/script.library.integration.tool/commits/Matrix)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/2e2794f8e9fc49108aaa541a03c37ec4)](https://www.codacy.com/gh/luizoti/script.library.integration.tool/dashboard?utm_source=github.com\&utm_medium=referral\&utm_content=luizoti/script.library.integration.tool\&utm_campaign=Badge_Grade)

[![](https://i.ibb.co/4RL50J2/paypal.png)](https://www.buymeacoffee.com/luizoti)
[![](https://i.ibb.co/xLSPYB3/snapshot-bmc-button.png)](https://www.paypal.com/donate?hosted_button_id=JM5MHUEW4W5AC)


</br>

Library Integration Tool is a Kodi addon that lets you integrate content from
any video plugin into your library. Provides tools for you to directly manage
their metadata, and automatically add/remove items based on their current
availability.

Forum Thread:
<https://forum.kodi.tv/showthread.php?tid=327514>

## Requirements

- **Kodi 19+**

## Working addons:

- [x] Netflix
- [x] Amazon VOD
- [x] Crunchyroll
- [x] Disney+

## NOT working addons:

Pirate addons will not be supported, more information can be read here: [read](https://forum.kodi.tv/showthread.php?tid=327514&pid=3043067#pid3043067)

I only added support to paid addons that I have access to, the ones I don't have won't work, if you have a paid addon and want it to work with LIT, submit a PR adding support to it or wait until it's possible to include it, donations are fine too coming, subscriptions are not cheap.

In many cases it is possible to add movies from addons without support, TV series are the biggest problem, so be free to try.

Music addons may be added in the future, the LIT structure itself supports it, but so far there is no real written code to deal with music.

- [ ] Sansung TV Plus
- [ ] Pluto TV
- [ ] HBO Max
- [ ] ABC Family
- [ ] Classic Cinema
- [ ] Cooking Channel
- [ ] Comedy Central
- [ ] Crackle
- [ ] DIY Network
- [ ] Food Network
- [ ] HGTV
- [ ] Popcornflix
- [ ] Travel Channel
- [ ] TV Land
- [ ] WABC Programs
- [ ] WNBC Programs
- [ ] BBC iPlayer


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
