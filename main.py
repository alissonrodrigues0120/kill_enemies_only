import pgzrun
import random

# Configurações do jogo
WIDTH = 800
HEIGHT = 600
TITLE = "KILL ENEMIES only"
FPS = 30

# Estados do jogo
MENU = 0
PLAYING = 1
game_state = MENU

# Sons e música
music.play("background_music")
music.set_volume(0.5)
shoot_sound = sounds.load("shoot.wav")
enemy_death_sound = sounds.load("enemy_death.wav")

# Variáveis globais
player = None
enemies = []
bullets = []
platforms = []
music_enabled = True
jump_pressed = False

class Platform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.actor = Actor("platform_image")  # Usa imagem da plataforma
        self.actor.x = self.x + self.width // 2
        self.actor.y = self.y + self.height // 2

    def colliderect(self, actor):
        return (actor.right > self.x and actor.left < self.x + self.width and
                actor.bottom > self.y and actor.top < self.y + self.height)

    def draw(self):
        self.actor.draw()


class Player(Actor):
    def __init__(self):
        super().__init__("player_idle_right")
        self.direction = "right"
        self.speed = 5
        self.gravity = 0.5
        self.velocity_y = 0
        self.animation_frames = {
            "idle": {"right": ["player_idle_right"], "left": ["player_idle_left"]},
            "walk": {"right": ["walk1_right", "walk2_right"], "left": ["walk1_left", "walk2_left"]},
            "jump": {"right": ["player_jump_right"], "left": ["player_jump_left"]}
        }
        self.current_animation = "idle"
        self.frame_index = 0
        self.animation_timer = 0

    def update(self):
        if keyboard.left:
            self.direction = "left"
            self.x -= self.speed
            if self.on_ground():
                self.current_animation = "walk"
        elif keyboard.right:
            self.direction = "right"
            self.x += self.speed
            if self.on_ground():
                self.current_animation = "walk"
        else:
            if self.on_ground():
                self.current_animation = "idle"

        self.animation_timer += 1
        if self.animation_timer >= 5:
            frames = self.animation_frames[self.current_animation][self.direction]
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.image = frames[self.frame_index]
            self.animation_timer = 0

        self.y += self.velocity_y
        self.velocity_y += self.gravity

        landed = False
        for platform in platforms:
            if platform.colliderect(self):
                if self.velocity_y > 0:
                    self.bottom = platform.y
                    self.velocity_y = 0
                    landed = True

        if not self.on_ground() and not landed:
            self.current_animation = "jump"

    def jump(self):
        if self.on_ground():
            self.velocity_y = -12

    def on_ground(self):
        for platform in platforms:
            if (self.bottom >= platform.y - 5 and self.bottom <= platform.y + 5 and
                self.right > platform.x and self.left < platform.x + platform.width):
                return True
        return False

class Enemy(Actor):
    def __init__(self, x, y):
        super().__init__("enemy_idle_right")
        self.direction = "right"
        self.speed = 2
        self.x = x
        self.y = y
        self.path_left = self.x - 50
        self.path_right = self.x + 50
        self.animation_frames = {
            "walk": {"right": ["enemy_walk1_right", "enemy_walk2_right"],
                     "left": ["enemy_walk1_left", "enemy_walk2_left"]}
        }
        self.current_animation = "walk"
        self.frame_index = 0
        self.animation_timer = 0

    def update(self):
        if self.direction == "right":
            self.x += self.speed
            if self.x > self.path_right:
                self.direction = "left"
        else:
            self.x -= self.speed
            if self.x < self.path_left:
                self.direction = "right"

        self.animation_timer += 1
        if self.animation_timer >= 5:
            frames = self.animation_frames[self.current_animation][self.direction]
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.image = frames[self.frame_index]
            self.animation_timer = 0

class Bullet(Actor):
    def __init__(self, x, y, direction):
        super().__init__("bullet")
        self.direction = direction
        self.speed = 8
        self.x = x
        self.y = y

    def update(self):
        if self.direction == "right":
            self.x += self.speed
        else:
            self.x -= self.speed
        if self.x < 0 or self.x > WIDTH:
            bullets.remove(self)

def setup_game():
    global player, enemies, platforms
    player = Player()
    player.x = 160  # Em cima da casa
    player.y = 60

    platforms = [
        Platform(50, 90, 220, 40),     # Plataforma da casa
        Platform(30, 270, 190, 40),    # Plataforma à esquerda
        Platform(270, 300, 210, 30),   # Plataforma central com tronco
        Platform(530, 140, 220, 40),   # Plataforma direita alta
        Platform(520, 400, 240, 40)    # Plataforma direita baixa
    ]

    enemies = [
        Enemy(120, 254),   # Em cima da plataforma esquerda
        Enemy(360, 284),   # Em cima do tronco
        Enemy(610, 124),   # Em cima da direita alta
        Enemy(610, 384)    # Em cima da direita baixa
    ]

def update():
    global game_state, enemies, jump_pressed

    if game_state == PLAYING:
        if keyboard.up and not jump_pressed:
            player.jump()
            jump_pressed = True
        if not keyboard.up:
            jump_pressed = False

        player.update()
        if player.bottom > HEIGHT:
            game_state = MENU
        for enemy in enemies:
            enemy.update()
        if keyboard.space:
            direction = player.direction
            bullet = Bullet(player.x, player.y, direction)
            bullets.append(bullet)
            shoot_sound.play()

        for bullet in bullets[:]:
            bullet.update()
            for enemy in enemies[:]:
                if bullet.colliderect(enemy):
                    enemy_death_sound.play()
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    break

        for enemy in enemies:
            if player.colliderect(enemy):
                game_state = MENU

    elif game_state == MENU:
        if keyboard.RETURN:
            setup_game()
            game_state = PLAYING
        if keyboard.m:
            toggle_music()
        if keyboard.ESCAPE:
            exit()

def toggle_music():
    global music_enabled
    music_enabled = not music_enabled
    if music_enabled:
        music.unpause()
    else:
        music.pause()

def draw():
    if game_state == MENU:
        draw_menu()
    elif game_state == PLAYING:
        draw_game()

def draw_menu():
    screen.clear()
    screen.blit("menu_background", (0, 0))
    screen.draw.text("START - Press Enter", center=(WIDTH//2, HEIGHT//2 - 100), fontsize=40, color="white")
    screen.draw.text(f"Music: {'ON' if music_enabled else 'OFF'} - Press 'M'", center=(WIDTH//2, HEIGHT//2 - 40), fontsize=30, color="yellow")
    screen.draw.text("EXIT - Press Esc", center=(WIDTH//2, HEIGHT//2 + 20), fontsize=40, color="red")
    screen.draw.text("Controls:", center=(WIDTH//2, HEIGHT//2 + 80), fontsize=30, color="cyan")
    screen.draw.text("Move Left/Right - Arrow Keys", center=(WIDTH//2, HEIGHT//2 + 120), fontsize=25, color="white")
    screen.draw.text("Jump - Up Arrow", center=(WIDTH//2, HEIGHT//2 + 150), fontsize=25, color="white")
    screen.draw.text("Shoot - Spacebar", center=(WIDTH//2, HEIGHT//2 + 180), fontsize=25, color="white")

def draw_game():
    screen.fill((0, 0, 0))
    screen.blit("forest_background", (0, 0))

    for platform in platforms:
        platform.draw()
    
    player.draw()

    for enemy in enemies:
        enemy.draw()

    for bullet in bullets:
        bullet.draw()

pgzrun.go()

