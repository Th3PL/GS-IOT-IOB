#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <ArduinoJson.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

const int pinoBuzzer = 8;
const int ledVerde = 6;
const int ledVermelho = 7;

String inputString = "";
bool stringComplete = false;

unsigned long ultimoMillis = 0;
const long intervaloPisca = 500;
bool estadoLed = LOW;

// Estados dos gestos
String gestoAtual = "IDLE";

void setup() {
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();

  pinMode(ledVerde, OUTPUT);
  pinMode(ledVermelho, OUTPUT);
  pinMode(pinoBuzzer, OUTPUT);

  lcd.setCursor(0, 0);
  lcd.print("Sistema pronto");
  lcd.setCursor(0, 1);
  lcd.print("Aguardando...");
}

void loop() {
  lerSerial();

  atualizarLEDs();
}

// 📥 Ler dados da Serial
void lerSerial() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      stringComplete = true;
      break;
    } else {
      inputString += inChar;
    }
  }

  if (stringComplete) {
    processarJson(inputString);
    inputString = "";
    stringComplete = false;
  }
}

// 🔧 Processar JSON recebido
void processarJson(String jsonString) {
  StaticJsonDocument<200> doc;

  DeserializationError error = deserializeJson(doc, jsonString);
  if (error) {
    Serial.print("Erro no JSON: ");
    Serial.println(error.c_str());
    return;
  }

  const char* gesto = doc["gesto"];
  gestoAtual = String(gesto);

  lcd.clear();
  lcd.print(gestoAtual);

  // 🔊 Sons apenas nos gestos críticos
  if (gestoAtual == "SOCORRO") {
    somSocorro();
  } else if (gestoAtual == "ALERTA_MAXIMO") {
    somAlertaMaximo();
  }
}

// ✨ Atualiza LEDs sem travar
void atualizarLEDs() {
  unsigned long agora = millis();

  // SOCORRO e ALERTA_MAXIMO → 🔴 Pisca, 🟢 apagado
  if (gestoAtual == "SOCORRO" || gestoAtual == "ALERTA_MAXIMO") {
    digitalWrite(ledVerde, LOW);
    if (agora - ultimoMillis >= intervaloPisca) {
      ultimoMillis = agora;
      estadoLed = !estadoLed;
      digitalWrite(ledVermelho, estadoLed);
    }
  }

  // AJUDA_TECNICA, ATENCAO, OK, RECURSOS, SOLICITACAO → 🟢 Pisca, 🔴 apagado
  else if (
    gestoAtual == "AJUDA_TECNICA" ||
    gestoAtual == "ATENCAO" ||
    gestoAtual == "OK" ||
    gestoAtual == "RECURSOS" ||
    gestoAtual == "SOLICITACAO"
  ) {
    digitalWrite(ledVermelho, LOW);
    if (agora - ultimoMillis >= intervaloPisca) {
      ultimoMillis = agora;
      estadoLed = !estadoLed;
      digitalWrite(ledVerde, estadoLed);
    }
  }

  // Outros → 🟢 aceso fixo, 🔴 apagado
  else {
    digitalWrite(ledVerde, HIGH);
    digitalWrite(ledVermelho, LOW);
  }
}

// 🔊 Som SOCORRO (2 bips agudos rápidos)
void somSocorro() {
  for (int i = 0; i < 2; i++) {
    tone(pinoBuzzer, 2000);
    delay(200);
    noTone(pinoBuzzer);
    delay(150);
  }
}

// 🔊 Som ALERTA MÁXIMO (3 bips graves rápidos)
void somAlertaMaximo() {
  for (int i = 0; i < 3; i++) {
    tone(pinoBuzzer, 1000);
    delay(150);
    noTone(pinoBuzzer);
    delay(150);
  }
}