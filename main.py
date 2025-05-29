import cv2
import mediapipe as mp
import serial
import time
import json

# Configurar a porta serial (ajuste para a porta correta do seu Arduino)
arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)  # Aguarda inicialização da conexão serial

# Inicializa o MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

def detectar_dedos_melhor(hand_landmarks, hand_label):
    dedos = []

    # Polegar: depende da mão (Right ou Left)
    if hand_label == "Right":
        # Polegar levantado se TIP estiver à esquerda do IP (para mão direita)
        dedos.append(1 if hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x <
                         hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].x else 0)
    else:
        # Mão esquerda: polegar levantado se TIP estiver à direita do IP
        dedos.append(1 if hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x >
                         hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].x else 0)

    # Dedos restantes (comparar TIP acima do PIP no eixo Y)
    dedos.append(1 if hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y <
                     hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP].y else 0)
    dedos.append(1 if hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y <
                     hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y else 0)
    dedos.append(1 if hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y <
                     hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP].y else 0)
    dedos.append(1 if hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y <
                     hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP].y else 0)

    return dedos

def classificar_gesto_melhor(dedos):
    padrao_gestos = {
        "SOCORRO": [1, 1, 1, 1, 1],
        "AJUDA_TECNICA": [0, 1, 1, 0, 0],
        "ATENCAO": [0, 1, 0, 0, 0],
        "OK": [1, 1, 0, 0, 0],
        "RECURSOS": [1, 0, 0, 0, 0]
    }

    for gesto, padrao in padrao_gestos.items():
        if padrao == dedos:
            return gesto
    return "INDEFINIDO"

# Abrir a webcam (ou troque para vídeo: video_path = "video.mp4" e cap = cv2.VideoCapture(video_path))
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Fim do vídeo ou erro ao carregar.")
        break

    frame = cv2.resize(frame, (500, 500))
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks and result.multi_handedness:
        for hand_landmarks, hand_handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
            label = hand_handedness.classification[0].label  # "Right" ou "Left"
            dedos = detectar_dedos_melhor(hand_landmarks, label)
            gesto = classificar_gesto_melhor(dedos)

            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Mostrar o gesto detectado na imagem
            cv2.putText(frame, f"Gesto: {gesto}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 0), 2)
            
            cv2.putText(frame, f"Dedos: {dedos}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 255, 255), 2)

            # Enviar JSON para Arduino
            data = {"gesto": gesto}
            pacote = json.dumps(data) + "\n"
            arduino.write(pacote.encode('utf-8'))
            print("Enviado:", pacote.strip())

    cv2.imshow("Video", frame)
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
arduino.close()