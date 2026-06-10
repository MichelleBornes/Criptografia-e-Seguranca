import socket
import threading
from datetime import datetime

from rsa_manual import gerar_chaves, cifrar, decifrar

HOST = "127.0.0.1"
PORT = 65432
NOME = "Servidor"

LINHA = "─" * 60
COR_INFO = "\033[93m"
COR_CLIENTE = "\033[94m"
RESET = "\033[0m"


def agora():
    return datetime.now().strftime("%H:%M:%S")


def info(msg):
    print(f"{COR_INFO}[INFO] {msg}{RESET}")


def msg(remetente, texto, cor):
    print(f"\n{cor}[{agora()}] {remetente}:{RESET} {texto}")


# RECEBER
def receber(conn, priv):
    while True:
        try:
            tam = int.from_bytes(conn.recv(4), "big")

            dados = b""
            while len(dados) < tam:
                dados += conn.recv(tam - len(dados))

            cifra = int.from_bytes(dados, "big")

            texto = decifrar(cifra, priv)

            print(f"\n[Cliente]: {texto}")
            print("  [cifrado recebido]")

        except:
            break


def main():
    print(LINHA)
    print("  CHAT RSA – SERVIDOR")
    print(LINHA)

    info("Gerando chaves...")
    pub, priv = gerar_chaves(2048)
    info("Chaves geradas.")

    print("\n[CHAVE PÚBLICA]")
    print(pub)

    server = socket.socket()
    server.bind((HOST, PORT))
    server.listen(1)

    info(f"\nAguardando conexão em {HOST}:{PORT}...")

    conn, addr = server.accept()

    info(f"Cliente conectado: {addr}")
    info("Canal ativo!")

    threading.Thread(
        target=receber,
        args=(conn, priv),
        daemon=True
    ).start()

    while True:
        texto = input("Servidor > ")

        if texto == "/sair":
            break

        print(f"Servidor > {texto}")  # 👈 ESSENCIAL

        cifra = cifrar(texto, pub)

        dados = cifra.to_bytes((cifra.bit_length() + 7) // 8, "big")

        conn.sendall(len(dados).to_bytes(4, "big"))
        conn.sendall(dados)

        print("  [mensagem cifrada enviada]")


if __name__ == "__main__":
    main()