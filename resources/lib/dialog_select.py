#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Custon xbmcgui.Dialog.select."""

import xbmcgui  # pylint: disable=import-error

from resources import ADDON_NAME

from resources.lib.utils import bold
from resources.lib.utils import getstring


class Select(xbmcgui.Dialog):
    def __init__(self, heading=ADDON_NAME, turnbold=False):
        """CustonDialog __init__."""
        super(Select, self).__init__()
        if turnbold:
            self.heading = bold(heading)
        else:
            self.heading = heading
        self.listofitems = None
        self.listofopts = None
        self.extra = None

    def items(self, listofitems, turnbold=True):
        """Add item lines to dialog select."""
        self.listofitems = [
            bold(bstr) for bstr in listofitems
        ] if turnbold else listofitems
        self._list = listofitems

    def extraopts(self, listofopts):
        """Add option lines to dialog select."""
        self.listofopts = listofopts
        self.extra = True

    def show(self, autoclose=False, useDetails=False, preselect=False, back=False, back_value=getstring(32011)):
        """Open dialog select with all params."""
        _type = None
        selection1 = None
        if self.extra:
            self.listofitems += self.listofopts
        if back:
            self.listofitems += [back_value]
        selection = self.select(
            heading=self.heading,
            list=self.listofitems,
            autoclose=autoclose,
            preselect=preselect,
            useDetails=useDetails
        )
        try:
            str_opt = self._list[selection]
        except IndexError:
            str_opt = self.listofitems[selection]
        if selection == -1:
            return None
        elif str_opt == back_value:
            return
        if str_opt in self.listofopts:
            _type = 'opt'
            for i, _str in enumerate(self.listofopts):
                if _str in str_opt:
                    selection1 = i
        elif str_opt in self._list or '[B]' in str_opt:
            _type = 'item'
            for i, _str in enumerate(self._list):
                if _str == str_opt:
                    selection1 = i
        return {'index': selection, 'index1': selection1, 'str': str_opt, 'type': _type}
