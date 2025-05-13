import pygame
import pygame.mixer
import sys

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Константы
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Настройки игры
FPS = 60
SHIP_WIDTH, SHIP_HEIGHT = 60, 120
LAUNCHER_WIDTH, LAUNCHER_HEIGHT = 30, 80
MISSILE_SIZE = 12
MAX_MISSILES = 5

# Инициализация экрана (должно быть перед загрузкой ресурсов)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Космический защитник")
clock = pygame.time.Clock()


# Состояния игры
class GameState:
    SPLASH = "splash"
    MENU = "menu"
    GAME = "game"
    NAME_INPUT = "name_input"
    DIFFICULTY_MENU = "menu_difficulty"
    GAME_OVER = "game_over"


# Загрузка ресурсов
def load_resources():
    try:
        # Музыка и звуки
        sounds = {}
        try:
            pygame.mixer.music.load("music.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
            sounds["shot"] = pygame.mixer.Sound("shot.mp3")
            sounds["hit"] = pygame.mixer.Sound("www.mp3")
        except:
            print("Не удалось загрузить звуки, игра продолжится без них")

        # Изображения (создаем цветные поверхности если файлов нет)
        images = {
            "menu_bg": pygame.Surface((WIDTH, HEIGHT)),
            "splash": pygame.Surface((WIDTH, HEIGHT)),
            "ship": pygame.Surface((SHIP_WIDTH, SHIP_HEIGHT)),
            "launcher": pygame.Surface((LAUNCHER_WIDTH, LAUNCHER_HEIGHT))
        }

        # Заливаем цветом
        images["menu_bg"].fill((50, 50, 100))  # Темно-синий
        images["splash"].fill((0, 100, 200))  # Голубой
        images["ship"].fill(BLUE)
        images["launcher"].fill(BLACK)

        # Пытаемся загрузить реальные изображения
        try:
            images["menu_bg"] = pygame.image.load("background.png").convert()
            images["splash"] = pygame.image.load("splash.jpg").convert()
        except:
            print("Используются стандартные фоны")

        # Шрифты
        fonts = {
            "large": pygame.font.SysFont("Arial", 48),
            "medium": pygame.font.SysFont("Arial", 36),
            "small": pygame.font.SysFont("Arial", 24)
        }

        return images, sounds, fonts

    except Exception as e:
        print(f"Ошибка загрузки ресурсов: {e}")
        pygame.quit()
        sys.exit()


# Загружаем ресурсы после создания окна
images, sounds, fonts = load_resources()

# Игровые переменные
state = GameState.SPLASH
score = 10
high_score = 0
name = ""
difficulty = 1  # 1 - легко, 2 - средне, 3 - сложно
game_over_time = 0

# Игровые объекты
ship = pygame.Rect(WIDTH - 150, HEIGHT // 2 - SHIP_HEIGHT // 2, SHIP_WIDTH, SHIP_HEIGHT)
launcher = pygame.Rect(50, HEIGHT // 2 - LAUNCHER_HEIGHT // 2, LAUNCHER_WIDTH, LAUNCHER_HEIGHT)
missiles = []
ship_alive = True
ship_direction = 1  # 1 - вниз, -1 - вверх


def reset_game():
    global ship, launcher, missiles, ship_alive, ship_direction, score
    ship = pygame.Rect(WIDTH - 150, HEIGHT // 2 - SHIP_HEIGHT // 2, SHIP_WIDTH, SHIP_HEIGHT)
    launcher = pygame.Rect(50, HEIGHT // 2 - LAUNCHER_HEIGHT // 2, LAUNCHER_WIDTH, LAUNCHER_HEIGHT)
    missiles = []
    ship_alive = True
    ship_direction = 1
    score = 10


def draw_text(text, font_type, x, y, color=BLACK, center=False):
    text_surface = fonts[font_type].render(text, True, color)
    if center:
        text_rect = text_surface.get_rect(center=(x, y))
    else:
        text_rect = text_surface.get_rect(topleft=(x, y))
    screen.blit(text_surface, text_rect)


def draw_button(text, x, y, width, height, inactive_color, active_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    rect = pygame.Rect(x, y, width, height)
    color = active_color if rect.collidepoint(mouse) else inactive_color

    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=10)
    draw_text(text, "medium", x + width // 2, y + height // 2, BLACK, True)

    if rect.collidepoint(mouse) and click[0] == 1 and action:
        return action
    return None


def run_game():
    global score, ship_alive, state, high_score, game_over_time, ship_direction

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and len(missiles) < MAX_MISSILES:
                missile = pygame.Rect(launcher.right, launcher.centery - MISSILE_SIZE // 2,
                                      MISSILE_SIZE, MISSILE_SIZE)
                missiles.append(missile)
                if "shot" in sounds:
                    sounds["shot"].play()
            elif event.key == pygame.K_ESCAPE:
                state = GameState.MENU

    # Управление
    keys = pygame.key.get_pressed()
    launcher_speed = 8 if difficulty == 3 else 6 if difficulty == 2 else 5
    launcher.y += (keys[pygame.K_s] - keys[pygame.K_w]) * launcher_speed
    launcher.clamp_ip(screen.get_rect())

    # Движение снарядов
    for missile in missiles[:]:
        missile.x += 10
        if not screen.get_rect().contains(missile):
            missiles.remove(missile)
            score = max(0, score - 1)

    # Движение корабля
    if ship_alive:
        ship_speed = difficulty + 2
        ship.y += ship_speed * ship_direction

        if ship.top <= 0:
            ship.top = 0
            ship_direction = 1
        elif ship.bottom >= HEIGHT:
            ship.bottom = HEIGHT
            ship_direction = -1

    # Столкновения
    for missile in missiles[:]:
        if ship_alive and missile.colliderect(ship):
            missiles.remove(missile)
            if "hit" in sounds:
                sounds["hit"].play()
            score += 1

    # Конец игры
    if score <= 0 and ship_alive:
        ship_alive = False
        game_over_time = pygame.time.get_ticks()
        high_score = max(high_score, score)

    # Отрисовка
    screen.fill(WHITE)

    # Снаряды
    for missile in missiles:
        pygame.draw.rect(screen, RED, missile, border_radius=3)

    # Объекты
    screen.blit(images["launcher"], launcher)
    if ship_alive:
        screen.blit(images["ship"], ship)

    # Интерфейс
    score_text = f"{name}: {score}" if name else f"Очки: {score}"
    draw_text(score_text, "small", 20, 20)

    if not ship_alive:
        current_time = pygame.time.get_ticks()
        if current_time - game_over_time > 3000:
            state = GameState.GAME_OVER
        draw_text("ИГРА ОКОНЧЕНА!", "large", WIDTH // 2, HEIGHT // 2, RED, True)

    pygame.display.flip()


def run_menu():
    global state

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                reset_game()
                state = GameState.GAME
            elif event.key == pygame.K_2:
                state = GameState.NAME_INPUT
            elif event.key == pygame.K_3:
                state = GameState.DIFFICULTY_MENU
            elif event.key == pygame.K_4:
                pygame.quit()
                sys.exit()

    screen.blit(images["menu_bg"], (0, 0))
    draw_text("КОСМИЧЕСКИЙ ЗАЩИТНИК", "large", WIDTH // 2, 80, WHITE, True)

    # Кнопки
    button_actions = [
        draw_button("1. Новая игра", WIDTH // 2 - 150, 200, 300, 50, GREEN, (100, 255, 100),
                    lambda: (reset_game(), setattr(globals()['state'], 'state', GameState.GAME))),
        draw_button("2. Ввести имя", WIDTH // 2 - 150, 270, 300, 50, GREEN, (100, 255, 100),
                    lambda: setattr(globals()['state'], 'state', GameState.NAME_INPUT)),
        draw_button("3. Сложность", WIDTH // 2 - 150, 340, 300, 50, GREEN, (100, 255, 100),
                    lambda: setattr(globals()['state'], 'state', GameState.DIFFICULTY_MENU)),
        draw_button("4. Выход", WIDTH // 2 - 150, 410, 300, 50, RED, (255, 100, 100),
                    lambda: (pygame.quit(), sys.exit()))
    ]

    if name:
        draw_text(f"Игрок: {name}", "small", WIDTH // 2, 480, WHITE, True)

    diff_text = ["Легко", "Средне", "Сложно"][difficulty - 1]
    draw_text(f"Сложность: {diff_text}", "small", WIDTH // 2, 520, WHITE, True)

    pygame.display.flip()


def run_splash():
    global state

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            state = GameState.MENU

    screen.blit(images["splash"], (0, 0))
    draw_text("Нажмите любую клавишу для продолжения...", "small",
              WIDTH // 2, HEIGHT - 50, WHITE, True)
    pygame.display.flip()


def run_name_input():
    global name, state

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                state = GameState.MENU
            elif event.key == pygame.K_ESCAPE:
                state = GameState.MENU
            elif event.key == pygame.K_BACKSPACE:
                name = name[:-1]
            else:
                if len(name) < 15:
                    name += event.unicode

    screen.fill(WHITE)
    draw_text("Введите ваше имя:", "medium", WIDTH // 2, 200, BLACK, True)

    input_rect = pygame.Rect(WIDTH // 2 - 200, 250, 400, 50)
    pygame.draw.rect(screen, BLACK, input_rect, 2)
    draw_text(name, "medium", WIDTH // 2, 275, BLACK, True)

    if draw_button("Назад", WIDTH // 2 - 100, 350, 200, 50, (200, 200, 200), (150, 150, 150)):
        state = GameState.MENU

    pygame.display.flip()


def run_difficulty_menu():
    global state, difficulty

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                difficulty = 1
                state = GameState.MENU
            elif event.key == pygame.K_2:
                difficulty = 2
                state = GameState.MENU
            elif event.key == pygame.K_3:
                difficulty = 3
                state = GameState.MENU
            elif event.key == pygame.K_ESCAPE:
                state = GameState.MENU

    screen.fill(WHITE)
    draw_text("Выберите уровень сложности:", "large", WIDTH // 2, 100, BLACK, True)

    buttons = [
        draw_button("1. Легко", WIDTH // 2 - 150, 200, 300, 60, GREEN, (100, 255, 100),
                    lambda: setattr(globals()['difficulty'], 1)),
        draw_button("2. Средне", WIDTH // 2 - 150, 280, 300, 60, YELLOW, (255, 255, 100),
                    lambda: setattr(globals()['difficulty'], 2)),
        draw_button("3. Сложно", WIDTH // 2 - 150, 360, 300, 60, RED, (255, 100, 100),
                    lambda: setattr(globals()['difficulty'], 3)),
        draw_button("Назад", WIDTH // 2 - 150, 450, 300, 60, (200, 200, 200), (150, 150, 150),
                    lambda: setattr(globals()['state'], 'state', GameState.MENU))
    ]

    pygame.display.flip()


def run_game_over():
    global state

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                reset_game()
                state = GameState.GAME
            elif event.key == pygame.K_ESCAPE:
                state = GameState.MENU

    screen.fill(WHITE)
    draw_text("ИГРА ОКОНЧЕНА", "large", WIDTH // 2, 100, RED, True)

    if name:
        draw_text(f"{name}, ваш счет: {score}", "medium", WIDTH // 2, 180, BLACK, True)
    else:
        draw_text(f"Ваш счет: {score}", "medium", WIDTH // 2, 180, BLACK, True)

    draw_text(f"Лучший счет: {high_score}", "medium", WIDTH // 2, 240, BLACK, True)

    buttons = [
        draw_button("Играть снова", WIDTH // 2 - 200, 320, 400, 60, GREEN, (100, 255, 100),
                    lambda: (reset_game(), setattr(globals()['state'], 'state', GameState.GAME))),
        draw_button("В меню", WIDTH // 2 - 200, 400, 400, 60, (200, 200, 200), (150, 150, 150),
                    lambda: setattr(globals()['state'], 'state', GameState.MENU))
    ]

    pygame.display.flip()


# Главный цикл
while True:
    if state == GameState.SPLASH:
        run_splash()
    elif state == GameState.MENU:
        run_menu()
    elif state == GameState.GAME:
        run_game()
    elif state == GameState.NAME_INPUT:
        run_name_input()
    elif state == GameState.DIFFICULTY_MENU:
        run_difficulty_menu()
    elif state == GameState.GAME_OVER:
        run_game_over()

    clock.tick(FPS)