int dado;
#define led1 2
#define led2 4

void setup() {

  Serial.begin(9600);
  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(8, OUTPUT);

}

void loop() {

  while( Serial.available() )
  {
    dado = Serial.read();

    if (dado == '1')
    {
      digitalWrite(led1, HIGH);
      digitalWrite(led2, LOW);
      delay(10);
    }
    if (dado == '2')
    {
      digitalWrite(led2, HIGH);
      digitalWrite(led1, LOW);
      delay(10);
    }
    if (dado == '3')
    {
      digitalWrite(4, HIGH);
    
    }
    if (dado == '4')
    {
      digitalWrite(5, HIGH);
  
    }
    if (dado == '5')
    {
      digitalWrite(6, HIGH);
    
    }
    if (dado == '6')
    {
      digitalWrite(7, HIGH);
    
    }
    if (dado == '7')
    {
      digitalWrite(8, HIGH);
    
    }
  }


}
