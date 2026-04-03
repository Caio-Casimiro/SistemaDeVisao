import cv2
from ultralytics import YOLO
from pathlib import Path
import serial.tools.list_ports
import serial
#py - m pip install opencv-python ultralytics pyserial

# Pega o caminho do best.pt
pasta = Path(__file__).resolve().parent
caminho = pasta / "best.pt"

# Procura arduino
def achar_arduino():
    portas = serial.tools.list_ports.comports()

    keywords = ['USB Serial","Arduino", "ESP']

    for porta in portas: 
        for palavra in keywords:
            if palavra in porta.description:
                print(f"Porta conectada: {porta.device}")
                return porta.device

    print("Nenhum arduino encontrado")
    exit()


# Configurações de arduino, modelo e câmera 
arduino = serial.Serial(achar_arduino(), 9600)
modelo = YOLO(caminho)
camera = cv2.VideoCapture(0)


# Definir confiança, frames de confirmação e tolerância
confianca = 0.8
frame_conf = 5
tolerancia = 5

# Variaveis iniciais
estado_ant = None
cont_frame = 0
frame_vazio = 0

# Caso não ache a câmera
if not camera.isOpened():
    print("Câmera não encontrada")
    exit()

# Começa o loop principal
while camera.isOpened():
    retorno, frame = camera.read()

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
        cont_frame += 1
        frame_vazio = 0
    else:
        frame_vazio +=1
        # Se parar de reconhecer, precisa passar da tolerância pra resetar
        if frame_vazio > tolerancia:
            cont_frame = 0

    # Confirma se passou da contagem
    if cont_frame>= frame_conf:
        confirmado = detectado
    else:
        confirmado = None

    
    # Confirmação pra printar só quando mudar de peça
    if (confirmado is not None) and (confirmado != estado_ant):
        print(f"Detectado: {confirmado}")
        estado_ant = confirmado
        # Envio pro Arduino
        if arduino.is_open:
            arduino.write((confirmado + '\n').encode()) # Tirar o \n caso mudar para char no arduino
            confirmacao = arduino.readline().decode().strip()
            print(f"Arduino confirmou: {confirmacao}")
    
    # Printa vazio
    if (frame_vazio == 15) and (estado_ant is not None):
        estado_ant = None
        print("Vazio")


# Exibe o frame com as caixas
    frame_caixa = resultado[0].plot()
    cv2.imshow("Janela", frame_caixa)


# Aperte Q para fechar
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
arduino.close()