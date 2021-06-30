#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Module dedicate to manipulate title."""

import os

# TODO: Use combined list on all platforms. Would need to be combined with version check
# to re-add all managed items
MAPPED_STRINGS = [
    ('.', ''),
    (':', ''),
    ('/', ''),
    ('"', ''),
    ('$', ''),
    ('é', 'e'),
    (' [cc]', ''),
    ('Part 1', 'Part One'),
    ('Part 2', 'Part Two'),
    ('Part 3', 'Part Three'),
    ('Part 4', 'Part Four'),
    ('Part 5', 'Part Five'),
    ('Part 6', 'Part Six'),
]

if os.name == 'nt':
    MAPPED_STRINGS += [
        ('?', ''),
        ('<', ''),
        ('>', ''),
        ('\\', ''),
        ('*', ''),
        ('|', ''),
        #('+', ''),
        #(',', ''),
        #(';', ''),
        #('=', ''),
        #('[', ''),
        #(']', ''),
    ]

# TODO: NETFLIX find a way to deal with show with Part 1,
# Part 2 and etc, now, any part will be a season,
# maybe a api call with trakt or tvdb to get episode info is a way

# TODO: Giant animes like One Piece is devided in folders with 60 eps,
# and not splited by season, maybe all eps need to be in the Show dir
# directly and follow absolute order, to do this is necessary identify this cases.

# TODO: CHRUNCHROLL create a dialog to selec language or
# use system language to auto select:


def clean_name(title):
    """Remove/replace problematic characters/substrings for filenames."""
    # IDEA: Replace in title directly, not just filename

    # TODO: use this function to remove from Show/episode title on,
    # Show title
    # episode number
    # (Legendado)
    # (Leg)
    # (Dub PT)
    # (French Dub)
    # (German Dub)
    # (Portuguese Dub)
    # (English Dub)
    # (Spanish Dub)
    # TODO: Efficient algorithm that removes/replaces in a single
    for key, val in MAPPED_STRINGS:
        title = title.replace(key, val)
    return title
