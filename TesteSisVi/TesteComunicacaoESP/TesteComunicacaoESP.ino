HardwareSerial minhaSerial(2);

void setup() {
  Serial.begin(9600);
  minhaSerial.begin(9600, SERIAL_8N1, 16, 17);
  Serial.println("Número:");
}

void loop() {

  if (Serial.available()) {
    String dado = Serial.readStringUntil('\n');
    minhaSerial.println(dado);
    Serial.print("Enviado: ");
    Serial.println(dado);
  }

}

