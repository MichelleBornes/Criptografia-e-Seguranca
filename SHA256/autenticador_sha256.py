#!/usr/bin/env python3
"""
Implementação manual do algoritmo SHA-256

"""

import struct
import sys
import os

# Constantes SHA-256
K = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
    0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
    0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
    0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
    0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
    0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
]


def rotacionar_direita(x, n):
    return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF


def ch(x, y, z):
    return (x & y) ^ (~x & z)


def maj(x, y, z):
    return (x & y) ^ (x & z) ^ (y & z)


def sigma0(x):
    return (
        rotacionar_direita(x, 7) ^
        rotacionar_direita(x, 18) ^
        (x >> 3)
    )


def sigma1(x):
    return (
        rotacionar_direita(x, 17) ^
        rotacionar_direita(x, 19) ^
        (x >> 10)
    )


def capsigma0(x):
    return (
        rotacionar_direita(x, 2) ^
        rotacionar_direita(x, 13) ^
        rotacionar_direita(x, 22)
    )


def capsigma1(x):
    return (
        rotacionar_direita(x, 6) ^
        rotacionar_direita(x, 11) ^
        rotacionar_direita(x, 25)
    )


def sha256_manual(mensagem: bytes) -> str:

    # Valores iniciais dos registradores
    h = [
        0x6a09e667,
        0xbb67ae85,
        0x3c6ef372,
        0xa54ff53a,
        0x510e527f,
        0x9b05688c,
        0x1f83d9ab,
        0x5be0cd19
    ]

    tamanho_original = len(mensagem) * 8

    # Padding
    mensagem += b'\x80'

    while ((len(mensagem) * 8) % 512) != 448:
        mensagem += b'\x00'

    mensagem += struct.pack('>Q', tamanho_original)

    # Processa blocos de 512 bits
    for i in range(0, len(mensagem), 64):

        bloco = mensagem[i:i+64]

        w = list(struct.unpack('>16L', bloco))

        # Expande para 64 palavras
        for j in range(16, 64):
            valor = (
                sigma1(w[j - 2]) +
                w[j - 7] +
                sigma0(w[j - 15]) +
                w[j - 16]
            ) & 0xFFFFFFFF

            w.append(valor)

        a, b, c, d, e, f, g, hh = h

        # 64 rodadas
        for j in range(64):

            t1 = (
                hh +
                capsigma1(e) +
                ch(e, f, g) +
                K[j] +
                w[j]
            ) & 0xFFFFFFFF

            t2 = (
                capsigma0(a) +
                maj(a, b, c)
            ) & 0xFFFFFFFF

            hh = g
            g = f
            f = e
            e = (d + t1) & 0xFFFFFFFF
            d = c
            c = b
            b = a
            a = (t1 + t2) & 0xFFFFFFFF

        # Atualiza registradores
        h[0] = (h[0] + a) & 0xFFFFFFFF
        h[1] = (h[1] + b) & 0xFFFFFFFF
        h[2] = (h[2] + c) & 0xFFFFFFFF
        h[3] = (h[3] + d) & 0xFFFFFFFF
        h[4] = (h[4] + e) & 0xFFFFFFFF
        h[5] = (h[5] + f) & 0xFFFFFFFF
        h[6] = (h[6] + g) & 0xFFFFFFFF
        h[7] = (h[7] + hh) & 0xFFFFFFFF

    return ''.join(f'{valor:08x}' for valor in h)


def calcular_hash_arquivo(caminho):

    if not os.path.isfile(caminho):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    with open(caminho, "rb") as f:
        dados = f.read()

    return sha256_manual(dados)


def gerar_hash(caminho):

    print("\n==============================")
    print(" GERADOR SHA-256 MANUAL")
    print("==============================")

    hash_hex = calcular_hash_arquivo(caminho)

    print(f"\nArquivo : {caminho}")
    print(f"Tamanho : {os.path.getsize(caminho)} bytes")
    print(f"SHA-256 : {hash_hex}\n")


def verificar_hash(caminho, hash_esperado):

    hash_calculado = calcular_hash_arquivo(caminho)

    print("\n==============================")
    print(" VERIFICAÇÃO SHA-256")
    print("==============================")

    print(f"\nArquivo        : {caminho}")
    print(f"Hash esperado  : {hash_esperado}")
    print(f"Hash calculado : {hash_calculado}")

    if hash_calculado.lower() == hash_esperado.lower():
        print("\nArquivo autêntico.\n")
    else:
        print("\nArquivo alterado ou corrompido.\n")


def menu():

    while True:

        print("=" * 60)
        print("        SHA-256 IMPLEMENTAÇÃO MANUAL")
        print("=" * 60)
        print("1 - Gerar hash")
        print("2 - Verificar hash")
        print("0 - Sair")
        print("=" * 60)

        opcao = input("Escolha: ").strip()

        if opcao == "1":

            caminho = input("Arquivo: ").strip()

            try:
                gerar_hash(caminho)
            except Exception as e:
                print(f"\nErro: {e}\n")

        elif opcao == "2":

            caminho = input("Arquivo: ").strip()
            hash_esperado = input("Hash esperado: ").strip()

            try:
                verificar_hash(caminho, hash_esperado)
            except Exception as e:
                print(f"\nErro: {e}\n")

        elif opcao == "0":
            print("\nSaindo...\n")
            break

        else:
            print("\nOpção inválida.\n")


if __name__ == "__main__":
    menu()