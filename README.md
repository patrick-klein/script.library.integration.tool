<img src="./resources/logo.png" width=512>


[![Version](https://img.shields.io/badge/latest%20version-0.2.2-blue.svg)](https://github.com/patrick-klein/repository.librarytools)
[![GitHub last commit](https://img.shields.io/github/last-commit/patrick-klein/script.library.integration.tool.svg)](https://github.com/patrick-klein/script.library.integration.tool/commits/master)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/af5eed5b87df49b49eed908b3d808f7c)](https://www.codacy.com/app/klein.pat/Library-Integration-Tool-for-Kodi?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=patrick-klein/Library-Integration-Tool-for-Kodi&amp;utm_campaign=Badge_Grade)
[![Paypal Donate](https://img.shields.io/badge/paypal-donate-yellow.svg)](https://www.paypal.me/104084485)

</br>

Library Integration Tool is a Kodi addon that lets you integrate content from any video plugin into your library.  Provides tools for you to directly manage their metadata, and automatically add/remove items based on their current availability.

Forum Thread: [https://forum.kodi.tv/showthread.php?tid=327514](https://forum.kodi.tv/showthread.php?tid=327514)

## Requirements

* **Kodi 17+**

## Installation

1. Download this zip for the [LibraryTools repository](repository.librarytools/repository.librarytools/repository.librarytools-1.0.0.zip)

2. In Kodi, go to Settings --> Add-ons --> Install from zip file --> then select the downloaded zip.  After installing the repo, "Library Tools repository" will be available in Kodi.

4. While in Add-ons, go to Install from repository --> Library Tools repository --> Program add-ons --> Select Library Integration Tool

5. Open the settings for Library Integration Tool and choose a Managed Folder.  This is where the metadata and stream files will be stored.  I suggest you create a new folder near your existing media called "ManagedMedia", but any folder will work.

6. Run Library Integration Tool for the first time.  You will get a message letting you know the Managed Folder was configured.

7. From Kodi Settings, go to Media Settings --> Library --> Videos... --> and navigate to your Managed Folder.  Set content for ManagedMovies to Movies and check "Movies are in separate folders that match the movie title".  Set content for ManagedTV to TV shows.  Recommended to use "Local information only" if you want to use your own metadata.

DISCLAIMER:  You should NEVER edit the contents of ManagedMovies, ManagedTV, or the .pkl lists.  This will break your addon.  If you do break the addon, you can delete ManagedMovies, ManagedTV, and the .pkl lists, and Library Integration Tool will automatically generate new, blank ones the next time you run it.

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

From "View Staged Movies", select the movie you already have.  Choose the option "Remove and block".  That simple!  You can block episodes and entire TV shows as well.  Keep in mind that any metadata files you've generated for items you block will be deleted from the Metadata folder.

Sometimes when you sync a directory, items may show up that aren't actually videos.  For example, Popcornflix includes items called "<span style="color:red">Next Page</span>", which will also be added to staged movies.  You can block these like you would for normal content, or you can add a blocked keyword.  Any movie, episode, or TV show that contains a blocked keyword in the title won't be automatically staged.  You can add blocked keywords by going to "View Blocked Items" from the main menu, then choose "Add keyword" at the bottom.  A few common keywords you might want to add are "next page" and "coming soon".

And if you change your mind later, you can select any blocked item from the list and choose "Remove".

## Recommended Addons

### Video Plugins

* **ABC Family** by t1m
* **Classic Cinema** by Jonathan Beluch (jbel)
* **Cooking Channel** by t1m
* **Crackle** by eracknaphobia
* **DIY Network** by t1m
* **Food Network** by t1m
* **HGTV** by t1m
* **Popcornflix** by t1m - *Lots of content, but most have low ratings and the lists constantly change*
* **Top Documentary Films** by Damon Toumbourou - *Most items won't be automatically scraped*
* **Travel Channel** by t1m
* **TV Land** by Lunatixz - *Double check episode numbers before scraping*
* **WNBC Programs** by t1m - *Huge amount of content, but slow to update*

### Other Addons

**Skin Helper Service Widgets BETA** by marcelveldt - *The latest versions include a new recommendation system that dynamically shows you personalized content on your homescreen.  So if you decide to add every possible directory and end up with 4000+ new items in your library, this addon will help ensure you only see the most relevant titles*

**WatchedList** by schapplm - *Because you'll potentially remove and re-add streamed content several times with Library Integration Tool, WatchedList makes your watched status persistent by storing it in an independent database*

## Contributing

The most important way to contribute right now is to use the addon and post a full debug log if there are any issues.  This is an early release and still likely to undergo drastic changes as I receive feedback.

This addon also includes full localization support, so you are welcome to submit and update translated string files.

For all known bugs and planned feature development, refer to inline TODO tags.  And thank you for considering improving this project!  Full credit for your contributions will be given in the release notes and here in the README.

## Known Issues

* .strm files aren't automatically marked as watched by Kodi
* Manually added single movies aren't automatically removed if they become unavailable
* Kodi sorts episodes according to episode number in file name, not .nfo file.
