# ✋ EchoHands – Sistema de Sinalização por Gestos

## 🚩 Objetivo

O **EchoHands** é uma solução desenvolvida para o desafio da **Global Solution - FIAP 2025**, com o objetivo de oferecer um meio alternativo de comunicação durante **falhas de energia elétrica**, especialmente em situações de emergência onde sistemas convencionais de comunicação estão indisponíveis.

Por meio de **reconhecimento de gestos utilizando visão computacional (MediaPipe)** e uma interface física com **Arduino**, o projeto permite que usuários possam emitir sinais visuais, sonoros e mensagens codificadas através de gestos com as mãos, mesmo em ambientes sem iluminação ou internet.

## ✋🖐️🆘 Demonstração dos Gestos

| Gesto                          | Ação                                        |
|-------------------------------|----------------------------------------------|
| ✋ Mão aberta                  | SOCORRO                                     |
| ✋✋ Duas mãos abertas          | ALERTA MÁXIMO (Prioridade Máxima)            |
| ☝️ Um dedo levantado          | ATENÇÃO                                     |
| ✌️ Dois dedos (índice e médio) | AJUDA TÉCNICA                               |
| 👌 OK (polegar + indicador)    | CONFIRMAÇÃO                                 |
| 🤚 Palma para cima             | SOLICITAÇÃO DE RECURSOS MATERIAIS            |

## 🚀 Acesso Rápido

- 🔗 [**Código Python – Detecção de Gestos**](./main.py/)  
- 🔗 [**Código Arduino – Interface de Sinalização**](./arduino.ino/)  
- 🎥 [**Vídeo no YouTube – Demonstração e Explicação**](https://youtube.com)  

## 🧠 Tecnologias Utilizadas

- 🐍 **Python** – Processamento de vídeo e reconhecimento de gestos.
- 🎯 **MediaPipe** – Framework de visão computacional (Reconhecimento de mãos).
- 📷 **OpenCV** – Processamento de imagem e interface da câmera.
- 🔌 **Arduino UNO** – Hardware responsável por emitir sinais visuais e sonoros.
- 🔊 **Buzzer Piezo** – Emissão de alarmes sonoros diferenciados.
- 💡 **LEDs (Verde e Vermelho)** – Sinalização visual.
- 📟 **LCD I2C 16x2** – Display de mensagens no hardware.
- 🔗 **Comunicação Serial (USB)** – Integração Python ↔ Arduino.

## 🔗 Arquitetura do Projeto

### 🔥 Diagrama de Funcionamento:

![Diagrama do EchoHands](./img/diagrama.png)

**Fluxo:**  
1. Usuário realiza um gesto →  
2. Webcam detecta →  
3. Python + MediaPipe classifica o gesto →   
4. Arduino recebe →  
5. Aciona buzzer, LEDs e LCD conforme o gesto.

## 🔌 Foto do Circuito Montado

![Circuito Montado](./img/circuito.jpeg)

## ✨ Créditos

Desenvolvido por:  
- ⚡ João Pedro Borsato Cruz – RM550294
- 💫 Maria Fernanda Vieira de Camargo – RM97956
- 🚀 Pedro Lucas de Andrade Nunes – RM550366

## 🚩 Referências
 
- 📚 [Documentação MediaPipe](https://mediapipe.readthedocs.io/en/latest/)  
- 📚 [Documentação OpenCV (Python)](https://docs.opencv.org/4.x/d0/de3/tutorial_py_intro.html)  
- 📚 [Documentação oficial do Arduino UNO](https://docs.arduino.cc/hardware/uno-rev3/)  
