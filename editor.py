# -*- coding: UTF-8 -*-

from PySide import QtGui, QtCore
import SettingsWidget, ScenarioData
from ImageCache import ImageCache

class Editor(QtGui.QMainWindow):
	def __init__(self, parent=None):
		super(Editor, self).__init__(parent)
		
		self.scenarioData = ScenarioData.ScenarioData()
		self.scenarioData.loadScenario()
		
		self.imageCache = ImageCache()
		
		self.setWindowTitle("Kiigame - Pelieditori")
		
		# TODO: Menubar
		menubar = self.menuBar()
		
		tabWidget = QtGui.QTabWidget()
		self.setCentralWidget(tabWidget)
		
		self.createMainTab()
		self.createSpaceTab()
		self.createTextsTab()
		
		tabWidget.addTab(self.mainTab, "Päänäkymä")
		tabWidget.addTab(self.spaceTab, "Tila")
		tabWidget.addTab(self.textsTab, "Tekstit")
		
	def createMainTab(self):
		self.mainTab = QtGui.QWidget()
		
		layout = QtGui.QGridLayout()
		self.mainTab.setLayout(layout)
		
		# Room preview
		left_frame = QtGui.QGroupBox("Tilat")
		left_frame_layout = QtGui.QGridLayout()
		left_frame.setLayout(left_frame_layout)
		layout.addWidget(left_frame, 1, 0, 1, 2)
		
		# Set-up widget for showing rooms
		self.left_scene = QtGui.QListWidget(self)
		self.left_scene.setIconSize(QtCore.QSize(200, 200))
		self.left_scene.setViewMode(QtGui.QListView.IconMode)
		self.left_scene.setFlow(QtGui.QListView.LeftToRight)
		self.left_scene.setMovement(QtGui.QListView.Static)
		self.left_scene.itemSelectionChanged.connect(self.roomClicked)
		# TODO: Double click room, display the room view
		left_frame_layout.addWidget(self.left_scene)
		
		self.addViewsCombo = QtGui.QComboBox(self)
		self.addViewsCombo.addItem("Lisää tila")
		self.addViewsCombo.addItem("Huone", userData="room")
		self.addViewsCombo.addItem("Välianimaatio", userData="sequence")
		self.addViewsCombo.currentIndexChanged.connect(self.addViewsComboChanged)
		layout.addWidget(self.addViewsCombo, 0, 0)
		
		self.removeViewsButton = QtGui.QPushButton("Poista valittu tila")
		self.setRemoveViewsButtonDisabled()
		self.removeViewsButton.clicked.connect(self.removeViewsButtonClicked)
		layout.addWidget(self.removeViewsButton, 0, 1)
		
		# Draw rooms and select the first one
		self.drawRooms()
		selectedRoom = self.left_scene.itemAt(0, 0)
		self.left_scene.setCurrentItem(selectedRoom)
		
		# Room items
		middle_frame = QtGui.QGroupBox("Tilan esineet")
		middle_frame_layout = QtGui.QVBoxLayout()
		middle_frame.setLayout(middle_frame_layout)
		layout.addWidget(middle_frame, 1, 2, 1, 2)
		
		# Set-up widget for showing room items
		self.middle_scene = QtGui.QListWidget(self)
		self.middle_scene.setIconSize(QtCore.QSize(100, 100))
		self.middle_scene.setMovement(QtGui.QListView.Static)
		self.middle_scene.itemSelectionChanged.connect(self.roomItemClicked)
		middle_frame_layout.addWidget(self.middle_scene)
		
		self.addObjectsCombo = QtGui.QComboBox(self)
		self.addObjectsCombo.addItem("Lisää esine valittuun huoneeseen")
		self.addObjectsCombo.addItem("Kiinteä esine", userData="object")
		self.addObjectsCombo.addItem("Käyttöesine", userData="item")
		self.addObjectsCombo.addItem("Ovi", userData="door")
		self.addObjectsCombo.addItem("Säiliö", userData="container")
		self.addObjectsCombo.addItem("Este", userData="obstacle")
		self.addObjectsCombo.currentIndexChanged.connect(self.addObjectsComboChanged)
		layout.addWidget(self.addObjectsCombo, 0, 2)
		
		self.removeObjectsButton = QtGui.QPushButton("Poista valittu esine")
		self.setRemoveObjectsButtonDisabled()
		self.removeObjectsButton.clicked.connect(self.removeObjectsButtonClicked)
		layout.addWidget(self.removeObjectsButton, 0, 3)
		
		self.drawRoomItems()
		
		# Settings for items and rooms
		right_frame = QtGui.QGroupBox("Asetukset")
		right_frame_layout = QtGui.QVBoxLayout()
		right_frame.setLayout(right_frame_layout)
		layout.addWidget(right_frame, 1, 4)
		
		self.settingsWidget = SettingsWidget.SettingsWidget(self)
		self.settingsWidget.displayOptions(selectedRoom.room)
		
		# Set settings widget scrollable instead resizing main window
		scrollArea = QtGui.QScrollArea()
		scrollArea.setWidgetResizable(True)
		scrollArea.setWidget(self.settingsWidget)
		right_frame_layout.addWidget(scrollArea)
		
	def addViewsComboChanged(self):
		selected = self.addViewsCombo.itemData(self.addViewsCombo.currentIndex())
		if not (selected in ("room", "sequence")):
			return
		self.createObject(selected)
		
		self.addObjectsCombo.setCurrentIndex(0)
		self.left_scene.setCurrentRow(self.left_scene.count()-1)
		
	def removeViewsButtonClicked(self):
		selected = self.left_scene.currentItem()
		
		row = self.left_scene.currentRow()
		self.left_scene.takeItem(row)
		
		self.drawRoomItems()
		
	def addObjectsComboChanged(self):
		selected = self.addObjectsCombo.itemData(self.addObjectsCombo.currentIndex())
		if not (selected in ("object", "item", "door", "container", "obstacle", )):
			return
		self.createObject(selected)
		
		self.addObjectsCombo.setCurrentIndex(0)
		self.middle_scene.setCurrentRow(self.middle_scene.count()-1)
		
	def removeObjectsButtonClicked(self):
		selected = self.middle_scene.currentItem()
		
		row = self.middle_scene.currentRow()
		self.middle_scene.takeItem(row)
		
	def setRemoveObjectsButtonDisabled(self):
		selected = self.middle_scene.selectedItems()
		if (len(selected) == 0):
			isDisabled = True
		else:
			isDisabled = False
			
		self.removeObjectsButton.setDisabled(isDisabled)
		
	def setRemoveViewsButtonDisabled(self):
		selected = self.left_scene.selectedItems()
		if (len(selected) == 0):
			isDisabled = True
		else:
			isDisabled = False
			
		self.removeViewsButton.setDisabled(isDisabled)
		
	def createSpaceTab(self):
		self.spaceTab = QtGui.QWidget()

		layout = QtGui.QHBoxLayout()
		self.spaceTab.setLayout(layout)
		
		# Another settings widget for room view
		self.spaceSettingsWidget = SettingsWidget.SettingsWidget(self)
		selectedRoom = self.left_scene.selectedItems()[0]
		self.spaceSettingsWidget.displayOptions(selectedRoom.room)

		# Room
		left_frame = QtGui.QGroupBox("Tila")
		left_frame_layout = QtGui.QVBoxLayout()
		left_frame.setLayout(left_frame_layout)
		layout.addWidget(left_frame)

		# Settings
		right_frame = QtGui.QGroupBox("Asetukset")
		right_frame_layout = QtGui.QVBoxLayout()
		right_frame.setLayout(right_frame_layout)
		layout.addWidget(right_frame)
		
		scrollArea = QtGui.QScrollArea()
		scrollArea.setWidgetResizable(True)
		scrollArea.setWidget(self.spaceSettingsWidget)
		
		right_frame_layout.addWidget(scrollArea)
		self.spaceScene = QtGui.QGraphicsScene(self)
		view = QtGui.QGraphicsView(self.spaceScene)
		view.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
		left_frame_layout.addWidget(view)
		
		self.updateSpaceTab()
	
	def updateSpaceTab(self):
		selectedRoom = self.left_scene.selectedItems()[0]
		self.spaceSettingsWidget.displayOptions(selectedRoom.room)
		
		# Display room image
		pixmap = self.imageCache.createPixmap(self.scenarioData.dataDir + "/" + selectedRoom.room.getRepresentingImage().getSource())
		self.spaceScene.addPixmap(pixmap)
		
		# Display objects
		for item in selectedRoom.room.getItems():
			# TODO: Resolve handling text objects (issue #8)
			if (item.getClassname() == "Text"):
				continue
				
			img = item.getRepresentingImage()
			#print(self.scenarioData.dataDir + "/" + img.getSource())
			pixmap = self.imageCache.createPixmap(self.scenarioData.dataDir + "/" + img.getSource())
			pixItem = QtGui.QGraphicsPixmapItem(pixmap)
			pixItem.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
			
			#TODO: Game crops some amount from the borders, insert that amount into items offset value
			pos = item.getPosition()
			pixItem.setPos(pos[0],pos[1])
			self.spaceScene.addItem(pixItem)
			
	def createObject(self, objectType):
		selectedRoom = self.left_scene.selectedItems()[0]
		if (objectType == "room"):
			newObject = self.scenarioData.addRoom(None, None, None)
			
		elif (objectType == "sequence"):
			print("create sequence")
			
		elif (objectType == "object"):
			newObject = selectedRoom.room.addObject()
		elif (objectType == "item"):
			newObject = selectedRoom.room.addItem()
		elif (objectType == "door"):
			newObject = selectedRoom.room.addDoor()
		elif (objectType == "container"):
			newObject = selectedRoom.room.addContainer()
		elif (objectType == "obstacle"):
			newObject = selectedRoom.room.addObstacle()
		else:
			return
		print("new ovject", newObject, newObject.id)
		
		#widget.setRepresentingImage("airfreshener.png")
		newObject.getRepresentingImage().setSource("airfreshener.png")
		widgetItem = ItemWidget(newObject, self.scenarioData.dataDir)
		self.middle_scene.addItem(widgetItem)
		
	def createTextsTab(self):
		self.textsTab = QtGui.QWidget()

		layout = QtGui.QHBoxLayout()
		self.textsTab.setLayout(layout)

		# Objects
		left_frame = QtGui.QGroupBox("Esineet")
		left_frame_layout = QtGui.QVBoxLayout()
		left_frame.setLayout(left_frame_layout)
		layout.addWidget(left_frame)
		
		# Set-up widget for showing room items
		self.text_scene = QtGui.QTableWidget(self)
		#text_scene.setMovement(QtGui.QListView.Static)
		self.text_scene.itemSelectionChanged.connect(self.textItemClicked)
		
		left_frame_layout.addWidget(self.text_scene)
		
		# Draw all items and their progress bar
		objects = self.scenarioData.getAllObjects()
		self.drawTextItems(objects)
		
		# Select the first item
		selectedItem = self.text_scene.itemAt(0, 0)
		self.text_scene.setCurrentItem(selectedItem)
		
		# Texts
		self.texts_frame = QtGui.QGroupBox("Tekstit - %s" %(selectedItem.text()))
		self.texts_frame_layout = QtGui.QVBoxLayout()
		self.texts_frame.setLayout(self.texts_frame_layout)
		layout.addWidget(self.texts_frame)
		
		self.textsWidget = TextsWidget(self.scenarioData)
		self.texts_frame_layout.addWidget(self.textsWidget)
		
		self.textsWidget.displayTexts(selectedItem)
		
	# Click on an object in the texts tab object list
	def textItemClicked(self):
		selected = self.text_scene.currentItem()
		if (selected):
			# TODO: Handle this better? Now there's a warning at the
			# beginning that textsWidget doesn't exist
			self.textsWidget.displayTexts(selected)
			self.texts_frame.setTitle("Tekstit - %s" %(selected.text()))
		
	def drawTextItems(self, textItems):
		row = 0
		secretCount = textItems.pop()
		imgCount = textItems.pop()
		textItems = textItems.pop()
		
		self.text_scene.setRowCount(0)
		self.text_scene.setColumnCount(2)
		
		# Disable sorting for row count, enable it after adding items
		self.text_scene.setSortingEnabled(False)
		
		for item in textItems:
			for itemImage in item.getImages():
				textCount = len(item.texts)
				
				# Add a row
				self.text_scene.insertRow(self.text_scene.rowCount())
				
				# Add a text item to the first column
				widgetItem = TextItemWidget(itemImage, item, self.scenarioData.dataDir, 25)
				self.text_scene.setItem(row, 0, widgetItem)
				
				# Maximum amount of texts for item
				maxAmount = 0
				if ("examine" in item.texts):
					maxAmount += 1
					
				if ("pickup" in item.texts):
					maxAmount += 1
				# TODO: Sorting doesn't work, fix possibly by setItem here and setCellWidget inside item
				nameCount = 0
				if ("name" in item.texts):
					textCount -= 1
				
				if (item.__class__.__name__ == "Item"
					or item.getRepresentingImage().imageAttributes["category"] == "reward"):
					# Max amount is number of all images minus item itself and secrets (no interaction)
					maxAmount += imgCount-1-secretCount
					
					# Different pictures for the inventory and the room
					if ("src2" in itemImage.imageAttributes):
						maxAmount = 1
					
				# Add a progressbar to the second column
				#progressBarItem = ProgressBarItemWidget(item, maxAmount)
				progressBar = QtGui.QProgressBar()
				progressBar.setMinimum(0)
				progressBar.setMaximum(maxAmount)
				progressBar.setValue(textCount)
				
				self.text_scene.setCellWidget(row, 1, progressBar)
				
				row += 1
		self.text_scene.setSortingEnabled(True)
	
	# Click on a room in the main tab
	def roomClicked(self):
		self.drawRoomItems()
		self.settingsWidget.displayOptions(self.left_scene.selectedItems()[0].room)
		self.updateSpaceTab()
		self.setRemoveViewsButtonDisabled()
		
	# Click on an item in the main tab room preview
	def roomItemClicked(self):
		# TODO: Clear when suitable (like when no items in the view)
		selected = self.middle_scene.currentItem()
		if (selected):
			self.settingsWidget.displayOptions(selected.item)
			
		self.setRemoveObjectsButtonDisabled()
		
	# Draw the leftmost frame items
	def drawRooms(self):
		self.left_scene.clear()
		
		# Rooms
		for i in range(len(self.scenarioData.roomList)):
			room = self.scenarioData.roomList[i]
			widgetItem = ViewWidget(room, self.scenarioData.dataDir)
			
			self.left_scene.addItem(widgetItem)
			
		# Sequences
		for i in range(len(self.scenarioData.sequenceList)):
			sequence = self.scenarioData.sequenceList[i]
			widgetItem = ViewWidget(sequence, self.scenarioData.dataDir)
			
			self.left_scene.addItem(widgetItem)
			
	# Draw the middle frame room items
	def drawRoomItems(self):
		self.middle_scene.clear()
		
		# There might not be a selection in left_scene
		try:
			roomItems = self.left_scene.currentItem().room.getItems()
		except IndexError:
			return
			
		for item in roomItems:
			# TODO: Resolve handling text objects (issue #8)
			if (item.getClassname() == "Text"):
				continue
				
			widgetItem = ItemWidget(item, self.scenarioData.dataDir)
			
			self.middle_scene.addItem(widgetItem)
			
	def getImageDir(self):
		return self.scenarioData.dataDir
		
	def getRoomObjects(self):
		return self.scenarioData.getRooms()
		
	# Get given types of objects found in rooms
	def getObjectsByType(self, objectType):
		return self.scenarioData.getObjectsByType(objectType)
		
	# Get the target object that is triggered by the given item
	def getItemUse(self, item):
		return item.getUse()
		
	# Get the general object name for an object type
	def getGeneralName(self, objectType):
		return self.scenarioData.getGeneralName(objectType)
		
