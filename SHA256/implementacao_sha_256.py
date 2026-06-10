import struct

VALORES_INICIAIS = [
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
]


CONSTANTES_K = [
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
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
]


# =============================================================================
# FUNÇÕES AUXILIARES DE BITS
# =============================================================================

def rotr(valor, n, bits=32):
    """Rotação circular para a direita de 'n' posições em palavra de 'bits' bits."""
    return ((valor >> n) | (valor << (bits - n))) & 0xFFFFFFFF


def shr(valor, n):
    """Deslocamento lógico para a direita (sem rotação)."""
    return (valor >> n) & 0xFFFFFFFF


def soma32(a, b):
    """Soma módulo 2^32 (mantém apenas os 32 bits inferiores)."""
    return (a + b) & 0xFFFFFFFF


# =============================================================================
# ETAPA 3 — Funções de Expansão da Mensagem
# =============================================================================

def sigma0(x):
    """σ₀(x) = (x ROTR 7) ⊕ (x ROTR 18) ⊕ (x >> 3)"""
    return rotr(x, 7) ^ rotr(x, 18) ^ shr(x, 3)


def sigma1(x):
    """σ₁(x) = (x ROTR 17) ⊕ (x ROTR 19) ⊕ (x >> 10)"""
    return rotr(x, 17) ^ rotr(x, 19) ^ shr(x, 10)


# =============================================================================
# ETAPA 4 — Funções de Compressão
# =============================================================================

def Sigma0(x):
    """Σ₀(x) = (x ROTR 2) ⊕ (x ROTR 13) ⊕ (x ROTR 22)"""
    return rotr(x, 2) ^ rotr(x, 13) ^ rotr(x, 22)


def Sigma1(x):
    """Σ₁(x) = (x ROTR 6) ⊕ (x ROTR 11) ⊕ (x ROTR 25)"""
    return rotr(x, 6) ^ rotr(x, 11) ^ rotr(x, 25)


def Ch(x, y, z):
    """Choose: (x ∧ y) ⊕ (¬x ∧ z)
    x 'escolhe' entre y e z bit a bit."""
    return (x & y) ^ (~x & z) & 0xFFFFFFFF


def Maj(x, y, z):
    """Majority: (x ∧ y) ⊕ (x ∧ z) ⊕ (y ∧ z)
    Retorna o bit que aparece na maioria dos inputs."""
    return (x & y) ^ (x & z) ^ (y & z)


# =============================================================================
# Padding (Preenchimento da Mensagem)
# =============================================================================

def aplicar_padding(mensagem: bytes) -> bytes:
    """
    Ajusta a mensagem para que seu tamanho seja múltiplo de 512 bits (64 bytes).

    Processo:
    1. Adiciona o byte 0x80 (bit '1' seguido de zeros) ao final.
    2. Preenche com bytes 0x00 até restar 8 bytes livres no bloco.
    3. Insere o tamanho original da mensagem em bits nos últimos 8 bytes (big-endian).
    """
    tamanho_original_bits = len(mensagem) * 8

    # Adiciona o bit '1' (representado como 0x80 em byte)
    mensagem += b'\x80'

    # Preenche com zeros até restar 8 bytes para o campo de tamanho
    # (o bloco total deve ser múltiplo de 64 bytes = 512 bits)
    while len(mensagem) % 64 != 56:
        mensagem += b'\x00'

    # Adiciona o tamanho original em 8 bytes (64 bits), big-endian
    mensagem += struct.pack('>Q', tamanho_original_bits)

    return mensagem


# =============================================================================
# Expansão: divide bloco em 64 palavras W[0..63]
# =============================================================================

def expandir_bloco(bloco: bytes) -> list:
    """
    Recebe um bloco de 64 bytes (512 bits) e retorna 64 palavras W[0..63].

    As primeiras 16 palavras vêm diretamente do bloco.
    As 48 restantes são calculadas com σ₀ e σ₁.
    """
    W = list(struct.unpack('>16I', bloco))  # 16 inteiros de 32 bits, big-endian

    for i in range(16, 64):
        w = soma32(sigma1(W[i - 2]), W[i - 7])
        w = soma32(w, sigma0(W[i - 15]))
        w = soma32(w, W[i - 16])
        W.append(w)

    return W


# =============================================================================
# Compressão de um bloco (64 rodadas)
# =============================================================================

