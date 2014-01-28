# -*- coding: utf-8 -*-

from .kate_selection_info import *


@kate.init
def init():
  global plugin
  plugin = Plugin()
  
@kate.unload
def unload():
    global plugin
    if plugin:
        del plugin
        plugin = None
