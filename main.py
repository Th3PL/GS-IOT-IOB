import cv2
import mediapipe as mp

# Inicializar MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

# Função para detectar se um dedo está levantado
def dedos_levantados(hand_landmarks):
    dedos = []

    # Dedo polegar
    if hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x < hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].x:
        dedos.append(1)
    else:
        dedos.append(0)

    # Dedo indicador
    if hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP].y:
        dedos.append(1)
    else:
        dedos.append(0)

    # Dedo médio
    if hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y:
        dedos.append(1)
    else:
        dedos.append(0)

    # Dedo anelar
    if hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP].y:
        dedos.append(1)
    else:
        dedos.append(0)

    # Dedo mínimo
    if hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP].y:
        dedos.append(1)
    else:
        dedos.append(0)

    return dedos

# Função para classificar os gestos
def classificar_gesto(dedos):
    if dedos == [1, 1, 1, 1, 1]:
        return "✋ SOCORRO"
    elif dedos == [0, 0, 0, 0, 0]:
        return "✊ OK / AGUARDANDO"
    elif dedos == [0, 1, 1, 0, 0]:
        return "✌️ PRECISO DE AJUDA TÉCNICA"
    elif dedos == [0, 1, 0, 0, 0]:
        return "☝️ CHAMAR ATENÇÃO"
    else:
        return "Gesto não reconhecido"

# Captura de vídeo
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip na imagem (espelho)
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(frame_rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            dedos = dedos_levantados(hand_landmarks)
            gesto = classificar_gesto(dedos)

            # Exibir o gesto detectado na tela
            cv2.putText(frame, gesto, (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                        1.2, (0, 0, 255), 3, cv2.LINE_AA)

    cv2.imshow('Detector de Gestos', frame)

    if cv2.waitKey(1) & 0xFF == 27:  # Tecla ESC para sair
        break

cap.release()
cv2.destroyAllWindows()