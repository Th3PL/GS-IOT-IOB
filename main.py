import cv2
import mediapipe as mp

# Inicialização do MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2,  # Número máximo de mãos
    min_detection_confidence=0.7,  # Confiança para detecção
    min_tracking_confidence=0.6    # Confiança para rastreamento
)

# Desenho dos landmarks na imagem
mp_drawing = mp.solutions.drawing_utils

# Abertura da webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Inverter a imagem horizontalmente (espelho)
    frame = cv2.flip(frame, 1)

    # Conversão de BGR (OpenCV) para RGB (MediaPipe)
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Melhora a performance
    image.flags.writeable = False

    # Processa a imagem
    results = hands.process(image)

    # Volta para BGR para exibir
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Desenha os pontos das mãos
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                image, 
                hand_landmarks, 
                mp_hands.HAND_CONNECTIONS
            )

    # Mostra na janela
    cv2.imshow('Detector de Maos', image)

    # Pressiona 'q' para sair
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera recursos
cap.release()
cv2.destroyAllWindows()