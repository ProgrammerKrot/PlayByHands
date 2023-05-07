import pygame
import random

# Инициализируем Pygame
pygame.init()

# Определяем цвета
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Определяем размер экрана
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Устанавливаем заголовок окна
pygame.display.set_caption("Лови цели мышкой")

# Определяем переменные
targets = []
score = 0
missed = 0
font = pygame.font.SysFont("Arial", 30)

# Определяем класс для цели
class Target:
    def __init__(self, size):
        self.size = size
        self.x = random.randint(self.size, SCREEN_WIDTH - self.size)
        self.y = 0

    def draw(self, screen):
        pygame.draw.circle(screen, RED, (self.x, self.y), self.size)

    def update(self):
        self.y += 5

# Создаем первые цели
for i in range(5):
    targets.append(Target(random.randint(30, 60)))

# Запускаем игровой цикл
running = True
clock = pygame.time.Clock()
while running:

    # Обрабатываем события
    for event in pygame.event.get():

        # Закрываем окно при нажатии на крестик
        if event.type == pygame.QUIT:
            running = False

        # Обрабатываем клик мыши
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for target in targets:
                distance = ((target.x - pos[0]) ** 2 + (target.y - pos[1]) ** 2) ** 0.5
                if distance <= target.size:
                    targets.remove(target)
                    targets.append(Target(random.randint(30, 60)))
                    score += 1

    # Очищаем экран
    screen.fill(WHITE)

    # Обновляем положение целей
    for target in targets:
        target.update()

    # Удаляем цели, которые ушли за экран
    targets = [target for target in targets if target.y < SCREEN_HEIGHT]

    # Создаем новые цели
    while len(targets) < 5:
        targets.append(Target(random.randint(30, 60)))
        missed += 1

    # Рисуем цели на экране
    for target in targets:
        target.draw(screen)

    # Рисуем счет на экране
    score_text = font.render(f"Score: {score}, Missed: {missed}", True, BLUE)
    screen.blit(score_text, (10, 10))

    # Обновляем экран
    pygame.display.flip()

    # Ограничиваем частоту обновления экрана
    clock.tick(60)

# Выходим из Pygame
pygame.quit()