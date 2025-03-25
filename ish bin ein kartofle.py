import cv2
import serial
import mediapipe as mp
import time

# Commandes de mouvement
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

# Initialiser MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

# Ouvrir le flux vidéo
capture = cv2.VideoCapture(1) #changement de flux vidéo

frame_width = int(capture.get(3))
frame_height = int(capture.get(4))
center_x = frame_width // 2
center_y = frame_height // 2

def track_person(person_x, person_y):
    threshold = 50  # Seuil de tolérance du centre

    # Mouvement horizontal
    if person_x < center_x - threshold:
        write_ser(commande_gauche)
    elif person_x > center_x + threshold:
        write_ser(commande_droite)
    else:
        write_ser(commande_stop_horizontal)

    # Mouvement vertical
    if person_y < center_y - threshold:
        write_ser(commande_haut)
    elif person_y > center_y + threshold:
        write_ser(commande_bas)
    else:
        write_ser(commande_stop_vert)

while capture.isOpened():
    ret, frame = capture.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    if results.pose_landmarks:
        mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # Utiliser le nez (landmark 0) ou le centre du torse (landmarks 11 et 12)
        nose = results.pose_landmarks.landmark[0]
        shoulder_left = results.pose_landmarks.landmark[11]
        shoulder_right = results.pose_landmarks.landmark[12]

        # Calcul du centre du corps
        person_x = int((shoulder_left.x + shoulder_right.x) / 2 * frame_width)
        person_y = int((shoulder_left.y + shoulder_right.y) / 2 * frame_height)

        track_person(person_x, person_y)
    else:
        write_ser(commande_stop_horizontal)
        write_ser(commande_stop_vert)

    cv2.imshow("Human Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()
