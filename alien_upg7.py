import pygame
pygame.mixer.pre_init(44100, 16, 2, 4096)
pygame.init()
pygame.mixer.init()
pygame.font.init()


FPS = 60
TIME = 0
WINDOW_HEIGHT = 700
WINDOW_WIDTH = 1280
RUN_APP = True

SPRITES = {}
BULLETS = {}
ENEMIES = {}
GAME_TEXTS = {}
MENU_TEXTS = {}

WINDOW = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
CLOCK = pygame.time.Clock()

#=============================================================================================CLASSES=============================================================================================#
#=================================================================================================================================================================================================#
#=================================================================================================================================================================================================#
class Sprite():
    def __init__(self,x,y,frames,endless=True,delay=1):
        global SPRITES
        self.id = id(self)
        self.frames = frames
        self.current_frame = self.frames[0]
        self.x = x
        self.y = y
        self.updateSize()
        self.frame_timer = 0
        self.endless = endless
        self.delay = delay
    def scale(self,width,height):
        self.width = width
        self.height = height
        self.frames = [pygame.transform.scale(frame,(self.width,self.height)) for frame in self.frames]
        self.current_frame = pygame.transform.scale(self.current_frame,(self.width,self.height))
    def update(self):
        global SPRITES
        if self.frame_timer%self.delay==0:
            self.current_frame = self.frames[self.frame_timer//self.delay]
            self.updateSize()
        self.frame_timer = (self.frame_timer+1)%len(self.frames*self.delay)
        if not self.endless and self.frame_timer==0:
            del SPRITES[self.id]
            del self
    def updateSize(self):
        self.width = self.current_frame.get_width()
        self.height = self.current_frame.get_height()
    def draw(self):
        global WINDOW
        WINDOW.blit(self.current_frame,(self.x,self.y))
    def addSprite(self):
        SPRITES[self.id] = self
    def setPosition(self,x,y):
        self.x = x
        self.y = y
        
#=================================================================================================================================================================================================#
class MovingObject(Sprite):
    def __init__(self,sprite,speed_x,speed_y):
        Sprite.__init__(self,sprite.x,sprite.y,sprite.frames)
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.prev_x = 0
        self.prev_y = 0
        self.moving = True
    def moveLeft(self):
        if self.moving:
            for i in range(self.speed_x):
                self.prev_x = self.x
                self.x -= 1
                self.checkPositionX()
    def moveRight(self):
        if self.moving:
            for i in range(self.speed_x):
                self.prev_x = self.x
                self.x += 1
                self.checkPositionX()
    def moveUp(self):
        if self.moving:
            for i in range(self.speed_y):
                self.prev_y = self.y
                self.y -= 1
                self.checkPositionY()
    def moveDown(self):
        if self.moving:
            for i in range(self.speed_y):
                self.prev_y = self.y
                self.y += 1
                self.checkPositionY()
    def checkPositionX(self):
        if self.xNotOnWindow():
            self.x = self.prev_x
    def checkPositionY(self):
        if self.yNotOnWindow():
            self.y = self.prev_y
    def xNotOnWindow(self):
        return (self.x<0-self.height) or (self.x>WINDOW_WIDTH)
    def yNotOnWindow(self):
        return (self.y<0-self.height) or (self.y>WINDOW_HEIGHT)
    def setPosition(self,x,y):
        self.x = x
        self.y = y
        self.checkPositionX()
        self.checkPositionY()

#=================================================================================================================================================================================================#
class MoveKeys():
    def __init__(self,key_left,key_right,key_up,key_down):
        self.key_left = key_left
        self.key_right = key_right
        self.key_up = key_up
        self.key_down = key_down
    def setMoveLeft(self,key):
        self.key_left = key
    def setMoveRight(self,key):
        self.key_right = key
    def setMoveUp(self,key):
        self.key_up = key
    def setMoveDown(self,key):
        self.key_down = key
        
#=================================================================================================================================================================================================#
class ShootKey():
    def __init__(self,shoot_key):
        self.shoot_key = shoot_key
    def setMoveDown(self,key):
        self.shoot_key = key

#=================================================================================================================================================================================================#
class MoveController(MoveKeys):
    def __init__(self,moveKeys):
        MoveKeys.__init__(self,moveKeys.key_left,moveKeys.key_right,moveKeys.key_up,moveKeys.key_down)
    def move_control(self):
        keys = pygame.key.get_pressed()
        if keys[self.key_left]:
            try:
                self.moveLeft()
            except Exception:
                pass
        if keys[self.key_right]:
            try:
                self.moveRight()
            except Exception:
                pass
        if keys[self.key_up]:
            try:
                self.moveUp()
            except Exception:
                pass
        if keys[self.key_down]:
            try:
                self.moveDown()
            except Exception:
                pass

#=================================================================================================================================================================================================#
class ShootController(ShootKey):
    shoot_sound = pygame.mixer.Sound('sounds/player_shoot.ogg')
    shoot_sound.set_volume(0.05)
    def __init__(self, shootKey):
        ShootKey.__init__(self,shootKey.shoot_key)
        self.shoot_timer = 0
    def shoot_control(self):
        keys = pygame.key.get_pressed()
        if keys[self.shoot_key]:
            try:
                self.shoot_timer = (self.shoot_timer+1)%5
                if self.shoot_timer == 0:
                    self.shoot()
                    self.shoot_sound.stop()
                    self.shoot_sound.play()
            except Exception:
                pass

#=================================================================================================================================================================================================#
class Bullet(MovingObject):
    def __init__(self,movingObject,damage):
        global BULLETS
        MovingObject.__init__(self,Sprite(movingObject.x,movingObject.y,movingObject.frames),movingObject.speed_x,movingObject.speed_y)
        self.damage = damage
    def checkPositionX(self):
        if self.xNotOnWindow():
            try:
                del BULLETS[self.id]
                del self
            except KeyError:        
                return
    def checkPositionY(self):
        if self.yNotOnWindow():
            try:
                del BULLETS[self.id]
                del SPRITES[self.id]
                del self
            except KeyError:        
                return
    def checkKill(self):
        global ENEMIES
        ENEMIES_COPY = ENEMIES.copy()
        for enemy in ENEMIES_COPY.values():
            if pygame.Rect(self.x,self.y,self.width,self.height).colliderect(pygame.Rect(enemy.x,enemy.y,enemy.width,enemy.height)):            
                try:
                    enemy.destroy()
                    del BULLETS[self.id]
                    del SPRITES[self.id]
                    del self
                    return
                except KeyError:
                    return
                
#=================================================================================================================================================================================================#
class ShootingObject():
    def __init__(self,bullet,gun_x,gun_y): 
        self.bullet = Bullet(MovingObject(Sprite(bullet.x,bullet.y,bullet.frames),bullet.speed_x,bullet.speed_y),bullet.damage)
        self.gun_x_position = gun_x
        self.gun_y_position = gun_y
    def shoot(self):
        global BULLETS,SPRITES
        bullet = Bullet(MovingObject(Sprite(self.x+self.gun_x_position,self.y+self.gun_y_position,self.bullet.frames),self.bullet.speed_x,self.bullet.speed_y),self.bullet.damage)
        BULLETS[bullet.id] = bullet
        SPRITES[bullet.id] = bullet
            
#=================================================================================================================================================================================================#
class player(MovingObject,ShootingObject,MoveController,ShootController):
    def __init__(self,movingObject,shootingObject,moveController,shootController):
        MovingObject.__init__(self,Sprite(movingObject.x,movingObject.y,movingObject.frames),movingObject.speed_x,movingObject.speed_y)
        ShootingObject.__init__(self,Bullet(MovingObject(Sprite(bullet.x,bullet.y,bullet.frames),bullet.speed_x,bullet.speed_y),bullet.damage),shootingObject.gun_x_position,shootingObject.gun_y_position)
        MoveController.__init__(self,MoveKeys(moveController.key_left,moveController.key_right,moveController.key_up,moveController.key_down))
        ShootController.__init__(self,ShootKey(shootController.shoot_key))
        self.life = 200
        self.score = 0
    def control(self):
        self.move_control()
        self.shoot_control()
    def checkCollision(self):
        global ENEMIES
        ENEMIES_COPY = ENEMIES.copy()
        for enemy in ENEMIES_COPY.values():
            if pygame.Rect(self.x,self.y,self.width,self.height).colliderect(pygame.Rect(enemy.x,enemy.y,enemy.width,enemy.height)):
                enemy.destroy()
                self.life -= 10
    def reset(self):
        self.x = 500
        self.y = 600
        self.score = 0
        self.life = 200

#=================================================================================================================================================================================================#
class Enemy(MovingObject,ShootingObject):
    destroy_frames = [pygame.image.load("images/boom/image_part_"+"0"*(3-len(str(i)))+str(i)+".png") for i in range(1,29)]
    def __init__(self, movingObject,shootingObject):
        global ENEMIES
        MovingObject.__init__(self,Sprite(movingObject.x,movingObject.y,movingObject.frames),movingObject.speed_x,movingObject.speed_y)
        ShootingObject.__init__(self,Bullet(MovingObject(Sprite(bullet.x,bullet.y,bullet.frames),bullet.speed_x,bullet.speed_y),bullet.damage),shootingObject.gun_x_position,shootingObject.gun_y_position)
        ENEMIES[self.id] = self
    def checkPositionX(self):
        if self.xNotOnWindow():
            try:
                del SPRITES[self.id]
                del ENEMIES[self.id]
                del self
            except KeyError:
                return
    def checkPositionY(self):
        global player
        if self.y>WINDOW_HEIGHT:                                 #??????????????????????
            player.life -= 5
            try:
                del SPRITES[self.id]
                del ENEMIES[self.id]
                del self
            except KeyError:
                return
    def destroy(self):  
        Sprite(self.x-45,self.y-30,self.destroy_frames,False).addSprite()
        player.score += 1
        try:
            del SPRITES[self.id]
            del ENEMIES[self.id]
            del self    
        except KeyError:
            return
        
#=================================================================================================================================================================================================#
class WindowText():
    font = pygame.font.SysFont(None, 30)
    def __init__(self,text,x,y,color=(0,0,0)):
        global TEXTS       
        self.x = x
        self.y = y
        self.id = id(self)
        self.color = color
        self.setText(text)
    def setText(self,text):
        self.text = self.font.render(text, False, self.color)
    def draw(self):
        global WINDOW
        WINDOW.blit(self.text,(self.x,self.y))

class GameText(WindowText):
    def __init__(self,text,x,y,color=(0,0,0)):
        global GAME_TEXT
        WindowText.__init__(self,text,x,y,color)
        GAME_TEXTS[self.id] = self
class MenuText(WindowText):
    def __init__(self,text,x,y,color=(0,0,0)):
        global GAME_TEXT
        WindowText.__init__(self,text,x,y,color)
        MENU_TEXTS[self.id] = self
        
        
#=================================================================================================================================================================================================#
#=================================================================================================================================================================================================#
#=================================================================================================================================================================================================#
        
        
        
        
#=========================================================================================FUNCTIONS===============================================================================================#
#=================================================================================================================================================================================================#
#=================================================================================================================================================================================================#      
def drawSprites():
    global SPRITES, player
    SPRITES_COPY = SPRITES.copy()
    for sprite in SPRITES_COPY.values():
        sprite.update()
        sprite.draw() 
    player.draw()
def moveBullets():
    global BULLETS
    BULLETS_COPY = BULLETS.copy()
    for bullet in BULLETS_COPY.values():
        bullet.moveUp() 
        bullet.checkKill()
def moveEnemies():
    global ENEMIES
    ENEMIES_COPY = ENEMIES.copy()
    for enemy in ENEMIES_COPY.values():
        enemy.moveDown()
def drawGameTexts():
    global GAME_TEXTS
    for text in GAME_TEXTS.values():
        text.draw()
def drawMenuTexts():
    global MENU_TEXTS
    for text in MENU_TEXTS.values():
        text.draw()
def iteration():
    player.control()
    player.checkCollision()
    moveBullets()
    moveEnemies()
    drawSprites()
    pygame.draw.line(WINDOW,(255,0,0),(10,10),(player.life*2,10),10)
    drawGameTexts()
def drawMenu():
    bg.draw()
    drawMenuTexts()
def createEnemies(speed):
    enemy_frames = [pygame.image.load('images/enemy/enemy_'+str(i)+'.png') for i in range(2)]
    enemy_moving_object = MovingObject(Sprite(10,10,enemy_frames),1,speed)
    enemy_shooting_object = ShootingObject(bullet,0,0)
    for y in range(3):
        for x in range(4,int(WINDOW_WIDTH/70)-5):
            enemy = Enemy(enemy_moving_object,enemy_shooting_object)
            enemy.scale(60,80)
            enemy.x = x*70
            enemy.y = -300+y*100
            enemy.addSprite()
#=================================================================================================================================================================================================#
#=================================================================================================================================================================================================#
#=================================================================================================================================================================================================#
        

bg_frames = [pygame.image.load('images/bg/frame_'+str(i)+'_delay-0.08s.png') for i in range(24)]
bg = Sprite(0,0,bg_frames,True,3)
bg.scale(WINDOW_WIDTH,WINDOW_HEIGHT)
bg.addSprite()  

bullet_frames = [pygame.image.load('images/bullet/bullet.png') for i in range(1)]
bullet_object = MovingObject(Sprite(10,200,bullet_frames),0,20)
bullet = Bullet(bullet_object,0)
bullet.scale(8,40)

player_frames = [pygame.image.load('images/basic_ship/ship-'+str(i)+'.png') for i in range(7)]
player_moving_object = MovingObject(Sprite(500,600,player_frames),10,10)
player_shooting_object = ShootingObject(bullet,45,0)
move_controller = MoveController(MoveKeys(pygame.K_LEFT,pygame.K_RIGHT,pygame.K_UP,pygame.K_DOWN))
shoot_controller = ShootController(ShootKey(pygame.K_q))
player = player(player_moving_object,player_shooting_object,move_controller,shoot_controller)
player.addSprite()


new_game_text = MenuText('Press SPACE to start new game',425,100,(255,255,255))
escape_text = MenuText('Press ESC to exit',490,150,(255,255,255))
move_key_text = MenuText("Moving - <- ->",500,200,(255,255,255))
shoot_key_text = MenuText('Shoot - q',520,250,(255,255,255))
menu_score_text = MenuText("",515,300,(255,255,255))

game_score_text = GameText("",10,30,(255,255,255))

def game():
    RUN_GAME = True
    enemies_speed = 0
    while RUN_GAME:
        game_score_text.setText("SCORE: "+str(player.score))
        CLOCK.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUN_GAME = False
                pygame.quit()
        iteration()
        pygame.display.update()
        if len(ENEMIES)==0:
            enemies_speed = min(enemies_speed+1,4)
            createEnemies(enemies_speed)
        if player.life <= 0:
            RUN_GAME = False
    return player.score

while RUN_APP:
    drawMenu()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
            elif event.key == pygame.K_SPACE:
                SPRITES = {}
                BULLETS = {}
                ENEMIES = {}
                bg.addSprite()
                player.reset()
                player.addSprite()
                score = game()
                menu_score_text.setText("SCORE: "+str(score))
    pygame.display.update()               
pygame.quit()