# Widget used to display rooms, sequences, start and end views
class ViewWidget(QtGui.QListWidgetItem):
	def __init__(self, room, imageDir, parent=None):
		super(ViewWidget, self).__init__(parent)
		
		self.room = room
		
		roomName = room.getName()
		if not (roomName):
			# TODO: Some common delegate for these namings
			roomName = "Tilalla ei ole nimeä"
		self.setText(roomName)
		
		imagePath = imageDir+"/"+room.getRepresentingImage().getSource()
		icon = QtGui.QIcon(imagePath)
		self.setIcon(icon)
		
# Item widget that represents items in game rooms
class ItemWidget(QtGui.QListWidgetItem):
	def __init__(self, item, imageDir, parent=None):
		super(ItemWidget, self).__init__(parent)
		
		# Row size, especially height
		self.setSizeHint(QtCore.QSize(100,100))
		
		self.item = item
		imageObject = item.getRepresentingImage()
		
		itemName = imageObject.getName()
		if not (itemName):
			itemName = "Esineellä ei ole nimeä"
		self.setText(itemName)
		
		imagePath = imageDir+"/"+imageObject.getSource()
		icon = QtGui.QIcon(imagePath)
		self.setIcon(icon)

# Text item widget that represents items in texts tab
class TextItemWidget(QtGui.QTableWidgetItem):
	def __init__(self, textItem, parentItem, imageDir, cellSize, parent=None):
		super(TextItemWidget, self).__init__(parent)
		
		# Row size, especially height
		self.setSizeHint(QtCore.QSize(cellSize, cellSize))
		
		self.id = textItem.id
		self.textItem = textItem
		self.parentItem = parentItem
		self.objectType = parentItem.__class__.__name__
		self.texts = textItem.texts
		
		if (self.textItem.imageAttributes["category"] == "reward"):
			self.objectType = "Item"
		
		try:
			self.target = parentItem.getUse().getName()
		except:
			self.target = None
		
		try:
			self.useText = parentItem.getUseText()
		except:
			self.useText = ""
		
		textItemName = self.textItem.getName()
		if not (textItemName):
			textItemName = "Esineellä ei ole nimeä"
		else:
			textItemName += self.getImageType()
		self.setText(textItemName)
		
		imagePath = imageDir+"/"+textItem.imageAttributes["src"]
		icon = QtGui.QIcon(imagePath)
		self.setIcon(icon)

	def getImageType(self):
		for attribute in dir(self.parentItem):
			if (self.textItem == getattr(self.parentItem, attribute)):
				if (attribute == "openImage"):
					return " - Auki"
				elif (attribute == "closedImage"):
					return " - Kiinni"
				elif (attribute == "lockedImage"):
					return " - Lukittu"
				elif (attribute == "emptyImage"):
					return " - Tyhjä"
				elif (attribute == "fullImage"):
					return " - Täysi"
				elif (attribute == "blockingImage"):
					return " - Estää"
				elif (attribute == "unblockingImage"):
					return " - Ei estä"
				elif (attribute == "blockedImage"):
					return " - Estetty"
		return ""

