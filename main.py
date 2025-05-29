import cv2
import mediapipe as mp
import serial
import time
import json
import math

try:
    arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    time.sleep(2)
except:
    print("⚠️ Não foi possível conectar ao Arduino.")

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2, 
    min_detection_confidence=0.5,  
    min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils

def dedos_levantados(hand_landmarks, hand_label):
    dedos = []
    if hand_label == "Right":
        dedos.append(1 if hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x <
                         hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].x else 0)
    else:
        dedos.append(1 if hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x >
                         hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].x else 0)
    dedos.append(1 if hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y <
                     hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP].y else 0)
    dedos.append(1 if hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y <
                     hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y else 0)
    dedos.append(1 if hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y <
                     hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP].y else 0)
    dedos.append(1 if hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y <
                     hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP].y else 0)
    return dedos

def distancia_entre_pontos(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

def calcular_escala_mao(landmarks):
    p1 = landmarks.landmark[mp_hands.HandLandmark.WRIST]
    p2 = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
    return distancia_entre_pontos(p1, p2)

def classificar_gesto(landmarks, dedos, hand_label):
    dist_polegar_indice = distancia_entre_pontos(
        landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP],
        landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    )
    escala = calcular_escala_mao(landmarks)
    limite_ok = 0.25 * escala

    if dedos == [1,1,1,1,1]:
        return "SOCORRO"
    elif dedos == [0,1,0,0,0]:
        return "ATENCAO"
    elif dedos == [0,1,1,0,0]:
        return "AJUDA_TECNICA"
    elif dedos == [0,1,1,1,1]:
        return "SOLICITACAO"
    elif dedos == [1,0,0,0,0]:
        return "RECURSOS"
    elif dist_polegar_indice < limite_ok:
        return "OK"
    else:
        return "INDEFINIDO"

prev_envio = 0
intervalo_envio = 0.2  # segundos

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultado = hands.process(rgb)

    gesto_detectado = "INDEFINIDO"

    if resultado.multi_hand_landmarks:
        for hand_landmarks, hand_handedness in zip(resultado.multi_hand_landmarks, resultado.multi_handedness):
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            label = hand_handedness.classification[0].label

            dedos = dedos_levantados(hand_landmarks, label)
            gesto = classificar_gesto(hand_landmarks, dedos, label)

            if gesto != "INDEFINIDO":
                gesto_detectado = gesto

    # Enviar comando ao Arduino apenas se passou o intervalo
    agora = time.time()
    if agora - prev_envio > intervalo_envio:
        try:
            dados_json = json.dumps({"gesto": gesto_detectado}) + "\n"
            arduino.write(dados_json.encode())
            prev_envio = agora
        except:
            pass

    cv2.putText(frame, gesto_detectado, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,
                1.5, (0, 255, 0), 3)

    cv2.imshow("Reconhecimento de Gestos", frame)

    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()