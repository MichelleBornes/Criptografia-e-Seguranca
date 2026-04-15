#Algoritmo Base64

BASE64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

def codificar(texto):
    bits = "".join(format(byte, '08b') for byte in texto.encode())

    # padding de bits
    len(texto.encode()) % 3
    if len(texto) % 3 == 1:
        resultado_base64 += "=="
    elif len(texto) % 3 == 2:
        resultado_base64 += "="

    # Divide a string em grupos de 6 bits
    grupos = [bits[i:i+6] for i in range(0, len(bits), 6)]

    resultado_base64 = "".join(BASE64[int(g, 2)] for g in grupos)

    # padding "="
    if len(texto) % 3 == 1:
        resultado_base64 += "=="
    elif len(texto) % 3 == 2:
        resultado_base64 += "="


    return resultado_base64

def decodificar(texto_base64):
    texto_base64 = texto_base64.rstrip("=")

    bits = "".join(format(BASE64.index(c), "06b") for c in texto_base64)

    bytes_lista = [
        int(bits[i:i+8], 2)
        for i in range(0, len(bits), 8)
        if len(bits[i:i+8]) == 8
    ]

    return bytes(bytes_lista).decode() 

if __name__ == "__main__":
    print("\n=== INICIANDO BASE64 ===")

    texto = input("Digite o texto para codificar: ")
    print("Texto: ", texto)

    codificado = codificar(texto)
    print("Codificado: ", codificado)

    decodificado = decodificar(codificado)
    print("Decodificado: ", decodificado)

    print("\nFim do programa...")



