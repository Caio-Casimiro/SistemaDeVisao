import paho.mqtt.client as mqtt

# Configurações do MQTT
broker = "broker.hivemq.com"
port = 1883
topic = "topico_teste"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

try:
    client.connect(broker, port, 60)
    client.loop_start()
    print("Conectado ao MQTT!")
except Exception as erro:
    print(f"MQTT não conectado: {erro}")
    exit()

try:
    while True:
        mensagem = input("Digite a mensagem: ")

        envio = client.publish(topic, mensagem)
        if envio.is_published():
            print(f"Enviado: {mensagem}")
        else:
            print(f"Falha ao enviar: {mensagem}")

finally:
    client.loop_stop()
    client.disconnect()