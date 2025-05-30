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
  lcd.setCursor(0, 0);
  lcd.print(gestoAtual);

  if (gestoAtual == "SOCORRO") {
    somSocorro();
  } else if (gestoAtual == "ALERTA_MAXIMO") {
    somAlertaMaximo();
  }
}

void atualizarLEDs() {
  unsigned long agora = millis();

  if (gestoAtual == "SOCORRO" || gestoAtual == "ALERTA_MAXIMO") {
    digitalWrite(ledVerde, LOW);
    if (agora - ultimoMillis >= intervaloPisca) {
      ultimoMillis = agora;
      estadoLed = !estadoLed;
      digitalWrite(ledVermelho, estadoLed);
    }
  }

  else if (
    gestoAtual == "AJUDA_TECNICA" ||
    gestoAtual == "ATENCAO" ||
    gestoAtual == "OK" ||
    gestoAtual == "RECURSOS" ||
    gestoAtual == "SOLICITACAO"
  ) {
    digitalWrite(ledVermelho, LOW);
    digitalWrite(ledVerde, HIGH);
  }

  else {
    digitalWrite(ledVerde, LOW);
    digitalWrite(ledVermelho, LOW);
  }
}

void somSocorro() {
  tone(pinoBuzzer, 1000, 500);
}

void somAlertaMaximo() {
  for (int i = 0; i < 3; i++) {
    tone(pinoBuzzer, 1500, 300);
    delay(400);
  }
}
