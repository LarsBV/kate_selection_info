# -*- coding: utf-8 -*-

# Author:  Lars Banner-Voigt
# License: see LICENSE

from PyKDE4.kdecore import i18n
from PyKDE4.kdeui import KAction, KIcon

from PyQt4.QtCore import QObject, Qt
from PyQt4.QtGui import *

from libkatepate.errors import showOk, showError

import kate
import re

      
class Plugin(QObject):
  def __init__(self):
    QObject.__init__(self)

    self.window = kate.mainInterfaceWindow().window()
    
    self.addAction('open_selection_info', None, 'Selection info', 'Ctrl+Alt+I', self.selection_info, 'Tools')
    
    showOk('Selection inits!')
    
    self.dia = QDialog(None, Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)
    self.dia.setStyleSheet('QDialog { border: 1px solid black; }')
    
    layout = QFormLayout(self.dia)
    layout.setSpacing(5)

    ok = QPushButton('Close')
    ok.clicked.connect(self.dia.hide)

    self.chars          = QLabel()
    self.lines          = QLabel()
    self.spaces         = QLabel()
    self.word_count     = QLabel()
    self.chars_no_space = QLabel()
    self.occurences     = QLabel()
    
    
    self.chars          .setTextInteractionFlags(Qt.TextSelectableByMouse)
    self.lines          .setTextInteractionFlags(Qt.TextSelectableByMouse)
    self.spaces         .setTextInteractionFlags(Qt.TextSelectableByMouse)
    self.word_count     .setTextInteractionFlags(Qt.TextSelectableByMouse)
    self.chars_no_space .setTextInteractionFlags(Qt.TextSelectableByMouse)
    self.occurences     .setTextInteractionFlags(Qt.TextSelectableByMouse)

    self.search = QLineEdit()
    self.search.textChanged.connect(self.updateInfo)
    self.search.setPlaceholderText('Regex')
     
    layout.addRow('Characters w. spaces:', self.chars)
    layout.addRow('Newlines:',             self.lines)
    layout.addRow('Word Count:',           self.word_count)
    layout.addRow('Characters:',           self.chars_no_space)
    layout.addRow('Spaces:',               self.spaces)
    layout.addRow( self.search,            self.occurences)
    layout.addRow( ok )
    

  def selection_info(self):
    self.updateInfo()
    self.dia.exec()

  def updateInfo(self):
    text = kate.activeView().selectionText()
    
    if text == '':
      text = kate.activeView().document().text()
    
    chars          = len(text)                           
    spaces         = sum([x.isspace() for x in text]) 
    lines          = sum([x == '\n' for x in text])
    word_count     = len(text.split(None))              
    chars_no_space = chars - spaces        
    
    try:
      junk, occurences = re.subn(self.search.text(), '', text)
    except:
      occurences = "Invalid"
      
    self.chars.setText(          str(chars          ).ljust(10))
    self.lines.setText(          str(lines          ))
    self.spaces.setText(         str(spaces         ))
    self.word_count.setText(     str(word_count     ))
    self.occurences.setText(     str(occurences     ))
    self.chars_no_space.setText( str(chars_no_space ))
    

  def addAction(self, objectName, icon, text, shortcut = "", slot = None, menuName = None):
    act = KAction(KIcon(icon), text, self)
    act.setObjectName(objectName)
    
    # Set shortcut
    if not act.objectName() in kate.configuration:
        kate.configuration[act.objectName()] = shortcut
    act.setShortcut(kate.configuration[act.objectName()])

    # Set slots
    if slot != None:
        act.triggered.connect( slot )
    kate.mainInterfaceWindow().window().actionCollection().addAction(act.objectName(), act)
    
    # Add to menu
    if menuName != None:
      menu = kate.mainInterfaceWindow().window().findChild(QMenu, menuName.lower())
      if menu == None:
        menu = kate.mainInterfaceWindow().window().menuBar().addMenu(menuName)
      menu.addAction(act)

    # Save changes to shortcut
    act.changed.connect( self.onActionChange )
    
    return act

  def onActionChange(self):
      kate.configuration[self.sender().objectName()] =  self.sender().shortcut().toString()
      kate.configuration.save()
      print(self.sender().objectName() + ': Save ' + kate.configuration[self.sender().objectName()])
  
  