import os
import shutil
import hashlib

MAPEAMENTO_PADRAO = {
        "Imagens":     [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"],
        "Documentos":  [".pdf", ".docx", ".txt", ".xlsx", ".odt", ".csv", ".latex", ".xltx", ".dotx", ".pptx", ".ppsx", ".potx", ".xlsm"],
        "Videos":      [".mp4", ".mkv", ".avi", ".mov"],
        "Musicas":     [".mp3", ".wav", ".flac", ".ogg"],
        "Apps/Executáveis": [".deb", ".sh", ".rpm", ".py", ".cs", ".html", ".css", ".json", ".exe", ".apk", ".elf", ".bin", ".bat", ".msi"],
    }

    
def calcular_hash(caminho_arquivo, bloco=65536):
    """Calcula o hash SHA-256 do conteúdo de um arquivo, lendo em blocos
    para não estourar a memória com arquivos grandes."""
    sha256 = hashlib.sha256()
    with open(caminho_arquivo, "rb") as f:
        for pedaco in iter(lambda: f.read(bloco), b""):
            sha256.update(pedaco)
    return sha256.hexdigest()

def encontrar_pasta(nomes_possiveis):
        home = os.path.expanduser("~")
        for nome in nomes_possiveis:
            caminho = os.path.join(home, nome)
            if os.path.exists(caminho):
                return caminho
        caminho = os.path.join(home, nomes_possiveis[0])
        os.makedirs(caminho, exist_ok=True)
        return caminho
#se necessário!

def criar_pastas_necessarias(destino, mapeamento=MAPEAMENTO_PADRAO, log=None):
    criadas = []
    for categoria in mapeamento.keys():
        caminho = os.path.join(destino, categoria)
        if not os.path.exists(caminho):
            os.makedirs(caminho, exist_ok=True)
            criadas.append(caminho)
            if log:
                log(f"Pasta criada: {caminho}")
        else:
            if log:
                log(f"Já existe: {caminho}")
    return criadas

def organizar(pasta_download, pasta_destino, mapeamento, log_callback):
    movidos = 0
    ignorados = 0

    if not os.path.isdir(pasta_download):
        log_callback(f" Pasta de origem não encontrada: {pasta_download}")
        return movidos, ignorados
    
    for arquivo in os.listdir(pasta_download):
        caminho_completo = os.path.join(pasta_download, arquivo)
        
        if not os.path.isfile(caminho_completo):
            log_callback(f"Arquivo não encontrado: {arquivo}")
            continue

        _, ext = os.path.splitext(arquivo)

        for pasta, extensoes in mapeamento.items():
            if ext.lower() in extensoes:
                pasta_final = os.path.join(pasta_destino, pasta)
                os.makedirs(pasta_final, exist_ok=True)

                destino_arquivo = os.path.join(pasta_final, arquivo)
                    
                if os.path.exists(destino_arquivo):
                    base, extensao = os.path.splitext(arquivo)
                    destino_arquivo = os.path.join(pasta_final, f"{base}_copia{extensao}")

                shutil.move(caminho_completo, destino_arquivo)
                log_callback(f"Movido: {arquivo} → {pasta}")
                movidos += 1
                break
        else:
            log_callback(f"Ignorado (extensão desconhecida): {arquivo}")
            ignorados += 1

    return movidos, ignorados
    
def remover_duplicatas(pasta, log_callback):
    hashes_vistos = {}  # hash -> caminho do primeiro arquivo encontrado
    removidos = 0

    if not os.path.isdir(pasta):
        log_callback(f"Pasta não encontrada: {pasta}")
        return removidos

    for raiz, _, arquivos in os.walk(pasta):
        for nome_arquivo in arquivos:
            caminho_completo = os.path.join(raiz, nome_arquivo)

            try:
                hash_arquivo = calcular_hash(caminho_completo)
            except (OSError, PermissionError) as e:
                log_callback(f"Erro ao ler {nome_arquivo}: {e}")
                continue

            if hash_arquivo in hashes_vistos:
                original = hashes_vistos[hash_arquivo]
                os.remove(caminho_completo)
                log_callback(f"Duplicata removida: {caminho_completo} (igual a {original})")
                removidos += 1
            else:
                hashes_vistos[hash_arquivo] = caminho_completo

    log_callback(f"Total de duplicatas removidas: {removidos}")
    return removidos

def remover_pastas_duplas():
    pass
