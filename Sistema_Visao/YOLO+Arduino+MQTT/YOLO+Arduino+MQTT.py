import cv2
from ultralytics import YOLO
from pathlib import Path
import serial.tools.list_ports
import serial
import paho.mqtt.client as mqtt
import time
import threading
#pip install -r requirements.txt

# Pega o caminho do best.pt
pasta = Path(__file__).resolve().parent
caminho = pasta / "modelo.pt"

# Configurações de modelo e câmera 
modelo = YOLO(caminho)
camera = cv2.VideoCapture(0)

# Definir confiança, frames de confirmação e tolerância
confianca = 0.85
frame_conf = 12
tolerancia = 3
tempo_parada = 5

# Configurações de Arduino
portas = serial.tools.list_ports.comports()
keywords = ["COM7"]

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
    arduino_connect = True
else: 
    arduino_connect = False

# Printa tudo que o Arduino mandar
def leitura_serial(arduino):
    while True:
        try:
            if arduino.in_waiting > 0:
                linha = arduino.readline().decode(errors='replace').strip()
                if linha:
                    print(f"[Arduino] {linha}")
        except serial.SerialException:
            print("[Arduino] Conexão serial perdida.")
            break
        except Exception as e:
            print(f"[Arduino] Erro na leitura: {e}")

if arduino_connect:
    thread_serial = threading.Thread(target=leitura_serial, args=(arduino,), daemon=True)
    thread_serial.start()

# Configurações do MQTT
broker = "broker.emqx.io"
port = 1883
topic = "vw/visao"
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

confirmado = None

def ao_publicar(client, userdata, mid, status, properties):
    global confirmado
    # Se o código for 0 ou sucesso, deu certo
    if status == 0 or str(status) == "Success":
        print(f"Enviado pro MQTT: {confirmado}")
    else:
        print(f"Falha ao enviar pro MQTT: {confirmado} (Erro: {status})")

client.on_publish = ao_publicar

try:
    client.connect(broker, port, 60)
    client.loop_start()
    print("Conectado ao MQTT!")
    mqtt_connect = True
except Exception as erro:
    print(f"MQTT não conectado: {erro}")
    mqtt_connect = False



# Variáveis iniciais
confirmado_ant = None
detectado_ant = None
cont_frame = 0
frame_vazio = 0
tempo_confirmado = 0


# Começa o loop principal
try: 
    while True:

        retorno, frame = camera.read()

        # Caso não achar a câmera, tenta reconectar
        if not retorno:
            camera.release()
            time.sleep(2)
            camera = cv2.VideoCapture(0)
            continue

         # Só classifica se o tempo desde a última confirmação for maior que o tempo de parada
        if (time.time() - tempo_confirmado) >= tempo_parada:
            # Lista do que a câmera achou 
            resultado = modelo(frame, conf=confianca, verbose=False)

            # Nome
            classes = resultado[0].boxes.cls
            # Confiança
            confs = resultado[0].boxes.conf

            detectado = None

            # Pega a classe de maior confiança
            if len(confs) > 0:
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
                frame_vazio += 1
                # Se parar de reconhecer, precisa passar da tolerância pra resetar
                if frame_vazio > tolerancia:
                    cont_frame = 0
                    detectado_ant = None

            # Confirma se passou da contagem
            if cont_frame >= frame_conf:
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
                    arduino.write((confirmado + '\n').encode())

                # Envio pro MQTT
                if mqtt_connect:
                    client.publish(topic, confirmado)

             # Printa vazio
            if (frame_vazio >= 15) and (confirmado_ant is not None):
                confirmado_ant = None
                print("Vazio")

            # Exibe o frame com as caixas
            frame_caixa = resultado[0].plot()

        # Caso esteja bloquado, para de reconhecer letras
        else:
            frame_caixa = frame

        cv2.imshow("Sistema de Visao", frame_caixa)

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
