import random, math

# Euclides estendido
def euclides_estendido(a: int, b: int):
    #Retorna (mdc, x, y) tal que: a*x + b*y = mdc(a, b)
    if a == 0:
        return b, 0, 1
    
    mdc, x1, y1 = euclides_estendido(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return mdc, x, y

def inverso_modular (e: int, phi: int) -> int:
    # Calcula d tal que: e * d ≡ 1 (mod φ)
    mdc, x, _ = euclides_estendido(e, phi)
    if mdc != 1:
        raise ValueError("Inverso modular não existe")
    
    return x % phi

# Miller-Rabin Simples
def miller_rabin (n: int, k: int = 10) -> bool:
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    
    # escreve n-1 = 2^r * d
    r, d = 0, n -1
    while d % 2 == 0:
        r += 1
        d //= 2

    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)

        if x in (1, n - 1):
            continue

        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False

    return True


def gerar_primo(bits: int) -> int:
    while True:
        n = random.getrandbits(bits)
        n |= (1 << bits - 1) | 1  # garante tamanho e ímpar

        if miller_rabin(n):
            return n
        
# Geração de chaves 
def gerar_chaves(bits: int = 512):
    #Gera chave pública (n, e) e privada (n, d)

    # 1. primos
    p = gerar_primo(bits // 2)
    q = gerar_primo(bits // 2)

    while q == p:
        q = gerar_primo(bits // 2)

    # 2. módulo
    n = p * q

    # 3. φ(n)
    phi = (p - 1) * (q - 1)

    # 4. expoente público
    e = 65537
    if math.gcd(e, phi) != 1:
        e = 3
        while math.gcd(e, phi) != 1:
            e += 2

    # 5. chave privada
    d = inverso_modular(e, phi)

    return (n, e), (n, d)

# Conversão de texto para inteiro
def texto_para_int(texto: str) -> int:
    return int.from_bytes(texto.encode("utf-8"), "big")


def int_para_texto(valor: int) -> str:
    tamanho = max(1, (valor.bit_length() + 7) // 8)
    return valor.to_bytes(tamanho, "big").decode("utf-8", errors="ignore")

# Cifrar e Decifrar
def cifrar(texto: str, chave_publica: tuple[int, int]) -> int:
    #C = M^e mod n
    n, e = chave_publica
    M = texto_para_int(texto)
    return pow(M, e, n)

def decifrar(cifrado: int, chave_privada: tuple[int, int]) -> str:
    #M = C^d mod n
    n, d = chave_privada
    M = pow(cifrado, d, n)
    return int_para_texto(M)

# Assinatura digital
def assinar(texto: str, chave_privada: tuple[int, int]) -> int:
    #S = H(M)^d mod n
    import hashlib

    n, d = chave_privada
    h = int(hashlib.sha256(texto.encode()).hexdigest(), 16) % n
    return pow(h, d, n)

def verificar_assinatura(texto: str, assinatura: int, chave_publica: tuple[int, int]) -> bool:
    #S^e mod n == H(M)
    import hashlib

    n, e = chave_publica
    h = int(hashlib.sha256(texto.encode()).hexdigest(), 16) % n
    return pow(assinatura, e, n) == h

# Teste rápido
if __name__ == "__main__":
    pub, priv = gerar_chaves(256)

    msg = "RSA manual funcionando 🔐"

    c = cifrar(msg, pub)
    d = decifrar(c, priv)

    print("Original:", msg)
    print("Cifrado :", c)
    print("Decifrado:", d)

    s = assinar(msg, priv)
    print("Assinatura válida:", verificar_assinatura(msg, s, pub))

