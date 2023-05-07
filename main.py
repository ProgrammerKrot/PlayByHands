import cv2
import mediapipe as mp
import pygame
import threading



hand_data = None

width = 800  # ширина игрового окна
height = 600 # высота игрового окна

pygame.init()

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("My Game")
background = pygame.image.load("backgroundtest.png") #background

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


thread = threading.Thread(target=detect_hand)
thread.daemon = True
thread.start()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    print(hand_data)
    try:
        if hand_data["hand_closed"]:
            pygame.draw.rect(screen, (255, 0, 255), (hand_data["wrist"][0], hand_data["wrist"][1], 20, 20))
        else:
            pygame.draw.rect(screen, (0, 255, 255), (hand_data["wrist"][0], hand_data["wrist"][1], 20, 20))
    except:
        pass

    pygame.display.flip()


#{'hand_closed': False, 'finger_tip': (360, 341), 'wrist': (264, 451)}