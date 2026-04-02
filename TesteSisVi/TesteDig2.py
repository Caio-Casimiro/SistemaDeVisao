import serial

port = serial.Serial('COM6', 9600)

while port.isOpen():
    dado = input("Digite a letra: ").upper()
    port.write(dado.encode())