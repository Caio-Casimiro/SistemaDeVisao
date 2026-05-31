import cv2
from ultralytics import YOLO
from pathlib import Path
import serial.tools.list_ports
import serial
import paho.mqtt.client as mqtt
import time

#py - m pip install -r requirements.txt

# Pega o caminho do best.pt
pasta = Path(__file__).resolve().parent
caminho = pasta / "modelo.pt"

# Configurações de modelo e câmera 
modelo = YOLO(caminho)
camera = cv2.VideoCapture(0)

# Definir confiança, frames de confirmação e tolerância
confianca = 0.8
frame_conf = 5
tolerancia = 5
tempo_parada = 3

# Configurações de Arduino
portas = serial.tools.list_ports.comports()

keywords = ["USB Serial","Arduino", "ESP", "COM_XX"]

porta_arduino = None
for porta in portas: 
    for keyword in keywords:
        if keyword in porta.description:
            print(f"Porta conectada: {porta.device}")
            porta_arduino = porta.device

if porta_arduino is None:
    print("Nenhum arduino encontrado")

if porta_arduino is not None:
    arduino = serial.Serial(porta_arduino, 9600, timeout=0.1)
    arduino_connect =  True
else: 
    arduino_connect = False

# Configurações do MQTT
broker = "broker.hivemq.com"
port = 1883
topic = "topico_teste"
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
try:
    client.connect(broker, port, 60)
    client.loop_start()
    print("Conectado ao MQTT!")
    mqtt_connect = True
except Exception as erro:
    print(f"MQTT não conectado: {erro}")
    mqtt_connect = False

# Variaveis iniciais
confirmado_ant = None
detectado_ant = None
cont_frame = 0
frame_vazio = 0
tempo_confirmado = 0


# Caso não ache a câmera
if not camera.isOpened():
    print("Câmera não encontrada")
    exit()


# Começa o loop principal
try: 
    while camera.isOpened():
        retorno, frame = camera.read()
        if not retorno:
            continue

        # Só classifica se o tempo desde a última confirmação for maior que o tempo de parada
        if (time.time() - tempo_confirmado) >= tempo_parada:
            # Lista do que a câmera achou 
            resultado = modelo(frame, conf=confianca, verbose = False) # verbose é o texto do programa

            # Nome
            classes = resultado[0].boxes.cls
            # Confiança
            confs = resultado[0].boxes.conf

            detectado = None

            # Pega a classe de maior confiança
            if len(confs)>0:
                maior_classe = confs.argmax()
                if confs[maior_classe] >= confianca:
                    detectado = modelo.names[int(classes[maior_classe])]

            # Contagem dos frames detectados e vazios
            if detectado is not None:
                if detectado == detectado_ant:
                    # Mesma peça -> continua a contagem
                    cont_frame += 1
                    frame_vazio = 0
                else:
                    # Outra peça -> reinicia a contagem
                    detectado_ant = detectado
                    cont_frame = 1
                    frame_vazio = 0

            else:
                frame_vazio +=1
                # Se parar de reconhecer, precisa passar da tolerância pra resetar
                if frame_vazio > tolerancia:
                    cont_frame = 0
                    detectado_ant = None

            # Confirma se passou da contagem
            if cont_frame>= frame_conf:
                confirmado = detectado
            else:
                confirmado = None

            
            # Confirmação pra printar só quando mudar de peça
            if (confirmado is not None) and (confirmado != confirmado_ant):
                tempo_confirmado = time.time()
                print(f"Detectado: {confirmado}")
                confirmado_ant = confirmado
                # Envio pro Arduino
                if arduino_connect:
                    arduino.write((confirmado + '\n').encode()) # Tirar o \n caso mudar para char no arduino
                    confirmacao = arduino.readline().decode().strip()
                    print(f"Arduino confirmou: {confirmacao}")
                # Envia pro MQTT
                if mqtt_connect:
                    envio = client.publish(topic, confirmado)
                    if envio.is_published():
                        print(f"Enviado pro MQTT: {confirmado}")
                    else:
                        print(f"Falha ao enviar pro MQTT: {confirmado}")

            
            # Printa vazio
            if (frame_vazio >= 15) and (confirmado_ant is not None):
                confirmado_ant = None
                print("Vazio")

            # Exibe o frame com as caixas
            frame_caixa = resultado[0].plot()

        else:
            frame_caixa = frame

        cv2.imshow("Sistema de Visão", frame_caixa)


        # Aperte Q para fechar
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    camera.release()
    cv2.destroyAllWindows()
    if arduino_connect:
        arduino.close()
    if mqtt_connect:
        client.loop_stop()
        client.disconnect()
