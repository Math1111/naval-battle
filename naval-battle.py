import pygame
import pygame.mixer
import sys

pygame.init()
pygame.mixer.init()

# Музыка
pygame.mixer.music.load("music.mp3")
pygame.mixer.music.play(-1)

shot_sound = pygame.mixer.Sound("shot.mp3")
hit = pygame.mixer.Sound("www.mp3")

# Экран и кадры
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Моя игра")
clock = pygame.time.Clock()
FPS = 60

# Фон и шрифт
menu_bg = pygame.image.load("background.png")
splash = pygame.image.load("splash.jpg")
font = pygame.font.SysFont("comicsansms", 40)

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Состояние
state = "splash"  # splash, menu, game, name_input
score = 10
name = ""

# Игровые объекты
ship = pygame.Rect(WIDTH - 100, 200, 40, 60)  # У правого края
launcher = pygame.Rect(50, HEIGHT // 2 - 25, 20, 50)
missiles = []
ship_speed_y = 2 # Быстрее
launcher_speed_y = 0
ship_alive = True

def draw_text(text, x, y, center=False, color=BLACK):
    t = font.render(text, True, color)
    rect = t.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(t, rect)

def run_game():
    global ship_speed_y
    global score, ship_alive, launcher_speed_y, missiles, state

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]: launcher_speed_y = -4
    elif keys[pygame.K_s]: launcher_speed_y = 4
    else: launcher_speed_y = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                missile = pygame.Rect(launcher.right, launcher.centery - 5, 10, 10)
                missiles.append((missile, 3, 0))
                shot_sound.play()
            elif event.key == pygame.K_ESCAPE:
                state = "menu"

    # Движение и столкновения
    for missile, dx, dy in missiles[:]:
        missile.move_ip(dx, dy)
        if not screen.get_rect().contains(missile):
            missiles.remove((missile, dx, dy))
            score -= 1

    for i, (missile, dx, dy) in enumerate(missiles):
        if ship_alive and missile.colliderect(ship):
            missiles.pop(i)
            hit.play()
            score += 1

    if score <= 0:
        ship_alive = False

    if ship_alive:
        ship.move_ip(0, ship_speed_y)
        if ship.top <= 0 or ship.bottom >= HEIGHT:
            ship_speed_y *= -1

    launcher.move_ip(0, launcher_speed_y)
    launcher.clamp_ip(screen.get_rect())

    # Отрисовка
    screen.fill(WHITE)
    if ship_alive:
        pygame.draw.rect(screen, BLUE, ship)
    pygame.draw.rect(screen, BLACK, launcher)
    for missile, _, _ in missiles:
        pygame.draw.rect(screen, RED, missile)
    draw_text(f"Очки: {score}", 10, 10)
    pygame.display.flip()

def run_menu():
    global state

    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                state = "game"
            elif event.key == pygame.K_2:
                state = "name_input"
            elif event.key == pygame.K_3:
                pygame.quit(); sys.exit()

    screen.blit(menu_bg, (0, 0))
    draw_text("1. Играть", WIDTH // 2, 150, center=True)
    draw_text("2. Имя игрока", WIDTH // 2, 200, center=True)
    draw_text("3. Выход", WIDTH // 2, 250, center=True)
    pygame.display.flip()

def run_splash():
    global state
    screen.blit(splash, (0, 0))
    draw_text("Нажмите любую клавишу...", WIDTH // 2, HEIGHT - 60, center=True, color=WHITE)
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        elif event.type == pygame.KEYDOWN:
            state = "menu"

def run_name_input():
    global name, state
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                state = "menu"
            elif event.key == pygame.K_ESCAPE:
                state = "menu"
            elif event.key == pygame.K_BACKSPACE:
                name = name[:-1]
            else:
                name += event.unicode

    screen.fill(WHITE)
    draw_text("Введите имя:", 50, 100)
    draw_text(name, 50, 150)
    pygame.display.flip()

# Главный цикл
while True:
    if state == "splash":
        run_splash()
    elif state == "menu":
        run_menu()
    elif state == "game":
        run_game()
    elif state == "name_input":
        run_name_input()

    clock.tick(FPS)

