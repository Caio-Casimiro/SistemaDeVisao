//SUCESSO

/************************************************************
 * ESP32 - MQTT Subscriber (HiveMQ Cloud)
 * Recebe "1" → Liga LED
 * Recebe "0" → Desliga LED
 ************************************************************/

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>

/******************** WIFI ****************************/
const char* ssid = "NOME_WIFI";
const char* password = "SENHA_WIFI";

/******************** MQTT ****************************/
const char* mqtt_server = "c528854bf12543d8b8664534c44c3d18.s1.eu.hivemq.cloud";
const int mqtt_port = 8883;
const char* mqtt_topic = "linha/teste";

/******************** LOGIN MQTT ***********************/
const char* mqtt_user = "USUARIO_MQTT";
const char* mqtt_pass = "SENHA_MQTT";

/******************** OBJETOS *************************/
WiFiClientSecure espClient;
PubSubClient client(espClient);

/******************** HARDWARE ************************/
const int ledPin = 2;

/************************************************************
 * CALLBACK - Executado quando chega mensagem
 ************************************************************/
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.println("=== CALLBACK EXECUTADO ===");

  String mensagem = "";

  for (int i = 0; i < length; i++) {
    mensagem += (char)payload[i];
  }

  mensagem.trim();

  Serial.print("Topico: ");
  Serial.println(topic);

  Serial.print("Mensagem recebida: ");
  Serial.println(mensagem);

  if (mensagem == "1") {
    digitalWrite(ledPin, HIGH);
    Serial.println(">> LED LIGADO");
  } else if (mensagem == "0") {
    digitalWrite(ledPin, LOW);
    Serial.println(">> LED DESLIGADO");
  } else {
    Serial.println(">> Comando desconhecido");
  }
}

/************************************************************
 * CONEXÃO MQTT
 ************************************************************/
void reconnect() {
  if (!client.connected()) {
    Serial.println("Conectando ao MQTT...");

    String clientId = "ESP32_";
    clientId += String((uint32_t)ESP.getEfuseMac(), HEX);

    if (client.connect(clientId.c_str(), mqtt_user, mqtt_pass)) {
      Serial.println("Conectado ao MQTT!");
      client.subscribe(mqtt_topic);

      Serial.print("Inscrito no topico: ");
      Serial.println(mqtt_topic);
    } else {
      Serial.print("Falha MQTT, rc=");
      Serial.println(client.state());
      Serial.println("Tentando novamente em 5 segundos...");
      delay(5000);
    }
  }
}

/************************************************************
 * SETUP
 ************************************************************/
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("===== INICIANDO ESP32 =====");

  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);  // começa desligado

  /*************** WIFI ***************/
  Serial.println("Conectando ao WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi conectado!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  /*************** TLS ***************/
  espClient.setInsecure();
  espClient.setTimeout(15000);

  /*************** MQTT ***************/
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  client.setBufferSize(1024);
  client.setKeepAlive(60);
}

/************************************************************
 * LOOP PRINCIPAL
 ************************************************************/
void loop() {
  if (!client.connected()) {
    reconnect();
  }

  client.loop();

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi caiu! Reconectando...");
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }

  Serial.println("\nWiFi reconectado!");
  }
}