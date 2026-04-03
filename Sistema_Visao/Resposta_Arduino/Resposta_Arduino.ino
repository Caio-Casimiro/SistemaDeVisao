// Programa pra responder o python
void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n') return;

    Serial.println("Confirmado: " + String(c));
  }