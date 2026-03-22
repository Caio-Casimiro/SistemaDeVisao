import cv2
from ultralytics import YOLO
from pathlib import Path


pasta = Path(__file__).resolve().parent
caminho = pasta / 'best.pt'

modelo = YOLO(caminho)
camera = cv2.VideoCapture(0)

# Variaveis iniciais
estado_ant = set()
cont_frame = {}
frame_vazio = 0
confianca = 0.8
frame_conf = 5

if not camera.isOpened():
    print('Câmera não encontrada')
    exit()

# Começa o loop principal
# Verifica os frames
while camera.isOpened():
    retorno, frame = camera.read()

    resultado = modelo(frame, conf=confianca, verbose = False) # verbose é o texto do programa

    classes = resultado[0].boxes.cls
    confs = resultado[0].boxes.conf

    detectado = set()

    for cls,conf in zip(classes, confs):
        if conf >= confianca:
            nome = modelo.names[int(cls)]
            detectado.add(nome)

    # Contagem e confirmação por frames
    for nome in detectado:
        cont_frame[nome] = cont_frame.get(nome, 0) + 1

    for nome in list(cont_frame.keys()):
        if nome not in detectado:
            cont_frame[nome] = 0

    confirmadas = set(nome for nome, cont in cont_frame.items() if cont>=frame_conf)  

    # Controle pros frames vazios
    if not confirmadas:
        frame_vazio += 1
    else:
        frame_vazio = 0

    # Confirmação pra printar só quando mudar de peça
    if (confirmadas != estado_ant) and confirmadas:
        print(f'Detectado: {"".join(confirmadas)}')
    if (frame_vazio == 15):
        print('Vazio')

    estado_ant = confirmadas.copy()     

# Exibe o frame com as caixas
    frame_caixa = resultado[0].plot()
    cv2.imshow('Janela', frame_caixa)



    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()