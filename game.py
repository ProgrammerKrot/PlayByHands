import pygame
import random
import cv2
import mediapipe as mp
import threading


menu_choice = None

# Определяем цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

hand_data = {'hand_closed': False, 'finger_tip': (0, 0), 'wrist': (0, 0)}
# Инициализируем Pygame
pygame.init()
numberloop = 0
pr_numberloop = -1

# Задаем размеры окна
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Создаем окно
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Задаем заголовок окна
pygame.display.set_caption("Кольцо")

#button for menu 0
# creating 3 buttons
button1 = pygame.Rect(50, 50, 200, 100)
button2 = pygame.Rect(300, 50, 200, 100)
button3 = pygame.Rect(550, 50, 200, 100)


def restart_game():
    global score1
    score1 = 0
    ball.__init__()
    ring.__init__()

restart_button = pygame.Rect(10, 500, 150, 75)

def detect_hand():
    global hand_data

    cap = cv2.VideoCapture(0) #Камера
    hands = mp.solutions.hands.Hands(max_num_hands=2) #Объект ИИ для определения ладони
    draw = mp.solutions.drawing_utils #Для рисование ладони
    cv2.namedWindow("Hand", cv2.WINDOW_NORMAL)

    while True:
        success, image = cap.read() #Считываем изображение с камеры
        image = cv2.flip(image, 1) #Отражаем изображение для корекктной картинки
        imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) #Конвертируем в rgb
        results = hands.process(imageRGB) #Работа mediapipe

        hand_data = {"hand_closed": False, "finger_tip": None, "wrist": None}

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                for id, lm in enumerate(handLms.landmark):
                    h, w, c = image.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    # Пересчитываем координаты с использованием пропорций
                    cx = int(cx * 800 / w)
                    cy = int(cy * 600 / h)

                    if id == mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP:
                        hand_data["finger_tip"] = (cx, cy)
                    elif id == mp.solutions.hands.HandLandmark.WRIST:
                        hand_data["wrist"] = (cx, cy)

                # Вычисляем расстояние между кончиком пальца и запястьем
                if hand_data["finger_tip"] is not None and hand_data["wrist"] is not None:
                    distance = ((hand_data["finger_tip"][0] - hand_data["wrist"][0]) ** 2 + (hand_data["finger_tip"][1] - hand_data["wrist"][1]) ** 2) ** 0.5

                    # Если расстояние меньше определенного порога, то считаем, что рука сжата в кулак
                    if distance < 100:
                        hand_data["hand_closed"] = True

                draw.draw_landmarks(image, handLms, mp.solutions.hands.HAND_CONNECTIONS) #Рисуем ладонь

        cv2.resizeWindow("Hand", 800, 600)
        cv2.imshow("Hand", image) #Отображаем картинку

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()





# Создаем класс для мяча
class Ball:
    def __init__(self):
        self.radius = 20
        self.x = random.randint(self.radius, SCREEN_WIDTH - self.radius)
        self.y = random.randint(self.radius, SCREEN_HEIGHT - self.radius)
        self.speed_x = random.randint(3, 6)
        self.speed_y = random.randint(3, 6)

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

        # Отражаем мяч от стенок
        if self.x < self.radius or self.x > SCREEN_WIDTH - self.radius:
            self.speed_x = -self.speed_x
        if self.y < self.radius or self.y > SCREEN_HEIGHT - self.radius:
            self.speed_y = -self.speed_y

    def draw(self):
        pygame.draw.circle(screen, GREEN, (self.x, self.y), self.radius)


