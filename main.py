import pygame, sys, random
pygame.init()

# Διαστάσεις παραθύρου
X = 900
Y = 600

# Χρώματα
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLOR_PLATFORM = (105, 39, 60)
COLOR_GROUND = (42, 39, 36)

#Παράθυρο
screen = pygame.display.set_mode((X, Y))
pygame.display.set_caption("Commander Keen")
gameIcon = pygame.image.load("images/icon.png")
pygame.display.set_icon(gameIcon)
clock = pygame.time.Clock()
pygame.time.set_timer(pygame.USEREVENT + 1, 10000)

# Ήχοι
pygame.mixer.init()
pygame.mixer.music.load("sounds/music.mp3") # Μουσική
pygame.mixer.music.play(-1) # Μέχρι να κλείσουμε το παράθυρο με το -1
jump = pygame.mixer.Sound("sounds/jump.wav") # Όταν πηδάει
hit = pygame.mixer.Sound("sounds/hit.wav") # Όταν ακουμπάει τη μπάλα

# Fonts
pygame.font.init()
myfont = pygame.font.Font("8-BitMadness.ttf", 50)
textsurface = myfont.render("Nice, keep going!", False, (0, 0, 0)) # Όταν κερδίζει 3 μπάλες

# Επιτάχυνση
acc = 1.5

class Player():
    def __init__(self):
        self.jump = False
        self.left = False
        self.right = False
        self.lives = 5 # Ξεκινάει με 5 ζωές
        self.life = pygame.image.load("images/life.png").convert()
        self.surf = pygame.image.load("images/character.png").convert()
        self.rect = self.surf.get_rect(midbottom=(X//2, Y - 100)) # Αρχική θέση παίκτη
        self.y_speed = 0

    def event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.on_ground():
                    self.jump = True
                    jump.play()
            elif event.type == pygame.USEREVENT + 1:
                enemy.timer = True

        self.left = False
        self.right = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.left = True
        if keys[pygame.K_RIGHT]:
            self.right = True

    def move(self):
        if self.jump:
            self.y_speed = -20
            self.jump = False
        self.rect.bottom += self.y_speed

        if self.left and self.rect.left > 0:
            self.rect.centerx -= 5
        if self.right and self.rect.right < X:
            self.rect.centerx += 5

        if self.on_ground():
            if self.y_speed >= 0:
                self.rect.bottom = p_rects[self.rect.collidelist(p_rects)].top + 1
                self.y_speed = 0
            else:
                self.rect.top = p_rects[self.rect.collidelist(p_rects)].bottom
                self.y_speed = 2
        else:
            self.y_speed += acc

    def on_ground(self):
        collision = self.rect.collidelist(p_rects)
        if collision > -1:
            return True
        else:
            return False

    def draw(self):
        screen.blit(self.surf, self.rect)
        for i in range(self.lives):
            screen.blit(self.life, [i*20 + 20, 20])

class Enemy():
    def __init__(self):
        self.surf = pygame.image.load("images/enemy.png").convert()
        self.rect = self.surf.get_rect(midtop=(X//2, 0)) # Θέση που ξεκινάει ο αντίπαλος
        self.x_speed = 10 # Ταχύτητα
        self.y_speed = 0
        self.timer = False

    def move(self): # Κατεύθυνση και αλλαγή
        self.rect.centerx += self.x_speed
        if self.rect.left <= 0 or self.rect.right >= X:
            self.x_speed *= -1

        if self.on_ground():
            self.rect.bottom = p_rects[self.rect.collidelist(p_rects)].top + 1
            self.y_speed = 0
        else:
            self.y_speed += acc
        self.rect.bottom += self.y_speed

        self.hit()

        if self.timer: # Χρόνος αντιπάλου
            self.timer = False
            self.rect.midtop = (X//2, 0)
            self.x_speed = random.randint(3, 7) * ((self.x_speed > 0) - (self.x_speed < 0))

    def on_ground(self):
        collision = self.rect.collidelist(p_rects)
        if collision > -1:
            return True
        else:
            return False

    def hit(self): # Ζωές και θέση παίκτη όταν ο εχθρός ακουμπάει τον παίκτη
        if player.rect.colliderect(self.rect):
            player.lives -= 1
            player.rect.midbottom = (X//2, Y - 100)
        if player.lives == 0:
            pygame.quit()
            exit()


    def draw(self):
        screen.blit(self.surf, self.rect)

class Ball():
    def __init__(self):
        self.positions = [(45, 335), (800,285),(40, 500), (850, 500)] # Θέσεις που εμφανίζεται η μπάλα
        self.surf = pygame.image.load("images/ball.png").convert()
        self.rect = self.surf.get_rect(midbottom=random.choice(self.positions)) # Random επιλογή από positions
        self.count = 0 # Μετρητής ξεκινάει από το 0
        self.small_surf = pygame.transform.scale(self.surf, (20, 20)) # Μικρή εικόνα μπάλας στο score

    def hit(self):
        if player.rect.colliderect(self.rect): # Αν ο παίχτης ακουμπήσει τη μπαλα αλλάζει position και count + 1
            self.rect.midbottom = random.choice(self.positions)
            self.count += 1
            hit.play() # Ήχος όταν ακουμπάει ο παίχτης τη μπάλα
        elif enemy.rect.colliderect(self.rect):
            self.rect.midbottom = random.choice(self.positions)
            self.count -= 1 # -1 όταν ο αντίπαλος ακουμπάει τη μπάλα
            hit.play() # Ήχος όταν ακουμπάει ο αντίπαλος τη μπάλα
        if self.count >= 3: # Αν έχουμε από 3 και πάνω μπάλες εμφανίζει μήνυμα από πάνω
            screen.blit(textsurface, (150, 0))
    def draw(self):
        screen.blit(self.surf, self.rect)
        for i in range(self.count):
            screen.blit(self.small_surf, [850 - i*20, 20]) # Θέση από μπάλες που έχουμε μαζέψει

class Platform():
    def __init__(self, sizex, sizey, posx, posy, color):
        self.surf = pygame.surface.Surface((sizex, sizey))
        self.rect = self.surf.get_rect(midbottom=(posx, posy))
        self.surf.fill(color)

    def draw(self):
        screen.blit(self.surf, self.rect)

# Πλατφόρμες
platforms = []
platforms.append(Platform(X, 100, X/2, Y, COLOR_GROUND))
platforms.append(Platform(300, 15, 500, 215, COLOR_PLATFORM))
platforms.append(Platform(150, 15, 800, 300, COLOR_PLATFORM))
platforms.append(Platform(150, 15, 500, 420, COLOR_PLATFORM))
platforms.append(Platform(300, 15, 150, 350, COLOR_PLATFORM))
p_rects = [p.rect for p in platforms]

# Δημιοργία των στιγμιοτύπων
player = Player()
enemy = Enemy()
ball = Ball()

while True: # Καλούμε τις μεθόδους μέσα στο loop
    clock.tick(30)
    screen.fill(WHITE) # Χρώμα φόντου

    player.event()
    player.move()
    enemy.move()
    ball.hit()

    player.draw()
    enemy.draw()
    ball.draw()


    for p in platforms: # Ζωγραφίζουμε τις πλατφόρμες
        p.draw()

    pygame.display.flip()
