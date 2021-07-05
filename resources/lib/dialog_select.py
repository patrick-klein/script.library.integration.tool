#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Custon xbmcgui.Dialog.select."""
from resources import ADDON_NAME
import xbmcgui  # pylint: disable=import-error


class Select(xbmcgui.Dialog):
    def __init__(self, heading=ADDON_NAME):
        """CustonDialog __init__."""
        super(Select, self).__init__()
        self.heading = heading
        self.listofitems = None
        self.listofopts = None
        self.extra = None

    def items(self, listofitems, bold=True):
        """Add item lines to dialog select."""
        self.listofitems = listofitems
        self._list = self.listofitems

    def extraopts(self, listofopts):
        """Add option lines to dialog select."""
        self.listofopts = listofopts
        self.extra = True

    def show(self, autoclose=False, useDetails=False, preselect=False, back=False, back_value='Backk'):
        """Open dialog select with all params."""
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
        str_opt = self.listofitems[selection]
        if selection == -1:
            return None
        elif str_opt == back_value:
            return
        if str_opt in self.listofopts:
            _type = 'opt'
            for i, _str in enumerate(self.listofopts):
                if _str == str_opt:
                    selection1 = i
        elif str_opt in self.listofitems:
            _type = 'item'
            selection1 = selection
        return {'index': selection, 'index1': selection1, 'str': str_opt, 'type': _type}