# Создаем класс для кольца
class Ring:
    def __init__(self):
        self.width = 20
        self.height = 100
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2

    def draw(self):
        pygame.draw.rect(screen, WHITE, (self.x - self.width // 2, self.y - self.height // 2, self.width, self.height))

    def move(self, pos):
        self.y = pos[1]


# Создаем мяч и кольцо
ball = Ball()
ring = Ring()

targets = []
score2 = 0
missed = 0
font = pygame.font.SysFont("Arial", 30)

class Target:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.size)

# Определяем функцию для создания новой цели
def new_target():
    size = random.randint(30, 60)
    x = random.randint(size, SCREEN_WIDTH - size)
    y = random.randint(size, SCREEN_HEIGHT - size)
    return Target(x, y, size)

# Создаем первые цели
for i in range(5):
    targets.append(new_target())


# Определяем переменную для счета очков
score1 = 0

menu_choice = 0
previus_choice = 0

need_pause = False

# Запускаем игру
count = 0
thread = threading.Thread(target=detect_hand)
thread.daemon = True
thread.start()
running = True
while running:
    screen.fill(BLACK)
    numberloop += 1
    # Обрабатываем события
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if menu_choice == 1:
        # Двигаем кольцо за мышкой
        try:
            if hand_data["hand_closed"] and restart_button.collidepoint(hand_data["wrist"]):
                menu_choice = 0
                previus_choice = 1
                restart_game()
            pos = (0, int(hand_data["wrist"][1]))
            ring.move(pos)
        except:
            print("errror")

        print(hand_data)

        # Двигаем мяч
        ball.move()

        # Отрисовываем мяч и кольцо
        screen.fill(BLACK)
        ball.draw()
        ring.draw()
        pygame.draw.rect(screen, WHITE, restart_button)
        text = font.render("Menu", True, BLACK)
        screen.blit(text, (10, 500))

        # Проверяем, попал ли мяч в кольцо
        if abs(ball.x - ring.x) < ring.width // 2 + ball.radius and abs(ball.y - ring.y) < ring.height // 2 + ball.radius:
            score1 += 1
            ball = Ball()


        # Отрисовываем счет
        font = pygame.font.Font(None, 36)
        text = font.render("Score: " + str(score1), True, WHITE)
        screen.blit(text, (10, 10))

    if menu_choice == 0:
        pygame.draw.rect(screen, (255, 0, 0), button1)
        pygame.draw.rect(screen, (0, 255, 0), button2)
        pygame.draw.rect(screen, (0, 0, 255), button3)

        font = pygame.font.Font(None, 36)
        text = font.render("Please, choose the game", True, WHITE)
        screen.blit(text, (400, 399))
        font = pygame.font.Font(None, 36)
        text = font.render("Baskcet", True, WHITE)
        screen.blit(text, (50, 50))
        font = pygame.font.Font(None, 36)
        text = font.render("Casino", True, WHITE)
        screen.blit(text, (300, 50))
        font = pygame.font.Font(None, 36)
        text = font.render("Continue", True, WHITE)
        screen.blit(text, (550, 50))
        count += 1



        if count % 60 == 0 and not need_pause:
            need_pause = True
            pr_numberloop = numberloop


        if need_pause:
            font = pygame.font.Font(None, 36)
            text = font.render("PAUSE", True, WHITE)
            screen.blit(text, (100, 400))
            if count % 60 == 0 and numberloop != pr_numberloop:
                need_pause = False

        try:
            if button3.collidepoint(hand_data["wrist"]) and hand_data["hand_closed"]:
                menu_choice = previus_choice
            if button1.collidepoint(hand_data["wrist"]) and hand_data["hand_closed"]:
                menu_choice = 1
            if button2.collidepoint(hand_data["wrist"]) and hand_data["hand_closed"]:
                menu_choice = 2
        except:
            pass


    if menu_choice == 2:
        if hand_data["hand_closed"]:
            for target in targets:
                distance = ((target.x - hand_data["wrist"][0]) ** 2 + (
                            target.y - hand_data["wrist"][1]) ** 2) ** 0.5
                if distance <= target.size:
                    targets.remove(target)
                    targets.append(new_target())
                    score2 += 1

        for target in targets:
            target.draw(screen)

        score_text = font.render(f"Score: {score2}, Miss: {missed / 4}", True, BLUE)
        screen.blit(score_text, (10, 10))


    else:
        count = 0

    try:
        if hand_data["hand_closed"]:
            pygame.draw.rect(screen, (255, 0, 255), (hand_data["wrist"][0], hand_data["wrist"][1], 20, 20))
        else:
            pygame.draw.rect(screen, (0, 255, 255), (hand_data["wrist"][0], hand_data["wrist"][1], 20, 20))
    except:
        pass


    # Обновляем экран
    pygame.display.flip()

    # Ограничиваем частоту кадров
    pygame.time.Clock().tick(60)

# Выходим из Pygame
pygame.quit()