import serial

port = serial.Serial('COM6',9600)

while( port.isOpen()):
    dado = str(input ("Digite a letra: ")).upper()
    if (dado == 'V'):
        port.write (b'1')
        
    elif (dado == 'O'):
        port.write(b'2')
        break
    elif (dado == 'L'):
        port.write(b'3')
        break
    elif (dado == 'K'):
        port.write(b'4')
        break
    elif (dado == 'S'):
        port.write(b'5')
        break
    elif (dado == 'W'):
        port.write(b'6')
        break
    elif (dado == 'A'):
        port.write(b'7')
        break
    elif (dado == 'G'):
        port.write(b'8')
        break
    elif (dado == 'E'):
        port.write(b'9')
        break
    elif (dado == 'N'):
        port.write(b'10')                            
    else:
        port.write(b'11')
        break
    