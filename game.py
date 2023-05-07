import pygame
import random
import cv2
import mediapipe as mp
import threading


menu_choice = None

# Some colour
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

hand_data = {'hand_closed': False, 'finger_tip': (0, 0), 'wrist': (0, 0)}
# Init pygame
pygame.init()
numberloop = 0
pr_numberloop = -1

# Windows size
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Задаем заголовок окна
pygame.display.set_caption("game by hand in OHIO")

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
    hands = mp.solutions.hands.Hands(max_num_hands=2) #Object for Ai hand detecting
    draw = mp.solutions.drawing_utils #for drawing hand
    cv2.namedWindow("Hand", cv2.WINDOW_NORMAL)

    while True:
        success, image = cap.read() #looking on camera
        image = cv2.flip(image, 1) #camera now mirror
        imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) #converting it rgb
        results = hands.process(imageRGB) #work mediapipe

        hand_data = {"hand_closed": False, "finger_tip": None, "wrist": None}

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                for id, lm in enumerate(handLms.landmark):
                    h, w, c = image.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    # Recalculating coordinates using proportions
                    cx = int(cx * 800 / w)
                    cy = int(cy * 600 / h)

                    if id == mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP:
                        hand_data["finger_tip"] = (cx, cy)
                    elif id == mp.solutions.hands.HandLandmark.WRIST:
                        hand_data["wrist"] = (cx, cy)

                # Вычисляем расстояние между кончиком пальца и запястьем
                if hand_data["finger_tip"] is not None and hand_data["wrist"] is not None:
                    distance = ((hand_data["finger_tip"][0] - hand_data["wrist"][0]) ** 2 + (hand_data["finger_tip"][1] - hand_data["wrist"][1]) ** 2) ** 0.5

                    # If the distance is less than a certain threshold, then we assume that the hand is clenched into a fist
                    if distance < 100:
                        hand_data["hand_closed"] = True

                draw.draw_landmarks(image, handLms, mp.solutions.hands.HAND_CONNECTIONS) #drawing hand

        cv2.resizeWindow("Hand", 800, 600)
        cv2.imshow("Hand", image) #mirroring

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()



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

        # We reflect the ball off the walls
        if self.x < self.radius or self.x > SCREEN_WIDTH - self.radius:
            self.speed_x = -self.speed_x
        if self.y < self.radius or self.y > SCREEN_HEIGHT - self.radius:
            self.speed_y = -self.speed_y

    def draw(self):
        pygame.draw.circle(screen, GREEN, (self.x, self.y), self.radius)


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


ball = Ball()
ring = Ring()

targets = []
score2 = 0
missed = 0
font = pygame.font.SysFont("Arial", 30)
biggestfon = pygame.font.SysFont("Arial", 80)

class Target:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.size)

def update(targets):
    for target in targets:
        target.y += 5
        if target.y > SCREEN_HEIGHT:
            targets.remove(target)
            targets.append(new_target())
            global missed
            missed += 1
# Defining a function to create a new goal
def new_target():
    size = random.randint(40, 75)
    x = random.randint(size, SCREEN_WIDTH - size)
    y = 0
    return Target(x, y, size)

# Creating the first goals
for i in range(5):
    targets.append(new_target())

# Define the "Exit" button
exit_button = pygame.Rect(10, SCREEN_HEIGHT-50, 100, 40)
exit_text = font.render("Menu", True, RED)

fromsitetomenu = pygame.Rect(300, 400, 250, 100)
fromsitetomenu_text = biggestfon.render("Exit", True, RED)

#Defining a variable for scoring points
score1 = 0

menu_choice = 0
previus_choice = 0

need_pause = False

# launching game
count = 0
thread = threading.Thread(target=detect_hand)
thread.daemon = True
thread.start()
running = True
while running:
    screen.fill(BLACK)
    numberloop += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if menu_choice == 1:
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

        # moving ball
        ball.move()

        # Drawing the ball and the ring
        screen.fill(BLACK)
        ball.draw()
        ring.draw()
        pygame.draw.rect(screen, WHITE, restart_button)
        text = font.render("Menu", True, BLACK)
        screen.blit(text, (10, 500))

        # Check if the ball has hit the ring
        if abs(ball.x - ring.x) < ring.width // 2 + ball.radius and abs(ball.y - ring.y) < ring.height // 2 + ball.radius:
            score1 += 1
            ball = Ball()


        # Drawing the invoice
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
        text = font.render("Catch the ball", True, WHITE)
        screen.blit(text, (300, 50))
        font = pygame.font.Font(None, 36)
        text = font.render("My Site", True, WHITE)
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
                menu_choice = 3
            if button1.collidepoint(hand_data["wrist"]) and hand_data["hand_closed"]:
                menu_choice = 1
            if button2.collidepoint(hand_data["wrist"]) and hand_data["hand_closed"]:
                menu_choice = 2
        except:
            pass


    if menu_choice == 2:
        if hand_data["hand_closed"]:
            for target in targets:
                distance = ((target.x - hand_data["wrist"][0]) ** 2 +
                            (target.y - hand_data["wrist"][1]) ** 2) ** 0.5
                if distance <= target.size:
                    targets.remove(target)
                    targets.append(new_target())
                    score2 += 1

        for target in targets:
            target.draw(screen)

        update(targets)

        score_text = font.render(f"Score: {score2}, Miss: {missed / 4}", True, BLUE)
        screen.blit(score_text, (10, 10))

        screen.blit(exit_text, exit_button)
        pygame.draw.rect(screen, RED, exit_button, 2)

        try:
            if exit_button.collidepoint(hand_data["wrist"]) and hand_data["hand_closed"]:
                menu_choice = 0
        except:
            pass


    if menu_choice == 3:
        image = pygame.image.load("qr.png")
        screen.blit(image, (300, 100))

        screen.blit(fromsitetomenu_text, fromsitetomenu)
        pygame.draw.rect(screen, RED, fromsitetomenu, 2)

        try:
            if fromsitetomenu.collidepoint(hand_data["wrist"]) and hand_data["hand_closed"]:
                menu_choice = 0
        except:
            pass


    else:
        count = 0

    try:
        if hand_data["hand_closed"]:
            pygame.draw.rect(screen, (255, 0, 255), (hand_data["wrist"][0], hand_data["wrist"][1], 20, 20))
        else:
            pygame.draw.rect(screen, (0, 255, 255), (hand_data["wrist"][0], hand_data["wrist"][1], 20, 20))
    except:
        pass


    # screen updating
    pygame.display.flip()

    # Limiting the frame rate
    pygame.time.Clock().tick(60)

# exit
pygame.quit()
