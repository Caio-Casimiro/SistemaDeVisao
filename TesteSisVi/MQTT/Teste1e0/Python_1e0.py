# SUCESSO

import paho.mqtt.client as mqtt

BROKER = "c528854bf12543d8b8664534c44c3d18.s1.eu.hivemq.cloud"
PORT = 8883
TOPIC = "linha/teste"

client = mqtt.Client()
client.username_pw_set("CADASTRO", "SENHA")
client.tls_set()

client.connect(BROKER, PORT)
client.loop_start()

print("Digite 1 para LIGAR e 0 para DESLIGAR\n")

while True:
    comando = input("Comando: ").strip()

    if comando in ["1", "0"]:
        client.publish(TOPIC, comando)
        print("Enviado:", comando)
    else:
        print("Digite apenas 1 ou 0")

