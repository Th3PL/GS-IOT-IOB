import cv2
import mediapipe as mp
import serial
import time
import json
import math

# === Configurar a porta serial ===
try:
    arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.5)
    time.sleep(2)  # Aguarda inicialização do Arduino
    print("✅ Conectado ao Arduino.")
except Exception as e:
    print(f"⚠️ Não foi possível conectar ao Arduino: {e}")
    arduino = None

# === Inicializar Mediapipe ===
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# === Funções Auxiliares ===
def dedos_levantados(hand_landmarks, hand_label):
    dedos = []

    # Polegar
    if hand_label == "Right":
        dedos.append(1 if hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x <
                         hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].x else 0)
    else:
        dedos.append(1 if hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x >
                         hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].x else 0)

    # Outros dedos
    dedos.extend([
        1 if hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y <
             hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP].y else 0,
        1 if hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y <
             hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y else 0,
        1 if hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y <
             hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP].y else 0,
        1 if hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y <
             hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP].y else 0
    ])

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

    if dedos == [1, 1, 1, 1, 1]:
        return "SOCORRO"
    elif dedos == [0, 1, 0, 0, 0]:
        return "ATENCAO"
    elif dedos == [0, 1, 1, 0, 0]:
        return "AJUDA_TECNICA"
    elif dedos == [0, 1, 1, 1, 1]:
        return "SOLICITACAO"
    elif dedos == [1, 0, 0, 0, 0]:
        return "RECURSOS"
    elif dist_polegar_indice < limite_ok:
        return "OK"
    else:
        return "INDEFINIDO"


def putTextWithBackground(img, text, pos, font, scale, color, thickness):
    cv2.putText(img, text, (pos[0]+1, pos[1]+1), font, scale, (0,0,0), thickness+2, cv2.LINE_AA)
    cv2.putText(img, text, pos, font, scale, color, thickness, cv2.LINE_AA)


# === Webcam ===
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Largura
cap.set(4, 480)  # Altura

cv2.namedWindow("Video", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Video", 640, 480)
cv2.moveWindow("Video", 100, 100)

prev_time = 0

with mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as hands:

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("❌ Erro ao capturar imagem da webcam")
            break

        frame = cv2.flip(frame, 1)

        current_time = time.time()
        fps = 1 / (current_time - prev_time) if prev_time != 0 else 0
        prev_time = current_time

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)

        gesto_final = "INDEFINIDO"

        if result.multi_hand_landmarks and result.multi_handedness:
            gestos_maos = []
            for landmarks, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
                label = handedness.classification[0].label
                score = handedness.classification[0].score

                if score < 0.5:
                    continue

                dedos = dedos_levantados(landmarks, label)
                gesto = classificar_gesto(landmarks, dedos, label)
                gestos_maos.append(gesto)

                mp_draw.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

                y_offset = 30 if label == "Right" else 60
                putTextWithBackground(frame, f"Label: {label}", (10, y_offset),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                putTextWithBackground(frame, f"Gesto: {gesto}", (10, y_offset + 30),
                                      cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                putTextWithBackground(frame, f"Dedos: {dedos}", (10, y_offset + 60),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            if len(gestos_maos) == 2 and gestos_maos[0] == "SOCORRO" and gestos_maos[1] == "SOCORRO":
                gesto_final = "ALERTA_MAXIMO"
            elif len(gestos_maos) >= 1:
                gesto_final = gestos_maos[0]

        else:
            putTextWithBackground(frame, "Nenhuma mao detectada", (10, 440),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        putTextWithBackground(frame, f"Gesto Final: {gesto_final}", (10, 470),
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        putTextWithBackground(frame, f'FPS: {int(fps)}', (530, 20),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        # === Envio para Arduino ===
        if arduino is not None:
            data = {"gesto": gesto_final}
            pacote = json.dumps(data) + "\n"
            try:
                arduino.write(pacote.encode('utf-8'))
                arduino.flush()  # Limpa buffer de saída para enviar na hora
                print("📤 Enviado:", pacote.strip())
            except Exception as e:
                print(f"⚠️ Erro ao enviar dados: {e}")

        cv2.imshow("Video", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# === Finalizar ===
cap.release()
cv2.destroyAllWindows()
if arduino is not None:
    arduino.close()