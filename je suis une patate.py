import cv2
import serial
import mediapipe as mp
import time

commande_haut = "b"
commande_bas = "h"
commande_gauche = "d"
commande_droite = "g"
commande_stop_vert = "v"
commande_stop_horizontal = "r"

MAX_BUFF_LEN = 255
SETUP = False
port = None
prev = time.time()

last_command_horiz = None
last_command_vert = None

while not SETUP:
    try:
        port = serial.Serial('COM9', 115200, timeout=1)
    except:
        if time.time() - prev > 2:
            print("No serial detected, please plug your uController")
            prev = time.time()
    if port is not None:
        SETUP = True
        print("connected")

# Fonction pour envoyer des commandes série
def write_ser(cmd):
    global last_command_horiz, last_command_vert
    if cmd in [commande_gauche, commande_droite, commande_stop_horizontal]:
        if cmd != last_command_horiz:
            port.write((cmd + '\n').encode())
            last_command_horiz = cmd
    elif cmd in [commande_haut, commande_bas, commande_stop_vert]:
        if cmd != last_command_vert:
            port.write((cmd + '\n').encode())
            last_command_vert = cmd

# Initialiser MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

# Ouvrir le flux vidéo
capture = cv2.VideoCapture(0)

frame_width = int(capture.get(3))
frame_height = int(capture.get(4))
center_x = frame_width // 2
center_y = frame_height // 2

def track_hand(hand_x, hand_y):
    threshold = 50  # Seuil pour la tolérance du centre
    
    if hand_x < center_x - threshold:
        write_ser(commande_gauche)
    elif hand_x > center_x + threshold:
        write_ser(commande_droite)
    else:
        write_ser(commande_stop_horizontal)
    
    if hand_y < center_y - threshold:
        write_ser(commande_haut)
    elif hand_y > center_y + threshold:
        write_ser(commande_bas)
    else:
        write_ser(commande_stop_vert)

while capture.isOpened():
    ret, frame = capture.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        hand_detected = False
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            label = handedness.classification[0].label  # "Left" ou "Right"
            if label == "Right":
                hand_detected = True
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                hand_x = int(hand_landmarks.landmark[9].x * frame_width)
                hand_y = int(hand_landmarks.landmark[9].y * frame_height)
                track_hand(hand_x, hand_y)
        
        if not hand_detected:
            write_ser(commande_stop_horizontal)
            write_ser(commande_stop_vert)
    else:
        write_ser(commande_stop_horizontal)
        write_ser(commande_stop_vert)

    cv2.imshow("Hand Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()
