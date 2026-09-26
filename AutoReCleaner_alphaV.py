import os
import shutil
import hashlib
import json
from watchdog.observers import Observer 
from watchdog.events import FileSystemEventHandler
import time


MAPEAMENTO_PADRAO = {
        "Imagens":     [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"],
        "Documentos":  [".html", ".txt", ".pdf"],
        "Videos":      [".mp4", ".mkv", ".avi", ".mov"],
        "Musicas":     [".mp3", ".wav", ".flac", ".ogg"],
        "Apps ou Executáveis": [".deb", ".sh", ".rpm", ".py", ".cs", ".css", ".json", ".exe", ".apk", ".elf", ".bin", ".bat", ".msi", ".exe"],
        "Word":   [".docx", ".dotx", ".docm", ".odt"],
        "Excel": [".xlsx", ".xlsm", ".xlsb", ".xltx", ".csv"],
        "PowerPoint": [".pptx", ".ppsx", ".potx", ".pptm"]
    }   

CAMINHO_REGRAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "regras_personalizadas.json")

CAMPOS_DISPONIVEIS = ["extensao", "nome", "tamanho_mb"]

OPERADORES_POR_CAMPO = {
    "extensao": ["igual", "diferente"],
    "nome": ["contém", "não contém", "começa com", "termina com"],
    "tamanho_mb": ["maior que", "menor que"],
}

def carregar_regras():
    if not os.path.exists(CAMINHO_REGRAS):
        return[]
    try:
        with open(CAMINHO_REGRAS, "r", encoding="utf-8") as f:
            return json.load(f)
        
    except Exception:
        return []
    
def salvar_regras(regras):
    with open(CAMINHO_REGRAS, "w", encoding="utf-8") as f:
        json.dump(regras, f, ensure_ascii=False, ident=2)
        
        
def arquivo_bate_condicao(caminho_arquivo, condicao):
    """Avalia uma condição isolada, ex: {'campo': 'extensao', 'operador': 'igual', 'valor': 'pdf'}"""
    nome = os.path.basename(caminho_arquivo)
    _, ext = os.path.splitext(nome)
    ext = ext.lower().lstrip(".")   
 
    campo = condicao["campo"]
    operador = condicao["operador"]
    valor = condicao["valor"]
 
    if campo == "extensao":
        valor_norm = valor.lower().lstrip(".")
        if operador == "igual":
            return ext == valor_norm
        if operador == "diferente":
            return ext != valor_norm
 
    elif campo == "nome":
        nome_lower = nome.lower()
        valor_lower = valor.lower()
        if operador == "contém":
            return valor_lower in nome_lower
        if operador == "não contém":
            return valor_lower not in nome_lower
        if operador == "começa com":
            return nome_lower.startswith(valor_lower)
        if operador == "termina com":
            return nome_lower.endswith(valor_lower)
 
    elif campo == "tamanho_mb":
        try:
            valor_num = float(valor)
            tamanho_mb = os.path.getsize(caminho_arquivo) / (1024 * 1024)
        except (ValueError, OSError):
            return False
        
        if operador == "maior que":
            return tamanho_mb > valor_num
        
        if operador == "menor que":
            return tamanho_mb < valor_num
 
    return False
 
 
def arquivo_bate_regra(caminho_arquivo, regra):
    """Uma regra tem 'condicoes' (lista) e 'modo' ('todas' = E, 'qualquer' = OU)."""
    condicoes = regra.get("condicoes", [])
    if not condicoes:
        return False
 
    modo = regra.get("modo", "todas")
    resultados = [arquivo_bate_condicao(caminho_arquivo, c) for c in condicoes]
 
    if modo == "todas":
        return all(resultados)
    else:
        return any(resultados)
 
 
def _caminho_unico_copia(pasta_final, arquivo):
    """Mesmo padrão de nomeação usado em organizar(): sufixo '_copia' em caso de conflito."""
    destino_arquivo = os.path.join(pasta_final, arquivo)
    if os.path.exists(destino_arquivo):
        base, extensao = os.path.splitext(arquivo)
        destino_arquivo = os.path.join(pasta_final, f"{base}_copia{extensao}")
    return destino_arquivo
 
 
def aplicar_regras_personalizadas(pasta_download, pasta_destino, regras, log_callback, apenas_simular=False):
    """Percorre os arquivos da origem e move o primeiro que bater com cada regra ativa, na ordem definida."""
    movidos = 0
    ignorados = 0
 
    if not os.path.isdir(pasta_download):
        log_callback(f"Pasta de origem não encontrada: {pasta_download}")
        return movidos, ignorados
 
    regras_ativas = [r for r in regras if r.get("ativa", True)]
    if not regras_ativas:
        log_callback("Nenhuma regra ativa.")
        return movidos, ignorados
 
    for arquivo in os.listdir(pasta_download):
        caminho_completo = os.path.join(pasta_download, arquivo)
        if not os.path.isfile(caminho_completo):
            continue
 
        for regra in regras_ativas:
            if arquivo_bate_regra(caminho_completo, regra):
                pasta_final = os.path.join(pasta_destino, regra["pasta_destino"])
 
                if apenas_simular:
                    log_callback(f"[TESTE] {arquivo} seria movido para {regra['pasta_destino']}")
                    movidos += 1
                    break
 
                os.makedirs(pasta_final, exist_ok=True)
                destino_arquivo = _caminho_unico_copia(pasta_final, arquivo)
 
                shutil.move(caminho_completo, destino_arquivo)
                log_callback(f"Movido (regra): {arquivo} → {regra['pasta_destino']}")
                movidos += 1
                break
        else:
            ignorados += 1
 
    return movidos, ignorados

#Monitoramento em tempo real com watchdog, Ela fica de olho na pasta e roda assim que um arquivo novo chega, sem clicar em nada!
class MonitorHandler(FileSystemEventHandler):
    def __init__(self, pasta_destino, obter_regras, log_callback):
        self.pasta_destino = pasta_destino
        self.obter_regras = obter_regras  # função, pra sempre pegar a lista atualizada
        self.log_callback = log_callback
 
    def on_created(self, event):
        if event.is_directory:
            return
        # pequena espera pra garantir que o arquivo terminou de ser escrito/baixado
        time.sleep(1)
        pasta_origem = os.path.dirname(event.src_path)
        aplicar_regras_personalizadas(pasta_origem, self.pasta_destino, self.obter_regras(), self.log_callback)
 
 
def iniciar_monitoramento(pasta_origem, pasta_destino, obter_regras, log_callback):
    handler = MonitorHandler(pasta_destino, obter_regras, log_callback)
    observer = Observer()
    observer.schedule(handler, pasta_origem, recursive=False)
    observer.start()
    return observer

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
