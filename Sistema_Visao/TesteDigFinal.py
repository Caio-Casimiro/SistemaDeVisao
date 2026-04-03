import serial.tools.list_ports
import serial
# py -m pip install pyserial

def achar_arduino():
    portas = serial.tools.list_ports.comports()

    keywords = ["USB Serial","Arduino", "ESP"]

    for porta in portas: 
        for palavra in keywords:
            if palavra in porta.description:
                print(f"Porta conectada: {porta.device}")
                return porta.device

    print("Nenhum arduino encontrado")
    return None


port = serial.Serial(achar_arduino(), 9600)

while port.isOpen():
    dado = input("Digite a letra: ").upper()
    port.write(dado.encode())