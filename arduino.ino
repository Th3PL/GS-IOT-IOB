#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// LCD I2C no endereço 0x27, 16 colunas e 2 linhas
LiquidCrystal_I2C lcd(0x27, 16, 2);

const int pinoBuzzer = 8;
const int ledVerde = 6;
const int ledVermelho = 7;

void setup() {
  pinMode(ledVerde, OUTPUT);
  pinMode(ledVermelho, OUTPUT);
  pinMode(pinoBuzzer, OUTPUT);

  // Inicializa o LCD
  lcd.init();
  lcd.backlight();

  // Escreve no LCD
  lcd.setCursor(0, 0);
  lcd.print("Hello, Mundo!");

  lcd.setCursor(0, 1);
  lcd.print("Teste LCD I2C");
}

void loop() {
  // Buzzer toca 1000Hz
  tone(pinoBuzzer, 1000);
  delay(500);
  noTone(pinoBuzzer);
  delay(500);

  // Liga LED verde e desliga vermelho
  digitalWrite(ledVerde, HIGH);
  digitalWrite(ledVermelho, LOW);
  delay(500);

  // Liga LED vermelho e desliga verde
  digitalWrite(ledVerde, LOW);
  digitalWrite(ledVermelho, HIGH);
  delay(500);
}
