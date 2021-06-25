<img src="./resources/media/logo.png" width=512>


[![Version](https://img.shields.io/badge/latest%20version-0.4.1-blue.svg)](https://github.com/patrick-klein/repository.librarytools)
[![GitHub last commit](https://img.shields.io/github/last-commit/luizoti/script.library.integration.tool.svg)](https://github.com/luizoti/script.library.integration.tool/commits/Matrix)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/2e2794f8e9fc49108aaa541a03c37ec4)](https://www.codacy.com/gh/luizoti/script.library.integration.tool/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=luizoti/script.library.integration.tool&amp;utm_campaign=Badge_Grade)
[![Paypal Donate](https://img.shields.io/badge/paypal-donate-yellow.svg)](https://www.paypal.com/donate?hosted_button_id=JM5MHUEW4W5AC)

</br>

Library Integration Tool is a Kodi addon that lets you integrate content from any video plugin into your library.  Provides tools for you to directly manage their metadata, and automatically add/remove items based on their current availability.

Forum Thread: [https://forum.kodi.tv/showthread.php?tid=327514](https://forum.kodi.tv/showthread.php?tid=327514)

## Requirements

* **Kodi 19+**

## Installation Matrix.

1. Download this zip for the [Library Integration Tool](https://github.com/luizoti/script.library.integration.tool/archive/refs/heads/Matrix.zip)

2. In Kodi, go to Settings --> Add-ons --> Install from zip file --> then select the downloaded zip.

3. Run Library Integration Tool for the first time.  You will get a message letting you know the managed folder was configured.

4. From Kodi Settings, go to Media Settings --> Library --> Videos....  If you are using a custom managed folder, add it as a source here, otherwise add `special://userdata/addon_data/script.library.integration.tool/`.  Set content for ManagedMovies to Movies and check "Movies are in separate folders that match the movie title".  Set content for ManagedTV to TV shows.  If you plan on using your own metadata, you may want to select "Local information only".

NOTE: By default, the managed folder is in the addon userdata folder.  You may open the settings for Library Integration Tool if you want to choose a custom managed folder instead.

DISCLAIMER:  Do not directly edit the contents of ManagedMovies, ManagedTV, or managed.db; you need to use the Library Integration Tool menu to edit these items.

## User Guide

### What does Library Integration Tool do?

This addon can create and manage .strm files for any video from a plugin, which Kodi will be able to add to the library and play.  New videos that become available in plugins can automatically be prepared for your library, and unavailable items will automatically be removed.

The tool will also create a Metadata folder where you can put .nfo files and artwork for your videos.  Whenever you add a streamed video to your library, it will automatically use your custom metadata.

### Tutorial - Staging Items

To start using this add-on, you need to begin adding content from a video plugin.  Crackle (in the Kodi Add-on repository) provides a ton of free content, so let's start there.  Open Crackle, then select and click Movies.  From the context menu, you can select "Add selected item to library" or "Sync directory to library".  If you choose to sync the directory, new movies that are added to Crackle will automatically become available to your library, and unavailable movies will be removed.  Select this option, and it will "stage" all the movies in this list.

Return to the top level of Crackle, and select TV.  Scroll down to "Seinfeld" and choose "Add selected item to library".  It may ask you to choose the content type, which should be "TV Show".  Library Integration Tool will load all of the episodes and add them to staging.  Now that we have selected movies and TV shows to add to the library, return to Program Add-ons and run Library Integration Tool.

### Tutorial - Adding Items to the Library

Running Library Integration Tool will open the main menu where you can view all of your staged and managed media, as well as synced directories and blocked items.  Select "View Staged Movies" to see all of the movies in the directory you just synced from Crackle.  You can select any item in the list to see available actions, or you can scroll to the bottom of the list to perform an action on all items.

If you have your ManagedMovies folder set to use an online scraper, you may want to go to the bottom of the list and choose "Add all movies".  This action will move all of the movies from "Staged" to "Managed" and create the appropriate folders and .strm files necessary for Kodi to recognize them.  After adding any staged media to managed, don't forget to "Update Library" from the main menu (or from Kodi settings).


### Tutorial - Using Metadata

You may be tempted to immediately add all the Seinfeld episodes like you did for the movies, however there is an issue with the episodes we got from Crackle: none of them have episode numbers!  Because Kodi and scrapers can't recognize episodes that don't have an episode number in the file name, the tool won't move any of these episodes to managed.  To fix this issue, we have two options...

#### 1) Renaming episodes within Library Integration Tool

The first option is to select each episode, click "Rename", and include the correct episode id at the beginning of the file.  For example, if "The Busboy" is in your list, you can rename it to "02x12 - The Busboy" or "S02E12 - The Busboy".  Now you will be able to add the item to your library.

#### 2) Using an external media manager

The second option is to use a media manager to generate .nfo files for each of the episodes.  In order to make the staged items visible to media managers, click on "Generate all metadata items" while viewing the Seinfeld episodes.  This will generate a folder for Seinfeld in Metadata/TV/ and populate it with empty files, and the titles will be appended by '-0x0'.  This tag is so the media manager will recognize the file as an episode.

Have your favorite media manager (MediaElch works great) scan the Metadata/TV/ directory.  It will find all the items that have generated metadata items.  Now, you can create .nfo files and download artwork automatically for every episode and tvshow.  Once you've gotten .nfo files saved with the correct episode numbers, you are ready to add the episodes.

In Library Integration Tool, you can select "Add all episodes" or "Add all episodes with metadata".  Both options will automatically rename the episodes using the episode number in their .nfo files, but you can also select "Automatically rename using metadata" on an episode to test it first.  Now, all of your Seinfeld episodes from Crackle (with their metadata) are in the library. Don't forget to update!

Note: Do NOT rename files directly in the Metadata folder; you must use the built-in rename tool or .nfo files.

### Tutorial - Updating Directories

Now that you've added this content from Crackle to your library, you can continue to add movies and TV shows from all of your favorite plugins.  Refer to the list at the bottom of the README for several suggested addons that work well with Library Integration Tool.  However, after you've been using this add-on for a while, the availability of streamed content may change.

To quickly update your directories, open "View Synced Directories" from the main menu and choose "Update all" at the bottom of the list.  This action will reload all synced directories and automatically find old managed and staged items that have become unavailable, and new items to stage.  Depending on how many directories need to be loaded, and which plugins you use, this may take a while.  Once the tool is done loading all the items, it will ask for your confirmation before proceeding.

After the directories are updated, you can review and add your staged items.  And remember to clean and/or update your library!


### Tutorial - Blocking Items

After updating, you may notice that you already have a local copy of one of the new staged movies.  Rather than just removing it from staged movies, you should consider blocking it.  If you block an item, it will not be automatically re-staged when updating directories again.

From "View Staged Movies", select the movie you already have.  Choose the option "Remove and block". You can block episodes and entire TV shows as well.  Keep in mind that any metadata files you've generated for items you block will be deleted from the Metadata folder.

If you change your mind later, you can select any blocked item from the list and choose "Remove".


## Settings

You can customize the behavior of this addon from the settings.  The following options can be changed:

### General
**Use custom managed folder** - Lets you select a custom managed folder instead of the default addon userdata folder.  This folder may be used by multiple Kodi instances. Sharing a managed folder between Windows and non-Windows computers is not recommended.

**Use custom metadata folder** - Lets you select a custom metadata folder, instead of creating a Metadata subfolder in the managed folder.  This folder may be used by multiple Kodi instances. Sharing a metadata folder between Windows and non-Windows computers is not recommended.

**Max recursion when finding videos** - Some plugins have content spread across multiple pages.  This setting specifies how many pages should be loaded before stopping.  Use a value of 0 to load all pages.

### Movies
**Add movies without staging** - By default, all new synced movies will be moved to staging.  This option allows you to automatically add movies directly to the library.  There is also an option to only automatically add movies that already have metadata.

### TV Shows
**Add TV show items without staging** - By default, all new synced TV show items will be moved to staging.  This option allows TV show items with properly formatted episode IDs to be automatically added to the library.  There is also an option to only add automatically TV show items that already have metadata.

**Use TV show artwork if episode thumb is unavailable** - Kodi can't create thumbnails from stream files, so this option will allow the addon to attempt copying the TV show thumb/fanart instead if an episode thumb isn't available.

### Development
**Enable development options** - Keep this option disabled, as it may slow down the addon.

## Tested with this streaming addons:

* NETFLIX - *Works*
* AMAZON VOD - *Works*
* CRUNCHYROLL - *Works*
* DISNEY+ - *Works*
* SEREN - *Works*
<!-- * ~~**ABC Family** by t1m~~ - *Seems to be broken at the moment*
* **Classic Cinema** by Jonathan Beluch (jbel)
* **Cooking Channel** by t1m
* **Comedy Central** by Lunatixz - *Great content and all videos have episode numbers*
* **Crackle** by eracknaphobia
* **DIY Network** by t1m
* **Food Network** by t1m
* **HGTV** by t1m
* **Popcornflix** by t1m - *Lots of content, but most have low ratings*
* **Travel Channel** by t1m
* **TV Land** by Lunatixz - *Double check episode numbers before scraping*
* **WABC Programs** by t1m - *Do not sync entire directory due to infinite load times for some items, but works well with individual TV shows*
* **WNBC Programs** by t1m - *Huge amount of content, but slow to update*
 -->
### Other Addons

**Skin Helper Service Widgets BETA** by marcelveldt - *The latest versions include a new recommendation system that dynamically shows you personalized content on your homescreen.  So if you decide to add every possible directory and end up with 4000+ new items in your library, this addon will help ensure you only see the most relevant titles*

**WatchedList** by schapplm - *Because you'll potentially remove and re-add streamed content several times with Library Integration Tool, WatchedList makes your watched status persistent by storing it in an independent database*

## Contributing

The most important way to contribute right now is to use the addon and post a full debug log in the forums or on GitHub if there are any issues.  I would also appreciate general feedback on performance, user-friendliness, and any feature requests.

This addon includes full localization support, so you are welcome to submit and update translated string files.

For all known bugs and planned feature development, refer to inline TODO tags.  And thank you for considering improving this project!  Full credit for your contributions will be given in the release notes and here in the README.

## Known Issues

* .strm files aren't automatically marked as watched by Kodi when played
* Manually added single movies aren't removed when updating synced directories if they become unavailable
* Kodi sorts episodes according to episode number in file name, not .nfo file
* Items with episode numbers that include spaces (i.e. S1 E1) may be added to the library, but are not recognized when generating metadata items (this is intentional to match MediaElch's behavior)
