#define led1 2
#define led2 4  

void setup() {
  Serial.begin(9600);
  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
}

void loop() 
{
  if (Serial.available() > 0) 
  {
    char dado = Serial.read();

    if (dado == '1') 
    {
      digitalWrite(led1, HIGH);
    }
    else if (dado == '2') 
    {
      digitalWrite(led2, HIGH);
    }
    else if (dado == '0') 
    {
      digitalWrite(led1, LOW);
      digitalWrite(led2, LOW);
      Serial.println("Reset");
    }
  }
}

