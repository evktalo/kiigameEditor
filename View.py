import Object
from random import randint

# Virtual class for views
class View(object):
	def __init__(self, id=None):
		# TODO: Check id collision, "running" id instead randint?
		#		Static ID counter?
		if not (id):
			self.id = int(randint(0, 1000000000))
		else:
			self.id = id

# Game cutscenes
class Sequence(View):
	def __init__(self, data, objectAttributes, imageAttributes):
		super(Sequence, self).__init__(objectAttributes["id"])
		self.images = []
		
		self.objectAttributes = objectAttributes
		
		# Create image objects
		for image in imageAttributes:
			sequenceImage = Object.JSONImage(data, self, image)
			self.images.append(sequenceImage)
		
	def deleteImage(self, imageId):
		for image in self.images:
			if (image.id == imageId):
				self.images.remove(image)

# Start menu
class Menu(View):
	def __init__(self, data, beginingImage, background, startButton, creditsButton, emptyButton):
		super(Menu, self).__init__("start")
		
		self.beginingImage = Object.JSONImage(data, self, beginingImage)
		self.background = Object.JSONImage(data, self, background)
		self.startButton = Object.JSONImage(data, self, startButton)
		self.creditsButton = Object.JSONImage(data, self, creditsButton)
		self.emptyButton = Object.JSONImage(data, self, emptyButton)

# End menu
class End(View):
	def __init__(self, endText, endImages):
		super(End, self).__init__("end")
		# TODO: End pictures are stupid
		# TODO: Before handling that, arrange pictures for UI?
		self.endImages = endImages
		self.endText = endText
		
	def deleteImage(self, imageId):
		for image in self.endImages:
			if (image.id == imageId):
				self.endImages.remove(image)

# Any game room
class Room(View):
	def __init__(self, data, viewAttributes, imageAttributes):
		super(Room, self).__init__(imageAttributes["id"])
		
		self.objectList = []
		self.background = Object.JSONImage(data, self, imageAttributes)
		
	def deleteObject(self, objectId):
		for obj in self.objectList:
			if (obj.id == objectId):
				self.objectList.remove(obj)
				
