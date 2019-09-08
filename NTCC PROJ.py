import pygame
import random
from os import path

img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'snd')

height = 600
width = 480
fps = 60

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Star Gaze')
clock = pygame.time.Clock()

white = (255, 255, 255)
black = (0, 0, 0)
red = (250, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)

running = True
game_over = True

font_name = pygame.font.match_font('arial')


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, white)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)


def draw_shield_bar(surf, x, y, pct):
    color = green
    if pct < 0:
        pct = 0
    bar_length = 100
    bar_height = 10
    fill = (pct / 100) * bar_length

    if fill > 50:
        color = green
    elif fill <= 50 or fill > 25:
        color = yellow
        if fill <= 25:
            color = red

    outline_rect = pygame.Rect(x, y, bar_length, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(surf, color, fill_rect)
    pygame.draw.rect(surf, white, outline_rect, 2)


def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50,44))
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .9 / 2)
        #pygame.draw.circle(self.image, red, self.rect.center, self.radius)
        self.rect.centerx = width/2
        self.rect.bottom = height - 10
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()

    def update(self):
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 3000:
            self.hidden = False
            self.rect.centerx = width / 2
            self.rect.bottom = height - 10
        self.speedx = 0
        self.speedya = 0

        keystate = pygame.key.get_pressed()

        if keystate[pygame.K_LEFT]:
            self.speedx = -5
        elif keystate[pygame.K_RIGHT]:
            self.speedx = 5
        if keystate[pygame.K_SPACE]:
            self.shoot()
        if keystate[pygame.K_UP]:
            self.speedya = -5
        elif keystate[pygame.K_DOWN]:
            self.speedya = 5

        self.rect.x += self.speedx
        self.rect.y += self.speedya

        if self.rect.right > width:
            self.rect.right = width
        elif self.rect.left < 0:
             self.rect.left = 0

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)
            shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (width / 2, height + 300)


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(black)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        #pygame.draw.circle(self.image, red, self.rect.center, self.radius)
        self.rect.x = random.randrange(0, width - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.rot = 0
        self.rot_speed= random.randrange(-8,8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now =pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        if self.rect.top > height + 10 or self.rect.left < -25 or self.rect.right > width + 25:
            self.rect.x = random.randrange(0, width - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy

        if self.rect.bottom < 0:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 75

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


def show_go_screen():
    screen.blit(menu_bck, menu_rect)
    draw_text(screen, "STAR GAZE", 64, width / 2, height / 4)
    draw_text(screen, 'Use Arrow keys to move, Space to Fire', 30, width / 2, height / 2)
    draw_text(screen, 'press any key to begin', 22, width / 2, height * 3 / 4 - 10)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False

background = pygame.image.load(path.join(img_dir, 'space5.png')).convert()
background_rect = background.get_rect()

menu_bck = pygame.image.load(path.join(img_dir, 'space6.png')).convert()
menu_rect = background.get_rect()


player_img = pygame.image.load(path.join(img_dir, 'ship.png')).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 20))
player_mini_img.set_colorkey(black)
bullet_img = pygame.image.load(path.join(img_dir, 'bullet.png')).convert()
meteor_images = []
meteor_list = ['met.png', 'met1.png', 'met2.png', 'met3.png', 'met4.png', 'met5.png', 'met6.png']

for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, img)).convert())

explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []

for i in range(8):
    filename = 'regularexplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(black)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(black)
    explosion_anim['player'].append(img)



shoot_sound = pygame.mixer.Sound(path.join(snd_dir, 'fire.wav'))
expl_sounds = []
for snd in ['explode.wav', 'explode1.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(snd_dir, snd)))

player_die_sound = pygame.mixer.Sound(path.join(snd_dir, 'rumble1.ogg'))

pygame.mixer.music.load(path.join(snd_dir, 'bckgrd.ogg'))
pygame.mixer.music.set_volume(0.4)



pygame.mixer.music.play(loops=-1)

while running:
    if game_over:
        show_go_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        player = Player()
        bullets = pygame.sprite.Group()
        all_sprites.add(player)
        for i in range(8):
            newmob()
        score = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update()

    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)

    for hit in hits:
        score += 50 - hit.radius
        random.choice(expl_sounds).play()
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        newmob()

    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius * 1.5
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        newmob()
        if player.shield <= 0:
            player_die_sound.play()
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = 100

    if player.lives == 0 and not death_explosion.alive():
        game_over = True

    clock.tick(fps)
    screen.fill(black)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, width / 2, 10)
    draw_lives(screen, width - 100, 5, player.lives, player_mini_img)
    draw_shield_bar(screen, 5, 5, player.shield)
    pygame.display.flip()

pygame.quit()