# ProgressBar item that shows how much item has texts completed
class ProgressBarItemWidget(QtGui.QTableWidgetItem):
	def __init__(self, textItem, maxAmount, parent=None):
		super(ProgressBarItemWidget, self).__init__(parent)
		
		self.progressBar = QtGui.QProgressBar()
		self.textItem = textItem
		self.maxAmount = maxAmount
		
		self.calculateProgress()

	def calculateProgress(self): # If there's many images, .texts doesn't work!
		
		print ("LOL", self.textItem.id, self.maxAmount, len(self.textItem.texts)-1)
		self.progressBar.setMinimum(0)
		self.progressBar.setMaximum(self.maxAmount)
		self.progressBar.setValue(len(self.textItem.texts)-1)

# Texts widget that shows texts of specific item in the texts tab
class TextsWidget(QtGui.QWidget):
	def __init__(self, scenarioData, parent=None):
		super(TextsWidget, self).__init__(parent)

		self.scenarioData = scenarioData
		self.layout = QtGui.QGridLayout()
		self.setLayout(self.layout)
		
		# Examine
		self.clickTextLabel = QtGui.QLabel("Teksti klikatessa:")
		self.clickTextEdit = QtGui.QTextEdit()
		self.clickTextEdit.setMaximumHeight(50)
		self.clickTextEdit.focusOutEvent = lambda s: self.changeText("click")
		
		# Pickup text
		self.pickupTextLabel = QtGui.QLabel("Teksti poimiessa:")
		self.pickupTextEdit = QtGui.QTextEdit()
		self.pickupTextEdit.setMaximumHeight(50)
		self.pickupTextEdit.focusOutEvent = lambda s: self.changeText("pickup")
		
		# Use text
		self.useTextLabel = QtGui.QLabel("")
		self.useTextEdit = QtGui.QTextEdit()
		self.useTextEdit.setMaximumHeight(50)
		self.useTextEdit.focusOutEvent = lambda s: self.changeText("use")
		
		# Default text
		self.defaultTextLabel = QtGui.QLabel("Oletusteksti puuttuville teksteille:")
		self.defaultTextEdit = QtGui.QTextEdit()
		self.defaultTextEdit.setMaximumHeight(50)
		self.defaultTextEdit.focusOutEvent = lambda s: self.changeText("default")
		
		# Default text without use text
		self.defaultTextLabel2 = QtGui.QLabel("Oletusteksti puuttuville teksteille:")
		self.defaultTextEdit2 = QtGui.QTextEdit()
		self.defaultTextEdit2.setMaximumHeight(50)
		self.defaultTextEdit2.focusOutEvent = lambda s: self.changeText("default")
		
		# Separator
		self.separator = QtGui.QLabel("")
		self.separator.setFrameStyle(QtGui.QFrame.HLine | QtGui.QFrame.Raised)
		
		# Display options for interaction texts
		self.displayOptionGroupBox = QtGui.QGroupBox("Näytä")
		self.displayOptionLayout = QtGui.QVBoxLayout()
		self.displayOptionGroupBox.setLayout(self.displayOptionLayout)
		self.displayAll = QtGui.QRadioButton("Kaikki")
		self.displayMissing = QtGui.QRadioButton("Puuttuvat")
		self.displayDone = QtGui.QRadioButton("Tehdyt")
		
		# Interaction texts
		self.interactionTextGroupBox = QtGui.QGroupBox("Tekstit muiden esineiden kanssa")
		self.interactionTextLayout = QtGui.QVBoxLayout()
		self.text_scene = QtGui.QTableWidget(self)
		self.interactionTextGroupBox.setLayout(self.interactionTextLayout)
		self.text_scene.cellChanged.connect(self.changeInteractionText)

	def displayTexts(self, item):
		self.currentItem = item
		# TODO: InteractionTextGroupBox should take 3/4 of the width
		self.layout.addWidget(self.clickTextLabel, 0, 0)
		self.layout.addWidget(self.clickTextEdit, 1, 0)
		self.layout.addWidget(self.pickupTextLabel, 0, 1)
		self.layout.addWidget(self.pickupTextEdit, 1, 1)
		self.layout.addWidget(self.useTextLabel, 2, 0)
		self.layout.addWidget(self.useTextEdit, 3, 0)
		self.layout.addWidget(self.defaultTextLabel2, 2, 0)
		self.layout.addWidget(self.defaultTextEdit2, 3, 0)
		self.layout.addWidget(self.defaultTextLabel, 2, 1)
		self.layout.addWidget(self.defaultTextEdit, 3, 1)
		self.layout.addWidget(self.separator, 4, 0, 1, 0)
		self.layout.addWidget(self.interactionTextGroupBox, 5, 0, 4, 1)
		self.layout.addWidget(self.displayOptionGroupBox, 5, 1)
		self.layout.addWidget(self.displayAll, 6, 1)
		self.layout.addWidget(self.displayMissing, 7, 1)
		self.layout.addWidget(self.displayDone, 8, 1)
		
		# Display option buttons
		self.displayAll.setChecked(True)
		self.displayOptionLayout.addWidget(self.displayAll)
		self.displayOptionLayout.addWidget(self.displayMissing)
		self.displayOptionLayout.addWidget(self.displayDone)
		
		# Interaction texts
		self.interactionTextLayout.addWidget(self.text_scene)
		self.text_scene.setRowCount(0)
		self.text_scene.setColumnCount(2)
		
		# TODO: Texts for open, closed, empty, full, etc.
		self.itemSettings = [
			self.pickupTextLabel,
			self.pickupTextEdit,
			self.useTextLabel,
			self.useTextEdit,
			self.defaultTextLabel,
			self.defaultTextEdit,
			self.defaultTextLabel2,
			self.defaultTextEdit2,
			self.displayOptionGroupBox,
			self.displayAll,
			self.displayMissing,
			self.displayDone,
			self.interactionTextGroupBox,
		]
		
		if (self.currentItem.textItem.imageAttributes["category"] == "secret" or "src2" in self.currentItem.textItem.imageAttributes):
			self.clickTextEdit.setText(self.currentItem.texts["pickup"])
		else:
			self.clickTextEdit.setText(self.currentItem.texts["examine"])
		
		# Item
		if (self.currentItem.objectType == "Item" and "src2" not in self.currentItem.textItem.imageAttributes):
			targets = self.scenarioData.getAllObjects()[0]
			row = 0
			for setting in self.itemSettings:
				setting.show()
			
			try:
				self.pickupTextEdit.setText(self.currentItem.texts["pickup"])
			except:
				pass
				
			try:
				if (self.currentItem.target):
					# TODO: Better text for label?
					self.useTextLabel.setText("Teksti käyttökohteelle ”%s”:" %(self.currentItem.target))
					self.useTextEdit.setText(self.currentItem.useText)
					self.defaultTextLabel2.hide()
					self.defaultTextEdit2.hide()
				else:
					self.useTextLabel.hide()
					self.useTextEdit.hide()
					self.defaultTextLabel.hide()
					self.defaultTextEdit.hide()
			except:
				self.useTextLabel.hide()
				self.useTextEdit.hide()
				
			try:
				self.defaultTextEdit.setText(self.currentItem.texts["default"])
				self.defaultTextEdit2.setText(self.currentItem.texts["default"])
			except:
				pass
			
			# Interaction texts
			self.text_scene.setSortingEnabled(False)
			for target in targets:
				for targetImage in target.getImages():
					# Target image
					if (targetImage.id == self.currentItem.id or targetImage.imageAttributes["category"] == "secret"):
						continue
					self.text_scene.insertRow(self.text_scene.rowCount())
					imageObject = self.scenarioData.getJSONObject(targetImage.id)
					# TODO: cell size doesn't work!
					targetItem = TextItemWidget(imageObject, self.scenarioData.getObject(target.id), self.scenarioData.dataDir, 100)
					self.text_scene.setItem(row, 0, targetItem)

					# Interaction text with the target
					try:
						interactionText = self.currentItem.texts[targetImage.id]
					except:
						interactionText = ""
					 
					interactionTextItem = QtGui.QTableWidgetItem()
					interactionTextItem.setText(interactionText)
					self.text_scene.setItem(row, 1, interactionTextItem)
					
					row += 1
			self.text_scene.resizeRowsToContents()
			self.text_scene.setSortingEnabled(True)
		
		# Everyone else
		else:
			for setting in self.itemSettings:
				setting.hide()
	
	def changeText(self, textType, gameObject=None, textEdit=None):
		if not (gameObject):
			gameObject = self.currentItem
			
		if (textType == "click"):
			if not (textEdit):
				textEdit = self.clickTextEdit
			gameObject.parentItem.setExamineText(textEdit.toPlainText())
		elif (textType == "pickup"):
			if not (textEdit):
				textEdit = self.pickupTextEdit
			gameObject.parentItem.setPickupText(textEdit.toPlainText())
		elif (textType == "use"):
			if not (textEdit):
				textEdit = self.useTextEdit
			gameObject.parentItem.setUseText(textEdit.toPlainText())
			gameObject.useText = textEdit.toPlainText()
		elif (textType == "default"):
			if not (textEdit):
				textEdit = self.defaultTextEdit
			gameObject.parentItem.setDefaultText(textEdit.toPlainText())
		elif (textType == "interaction"):
			print ("Joo")

	def changeInteractionText(self, row, column):
		item = self.text_scene.itemAt(row, column)
		print ("tewjiotjewiojtiojt", item.id, row, column)
							
if __name__ == '__main__':
	from sys import argv, exit

	app = QtGui.QApplication(argv)

	editor = Editor()
	editor.show()
	exit(app.exec_())