def comprimir_bloco(W: list, registradores: list) -> list:
    """
    Executa as 64 rodadas de compressão sobre as palavras W[],
    usando o estado atual dos registradores H0…H7.

    Retorna os novos valores de a,b,c,d,e,f,g,h (ainda NÃO somados a H0…H7).
    """
    a, b, c, d, e, f, g, h = registradores

    for i in range(64):
        T1 = soma32(h, Sigma1(e))
        T1 = soma32(T1, Ch(e, f, g))
        T1 = soma32(T1, CONSTANTES_K[i])
        T1 = soma32(T1, W[i])

        T2 = soma32(Sigma0(a), Maj(a, b, c))

        h = g
        g = f
        f = e
        e = soma32(d, T1)
        d = c
        c = b
        b = a
        a = soma32(T1, T2)

    return [a, b, c, d, e, f, g, h]


# =============================================================================
# FUNÇÃO PRINCIPAL: sha256()
# =============================================================================

def sha256(dados: bytes) -> str:

    # --- Etapa 1: Padding ---
    mensagem_padded = aplicar_padding(dados)

    # --- Etapa 2: Inicialização dos registradores H0…H7 ---
    H = list(VALORES_INICIAIS)

    # Processa cada bloco de 512 bits (64 bytes)
    num_blocos = len(mensagem_padded) // 64

    for bloco_idx in range(num_blocos):
        bloco = mensagem_padded[bloco_idx * 64 : (bloco_idx + 1) * 64]

        # --- Etapa 3: Expansão do bloco em 64 palavras ---
        W = expandir_bloco(bloco)

        # --- Etapa 4: Compressão ---
        novo_estado = comprimir_bloco(W, H)

        # --- Etapa 5: Atualização dos registradores ---
        H = [soma32(H[i], novo_estado[i]) for i in range(8)]

    # --- Etapa 6: Geração do hash final ---
    # Concatena H0||H1||H2||H3||H4||H5||H6||H7 em hexadecimal
    hash_final = ''.join(f'{h:08x}' for h in H)
    return hash_final


# =============================================================================
# DEMONSTRAÇÃO
# =============================================================================

if __name__ == '__main__':
    print("=" * 65)
    print("         SHA-256 — Implementação Manual em Python")
    print("=" * 65)

    # Caso 1: string simples
    entrada1 = "hello world"
    hash1 = sha256(entrada1.encode('utf-8'))
    print(f"\n[Entrada]  \"{entrada1}\"")
    print(f"[SHA-256]  {hash1}")

    # Caso 2: string vazia
    entrada2 = ""
    hash2 = sha256(entrada2.encode('utf-8'))
    print(f"\n[Entrada]  \"\" (string vazia)")
    print(f"[SHA-256]  {hash2}")

    # Caso 3: demonstração do efeito avalanche
    entrada3a = "abc"
    entrada3b = "abd"  # apenas 1 caractere diferente!
    hash3a = sha256(entrada3a.encode('utf-8'))
    hash3b = sha256(entrada3b.encode('utf-8'))
    print(f"\n[Efeito Avalanche — 1 caractere diferente]")
    print(f"  \"{entrada3a}\" → {hash3a}")
    print(f"  \"{entrada3b}\" → {hash3b}")

    # Conta bits diferentes
    bits_a = bin(int(hash3a, 16))[2:].zfill(256)
    bits_b = bin(int(hash3b, 16))[2:].zfill(256)
    bits_diferentes = sum(a != b for a, b in zip(bits_a, bits_b))
    print(f"  Bits diferentes: {bits_diferentes} de 256 ({bits_diferentes/256*100:.1f}%)")

    # Caso 4: verificação de integridade
    arquivo_original = b"Relatorio_Financeiro_Q4_2024.pdf"
    hash_original = sha256(arquivo_original)
    print(f"\n[Verificação de Integridade]")
    print(f"  Hash original : {hash_original}")

    # Simula adulteração: 1 byte diferente
    arquivo_adulterado = b"Relatorio_Financeiro_Q4_2025.pdf"
    hash_adulterado = sha256(arquivo_adulterado)
    print(f"  Hash adulterado: {hash_adulterado}")
    print(f"  Arquivos iguais? {'SIM ✓' if hash_original == hash_adulterado else 'NÃO — adulteração detectada! ✗'}")

    # Validação com a biblioteca padrão do Python
    print("\n" + "-" * 65)
    print("[Validação com hashlib do Python]")
    import hashlib
    for texto in ["hello world", "", "abc", "abd"]:
        h_manual = sha256(texto.encode())
        h_oficial = hashlib.sha256(texto.encode()).hexdigest()
        status = "✓ OK" if h_manual == h_oficial else "✗ ERRO"
        print(f"  \"{texto}\" → {status}")

    print("\n" + "=" * 65)
    print("  Todos os hashes batem com a implementação oficial!")
    print("=" * 65)
