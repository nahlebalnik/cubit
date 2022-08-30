import pygame
pygame.init()

wh = w,h = 800,512
screen = pygame.display.set_mode(wh)
pygame.display.set_caption('Кубит 2.1')

fonts = {}
def font(size):
	if not (size in fonts):
		fonts[size] = pygame.font.SysFont('Consolas',size)
	return fonts[size]

class Label:
	def __init__(self,center,text):
		self.center = center
		self.text = text
		
	def draw(self):
		image = font(20).render(self.text,True,[150,30,30])
		rect = image.get_rect(center=self.center)
		screen.blit(image,rect)

def GIR(self,pos,size,background=[150,150,150],color=[130,86,169]):
	self.image = pygame.Surface(size)
	self.image.fill(background)
	pygame.draw.rect(self.image,color,(0,0,*size),3)
	self.rect = self.image.get_rect(x=pos[0],y=pos[1])

class Input:
	def __init__(self,pos,size,hide,max,mask):
		GIR(self,pos,size)
		self.hide = hide
		self.hide_color = [37,70,30]
		self.text = ''
		self.text_color = [122,48,134]

		self.max = max
		self.mask = mask
		self.active = False

	def draw(self):
		screen.blit(self.image,self.rect)
		if self.text:
			screen.blit(font(18).render(self.text,1,self.text_color),(self.rect.x+5,self.rect.y+5))
		else:
			screen.blit(font(18).render(self.hide,1,self.hide_color),(self.rect.x+5,self.rect.y+5))
	
class Button:
	def __init__(self,pos,size,name,func=None,*args):
		GIR(self,pos,size)
		w,h = size
		image = font(20).render(name,True,[150,30,30])
		self.image.blit(image,image.get_rect(center=[w//2,h//2]))
		self.func = func
		self.args = args

	def update(self):
		if self.func != None: self.func(*self.args)

	def draw(self):
		screen.blit(self.image,self.rect)

class Menu:
	def __init__(self,app):
		self.app = app
		self.page = 0
		self.active = True
		self.buttons = {0:[]}
		self.inputs = {0:[]}
		self.labels = {0:[]}

	def add(self,name,*a,**b):
		if name == 0:
			self.buttons[self.page].append(Button(*a,**b))
		elif name == 1:
			self.inputs[self.page].append(Input(*a,**b))
		elif name == 2:
			self.labels[self.page].append(Label(*a,**b))

	def page(self,page):
		self.page = page
		if not (page in self.buttons):
			self.buttons[page] = []
			self.inputs[page] = []
			self.labels[page] = []

	def event(self,events):
		for event in events:
			if event.type == pygame.MOUSEBUTTONDOWN:
				for button in self.buttons[self.page]:
					if button.rect.collidepoint(event.pos):
						button.update()

				for _input in self.inputs[self.page]:
					if _input.rect.collidepoint(event.pos):
						_input.active = True
					else:
						_input.active = False

			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_BACKSPACE:
					for _input in self.inputs[self.page]:
						if _input.active and len(_input.text) > 0:
							_input.text = _input.text[:-1]
				else:
					for _input in self.inputs[self.page]:
						if _input.active and event.unicode in _input.mask and len(_input.text) < _input.max:
							_input.text += event.unicode

	def update(self):
		pass

	def draw(self):
		for button in self.buttons[self.page]:
			button.draw()

		for _input in self.inputs[self.page]:
			_input.draw()

		for label in self.labels[self.page]:
			label.draw()