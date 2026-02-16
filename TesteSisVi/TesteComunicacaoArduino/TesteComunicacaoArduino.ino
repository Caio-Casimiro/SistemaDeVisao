#include <SoftwareSerial.h>

SoftwareSerial minhaSerial(10, 11); 
//RX = 10 e TX = 11

void setup() {
  Serial.begin(9600);
  minhaSerial.begin(9600);
}

void loop() {

  if (minhaSerial.available()) {
    String recebido = minhaSerial.readStringUntil('\n');
    Serial.print("Recebido: ");
    Serial.println(recebido);
  }

}
