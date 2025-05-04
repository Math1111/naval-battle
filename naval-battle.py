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
state = "splash"  # splash, menu, game, name_input, menu_difficulty
score = 10
name = ""
difficulty = 1  # 1 — легко, 2 — средне, 3 — сложно

# Игровые объекты
ship = pygame.Rect(WIDTH - 100, 200, 50, 100)
launcher = pygame.Rect(50, HEIGHT // 2 - 25, 20, 50)
missiles = []
launcher_speed_y = 0
ship_alive = True
ship_speed_y = 2  # Начальная скорость
ship_direction = 1  # 1 - вниз, -1 - вверх
MAX_SPEED = 8  # Максимальная скорость корабля


def draw_text(text, x, y, center=False, color=BLACK):
    t = font.render(text, True, color)
    rect = t.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(t, rect)


def run_game():
    global score, ship_alive, launcher_speed_y, missiles, state, difficulty
    global ship_speed_y, ship_direction

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        launcher_speed_y = -4
    elif keys[pygame.K_s]:
        launcher_speed_y = 4
    else:
        launcher_speed_y = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit();
            sys.exit()
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

    # Движение врага - полностью безопасная версия
    if ship_alive:
        # Рассчитываем скорость в зависимости от сложности
        base_speed = min(difficulty + 1, 3)  # Ограничиваем базовую скорость
        ship_speed_y = base_speed * ship_direction

        # Двигаем корабль
        ship.y += ship_speed_y

        # Проверка границ и изменение направления
        if ship.top <= 0:
            ship.top = 0
            ship_direction = 1  # Двигаемся вниз
        elif ship.bottom >= HEIGHT:
            ship.bottom = HEIGHT
            ship_direction = -1  # Двигаемся вверх

    launcher.move_ip(0, launcher_speed_y)
    launcher.clamp_ip(screen.get_rect())

    # Отрисовка
    screen.fill(WHITE)
    if ship_alive:
        pygame.draw.rect(screen, BLUE, ship)
    pygame.draw.rect(screen, BLACK, launcher)
    for missile, _, _ in missiles:
        pygame.draw.rect(screen, RED, missile)

    if name:
        draw_text(f"{name} набрал очков: {score}", 10, 10)
    else:
        draw_text(f"Очки: {score}", 10, 10)

    pygame.display.flip()


# Остальные функции остаются без изменений
def run_menu():
    global state, difficulty

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit();
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                state = "game"
            elif event.key == pygame.K_2:
                state = "name_input"
            elif event.key == pygame.K_3:
                state = "menu_difficulty"
            elif event.key == pygame.K_4:
                pygame.quit();
                sys.exit()

    screen.blit(menu_bg, (0, 0))
    draw_text("1. Играть", WIDTH // 2, 150, center=True)
    draw_text("2. Имя игрока", WIDTH // 2, 200, center=True)
    draw_text("3. Сложность", WIDTH // 2, 250, center=True)
    draw_text("4. Выход", WIDTH // 2, 300, center=True)
    pygame.display.flip()


def run_splash():
    global state
    screen.blit(splash, (0, 0))
    draw_text("Нажмите любую клавишу...", WIDTH // 2, HEIGHT - 60, center=True, color=WHITE)
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit();
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            state = "menu"


def run_name_input():
    global name, state
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit();
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                state = "menu"
            elif event.key == pygame.K_BACKSPACE:
                name = name[:-1]
            else:
                name += event.unicode

    screen.fill(WHITE)
    draw_text("Введите имя:", 50, 100)
    draw_text(name, 50, 150)
    pygame.display.flip()


def run_menu_difficulty():
    global state, difficulty
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit();
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                difficulty = 1
                state = "menu"
            elif event.key == pygame.K_2:
                difficulty = 2
                state = "menu"
            elif event.key == pygame.K_3:
                difficulty = 3
                state = "menu"
            elif event.key == pygame.K_ESCAPE:
                state = "menu"

    screen.fill(WHITE)
    draw_text("Выберите уровень сложности:", WIDTH // 2, 120, center=True)
    draw_text("1. Легко", WIDTH // 2, 180, center=True)
    draw_text("2. Средне", WIDTH // 2, 230, center=True)
    draw_text("3. Сложно", WIDTH // 2, 280, center=True)
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
    elif state == "menu_difficulty":
        run_menu_difficulty()

    clock.tick(FPS)