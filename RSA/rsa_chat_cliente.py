import socket
import threading
from datetime import datetime

from rsa_manual import gerar_chaves, cifrar, decifrar

HOST = "127.0.0.1"
PORT = 65432
NOME = "Cliente"

LINHA = "─" * 60
COR_INFO = "\033[93m"
COR_SERVIDOR = "\033[92m"
RESET = "\033[0m"


def agora():
    return datetime.now().strftime("%H:%M:%S")


def info(msg):
    print(f"{COR_INFO}[INFO] {msg}{RESET}")


def msg(remetente, texto, cor):
    print(f"\n{cor}[{agora()}] {remetente}:{RESET} {texto}")


# RECEBER
def receber(sock, priv):
    while True:
        try:
            tam = int.from_bytes(sock.recv(4), "big")

            dados = b""
            while len(dados) < tam:
                dados += sock.recv(tam - len(dados))

            cifra = int.from_bytes(dados, "big")

            texto = decifrar(cifra, priv)

            # 👇 só aqui aparece mensagem do outro lado
            print(f"\n[Servidor]: {texto}")
            print("  [cifrado recebido]")

        except:
            break


def main():
    print(LINHA)
    print("  CHAT RSA – CLIENTE")
    print(LINHA)

    info("Gerando chaves...")
    pub, priv = gerar_chaves(2048)
    info("Chaves geradas.")

    print("\n[CHAVE PÚBLICA]")
    print(pub)

    sock = socket.socket()
    sock.connect((HOST, PORT))

    info("Conectado ao servidor")
    info("Canal ativo!")

    threading.Thread(
        target=receber,
        args=(sock, priv),
        daemon=True
    ).start()

    print(LINHA)
    print("  Digite sua mensagem e pressione ENTER.")
    print("  Para sair, /sair")
    print(LINHA)

    while True:
        texto = input(f"{NOME} > ")

        if texto == "/sair":
            break

        # 👇 MOSTRA TEXTO LIMPO (isso estava faltando)
        print(f"{NOME} > {texto}")

        # criptografa
        cifra = cifrar(texto, pub)

        dados = cifra.to_bytes((cifra.bit_length() + 7) // 8, "big")

        sock.sendall(len(dados).to_bytes(4, "big"))
        sock.sendall(dados)

        print("  [mensagem cifrada enviada]")


if __name__ == "__main__":
    main()