import pygame
import pygame.mixer

pygame.init()
pygame.mixer.init()

pygame.mixer.music.load("www.mp3")
shot_sound = pygame.mixer.Sound("shot.mp3")

FPS = 120

clock = pygame.time.Clock()

screen = pygame.display.set_mode((640, 480))

screen_rect = screen.get_rect()

MAIN_BACKGROUND_COLOR = (255, 255, 255)
MISSILE_COLOR = (255, 0, 0)
SHIP_COLOR = (0, 0, 255)
LAUNCHER_COLOR = (0, 0, 0)
GAME_OVER_COLOR = (0, 0, 0)

background_color = MAIN_BACKGROUND_COLOR

ship = pygame.Rect(300, 200, 50, 100)
ship.right = screen_rect.right
ship.centery = screen_rect.centery

launcher = pygame.Rect(50, screen_rect.centery - 25, 20, 50)

missiles = []

ship_speed_y = 1
launcher_speed_y = 0

ship_alive = True

score = 10

font = pygame.font.SysFont(None, 36)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                missile = pygame.Rect(launcher.right, launcher.centery - 5, 10, 10)
                missile_speed_x = 3
                missile_speed_y = 0
                missiles.append((missile, missile_speed_x, missile_speed_y))

                shot_sound.play()

            elif event.key == pygame.K_w:
                launcher_speed_y = -2

            elif event.key == pygame.K_s:
                launcher_speed_y = 2

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w or event.key == pygame.K_s:
                launcher_speed_y = 0

    for missile, missile_speed_x, missile_speed_y in missiles:
        missile.move_ip(missile_speed_x, missile_speed_y)

        if not missile.colliderect(screen_rect):
            missiles.remove((missile, missile_speed_x, missile_speed_y))
            score -= 1


    for i, (missile, missile_speed_x, missile_speed_y) in enumerate(missiles):
        if ship_alive and missile.colliderect(ship):
            missiles.pop(i)
            pygame.mixer.music.play()
            score += 1
            print(f"Попадание! Очки: {score}")

    if score <= 0:
        background_color = GAME_OVER_COLOR
        print("Игра окончена!")
        running = False

    if ship_alive:
        ship.move_ip(0, ship_speed_y)

    if ship.bottom > screen_rect.bottom or ship.top < screen_rect.top:
        ship_speed_y = -ship_speed_y

    launcher.move_ip(0, launcher_speed_y)

    if launcher.top < screen_rect.top:
        launcher.top = screen_rect.top
    if launcher.bottom > screen_rect.bottom:
        launcher.bottom = screen_rect.bottom

    screen.fill(background_color)

    if ship_alive:
        pygame.draw.rect(screen, SHIP_COLOR, ship)

    pygame.draw.rect(screen, LAUNCHER_COLOR, launcher)

    for missile, _, _ in missiles:
        pygame.draw.rect(screen, MISSILE_COLOR, missile)

    score_text = font.render(f"Очки: {score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))

    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()