import threading
import tkinter as tk
import os
from tkinter import filedialog, scrolledtext, messagebox
from tkinter import ttk
from AutoReCleanerPORTABLE_VERSION import encontrar_pasta, encontrar_pasta, organizar, remover_duplicatas, MAPEAMENTO_PADRAO, criar_pastas_necessarias, calcular_hash

import base64

# Ícone do app (PNG 64x64 embutido em base64 -- logo AutoReCleaner)
ICONE_APP_B64 = (
    "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"
)


# ---------------------------------------------------------------------------
# Paleta de cores
# ---------------------------------------------------------------------------
COR_FUNDO = "#0f1b2d"          # azul bem escuro (fundo geral)
COR_FUNDO_PAINEL = "#16273f"   # azul escuro (painéis/labelframes)
COR_FUNDO_LOG = "#0b1626"      # azul quase preto (área de log)
COR_TEXTO = "#e6eefc"          # texto claro
COR_TEXTO_SECUNDARIO = "#9db4d6"
COR_AZUL_PRIMARIO = "#2f6fed"  # azul vibrante (botões principais)
COR_AZUL_PRIMARIO_HOVER = "#4c86ff"
COR_AZUL_ESCURO = "#1c3a63"    # bordas/entradas
COR_ACENTO = "#5ad1ff"         # azul claro de destaque (barra de progresso, foco)
COR_SUCESSO = "#3ddc97"


class OrganizadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoReCleaner")
        self.root.geometry("740x560")
        self.root.minsize(640, 480)
        self.root.configure(bg=COR_FUNDO)

        self.pasta_origem = tk.StringVar(value=encontrar_pasta(["Downloads", "downloads"]))
        self.pasta_destino = tk.StringVar(value=encontrar_pasta(["Downloads", "downloads"]))

        self._carregar_icone()
        self._configurar_estilos()
        self._montar_layout()

    # -- ícone do app ---------------------------------------------------

    def _carregar_icone(self):
        """Carrega o logo (embutido em base64) e aplica como ícone da janela."""
        try:
            dados_png = base64.b64decode(ICONE_APP_B64)
            self.icone_img = tk.PhotoImage(data=dados_png)
            self.root.iconphoto(True, self.icone_img)
            # Versão menor para usar dentro do cabeçalho da interface
            self.icone_pequeno = self.icone_img.subsample(2, 2)
        except Exception:
            # Se algo falhar na decodificação, a interface continua funcionando sem o ícone
            self.icone_img = None
            self.icone_pequeno = None

    # -- estilos (tema azul) -------------------------------------------------

    def _configurar_estilos(self):
        style = ttk.Style(self.root)
        # 'clam' é o único tema nativo que aceita customização de cores de forma consistente
        style.theme_use("clam")

        fonte_base = ("Segoe UI", 10)
        fonte_titulo = ("Segoe UI Semibold", 10)
        fonte_status = ("Segoe UI", 9)

        # Frame / LabelFrame
        style.configure("TFrame", background=COR_FUNDO)
        style.configure(
            "TLabelframe",
            background=COR_FUNDO_PAINEL,
            bordercolor=COR_AZUL_ESCURO,
            relief="solid",
            borderwidth=1,
        )
        style.configure(
            "TLabelframe.Label",
            background=COR_FUNDO_PAINEL,
            foreground=COR_ACENTO,
            font=fonte_titulo,
        )

        # Labels
        style.configure("TLabel", background=COR_FUNDO_PAINEL, foreground=COR_TEXTO, font=fonte_base)
        style.configure("Status.TLabel", background=COR_AZUL_ESCURO, foreground=COR_TEXTO_SECUNDARIO, font=fonte_status)

        # Entradas
        style.configure(
            "TEntry",
            fieldbackground=COR_FUNDO_LOG,
            background=COR_FUNDO_LOG,
            foreground=COR_TEXTO,
            bordercolor=COR_AZUL_ESCURO,
            insertcolor=COR_TEXTO,
            relief="flat",
            padding=6,
        )
        style.map(
            "TEntry",
            bordercolor=[("focus", COR_ACENTO)],
            lightcolor=[("focus", COR_ACENTO)],
        )

        # Botões principais (azul cheio)
        style.configure(
            "Azul.TButton",
            background=COR_AZUL_PRIMARIO,
            foreground="white",
            font=fonte_titulo,
            padding=(14, 8),
            borderwidth=0,
            relief="flat",
        )
        style.map(
            "Azul.TButton",
            background=[("active", COR_AZUL_PRIMARIO_HOVER), ("disabled", COR_AZUL_ESCURO)],
            foreground=[("disabled", COR_TEXTO_SECUNDARIO)],
        )

        # Botão secundário (contorno)
        style.configure(
            "Secundario.TButton",
            background=COR_FUNDO_PAINEL,
            foreground=COR_ACENTO,
            font=fonte_base,
            padding=(12, 7),
            borderwidth=1,
            relief="solid",
        )
        style.map(
            "Secundario.TButton",
            background=[("active", COR_AZUL_ESCURO)],
            bordercolor=[("!disabled", COR_AZUL_ESCURO)],
        )

        # Botão "Escolher..." pequeno
        style.configure(
            "Escolher.TButton",
            background=COR_AZUL_ESCURO,
            foreground=COR_TEXTO,
            font=fonte_status,
            padding=(8, 4),
            borderwidth=0,
        )
        style.map("Escolher.TButton", background=[("active", COR_AZUL_PRIMARIO)])

        # Barra de progresso
        style.configure(
            "Azul.Horizontal.TProgressbar",
            troughcolor=COR_FUNDO_LOG,
            background=COR_ACENTO,
            bordercolor=COR_FUNDO_LOG,
            lightcolor=COR_ACENTO,
            darkcolor=COR_ACENTO,
            thickness=8,
        )

    # -- construção da UI ---------------------------------------------------

    def _montar_layout(self):
        padding = {"padx": 14, "pady": 8}

        # Cabeçalho
        cabecalho = ttk.Frame(self.root, style="TFrame")
        cabecalho.pack(fill="x", padx=14, pady=(14, 0))

        if self.icone_pequeno is not None:
            lbl_icone = tk.Label(cabecalho, image=self.icone_pequeno, bg=COR_FUNDO)
            lbl_icone.pack(side="left", padx=(0, 10))

        bloco_titulo = tk.Frame(cabecalho, bg=COR_FUNDO)
        bloco_titulo.pack(side="left")

        titulo = tk.Label(
            bloco_titulo,
            text="AutoReCleaner",
            bg=COR_FUNDO,
            fg=COR_TEXTO,
            font=("Segoe UI Semibold", 18),
        )
        titulo.pack(anchor="w")
        subtitulo = tk.Label(
            bloco_titulo,
            text="Organize e limpe seus arquivos automaticamente",
            bg=COR_FUNDO,
            fg=COR_TEXTO_SECUNDARIO,
            font=("Segoe UI", 9),
        )
        subtitulo.pack(anchor="w")

        frame_pastas = ttk.LabelFrame(self.root, text="  Pastas  ")
        frame_pastas.pack(fill="x", **padding)

        self._linha_pasta(frame_pastas, "Origem (Downloads):", self.pasta_origem)
        self._linha_pasta(frame_pastas, "Destino:", self.pasta_destino)

        frame_botoes = ttk.Frame(self.root, style="TFrame")
        frame_botoes.pack(fill="x", **padding)

        self.btn_organizar = ttk.Button(
            frame_botoes, text="📂 Organizar arquivos", style="Azul.TButton", command=self.executar_organizar
        )
        self.btn_organizar.pack(side="left", padx=(0, 8))

        self.btn_duplicatas = ttk.Button(
            frame_botoes, text="🗑 Remover duplicatas", style="Secundario.TButton", command=self.executar_remover_duplicatas
        )
        self.btn_duplicatas.pack(side="left", padx=8)

        self.btn_ambos = ttk.Button(
            frame_botoes, text="✨ Organizar + Duplicatas", style="Azul.TButton", command=self.executar_ambos
        )
        self.btn_ambos.pack(side="left", padx=8)

        self.btn_criar_pastas = ttk.Button(
            frame_botoes, text="📁 Criar pastas necessárias", style="Secundario.TButton", command=self.executar_criar_pastas
        )
        self.btn_criar_pastas.pack(side="left", padx=8)

        self.progress = ttk.Progressbar(self.root, mode="indeterminate", style="Azul.Horizontal.TProgressbar")
        self.progress.pack(fill="x", padx=14, pady=(2, 10))

        frame_log = ttk.LabelFrame(self.root, text="  Log  ")
        frame_log.pack(fill="both", expand=True, **padding)

        self.log_text = scrolledtext.ScrolledText(
            frame_log,
            state="disabled",
            wrap="word",
            bg=COR_FUNDO_LOG,
            fg=COR_TEXTO,
            insertbackground=COR_TEXTO,
            relief="flat",
            borderwidth=0,
            font=("Consolas", 10),
            padx=8,
            pady=8,
        )
        self.log_text.pack(fill="both", expand=True, padx=6, pady=6)

        self.status_var = tk.StringVar(value="Pronto.")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, anchor="w", style="Status.TLabel", padding=(10, 6))
        status_bar.pack(fill="x", side="bottom")

    def _linha_pasta(self, parent, rotulo, variavel):
        frame = ttk.Frame(parent, style="TFrame")
        frame.configure(style="TFrame")
        # força o fundo do frame interno a acompanhar o LabelFrame
        frame_tk = tk.Frame(parent, bg=COR_FUNDO_PAINEL)
        frame_tk.pack(fill="x", padx=8, pady=6)

        tk.Label(
            frame_tk, text=rotulo, width=20, anchor="w",
            bg=COR_FUNDO_PAINEL, fg=COR_TEXTO_SECUNDARIO, font=("Segoe UI", 10),
        ).pack(side="left")
        entry = ttk.Entry(frame_tk, textvariable=variavel)
        entry.pack(side="left", fill="x", expand=True, padx=8)
        ttk.Button(
            frame_tk, text="Escolher...", style="Escolher.TButton",
            command=lambda: self._escolher_pasta(variavel)
        ).pack(side="left")

    def _escolher_pasta(self, variavel):
        caminho = filedialog.askdirectory(initialdir=variavel.get() or os.path.expanduser("~"))
        if caminho:
            variavel.set(caminho)

    # -- log e status ---------------------------------------------------

    def log(self, mensagem):
        """Thread-safe: agenda a escrita no widget de log na thread principal."""
        self.root.after(0, self._escrever_log, mensagem)

    def _escrever_log(self, mensagem):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", mensagem + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def set_status(self, texto):
        self.root.after(0, self.status_var.set, texto)

    # -- controle de botões / progresso ---------------------------------

    def _travar_botoes(self, travado: bool):
        estado = "disabled" if travado else "normal"
        self.btn_organizar.configure(state=estado)
        self.btn_duplicatas.configure(state=estado)
        self.btn_ambos.configure(state=estado)
        self.btn_criar_pastas.configure(state=estado)
        if travado:
            self.progress.start(10)
        else:
            self.progress.stop()

    # -- ações (rodam em thread separada para não travar a janela) ------

    def executar_organizar(self):
        self._rodar_em_thread(self._tarefa_organizar)

    def executar_remover_duplicatas(self):
        self._rodar_em_thread(self._tarefa_remover_duplicatas)

    def executar_ambos(self):
        self._rodar_em_thread(self._tarefa_ambos)

    def _rodar_em_thread(self, tarefa):
        origem = self.pasta_origem.get().strip()
        destino = self.pasta_destino.get().strip()

        if not origem or not destino:
            messagebox.showwarning("Atenção", "Selecione as pastas de origem e destino.")
            return

        self._travar_botoes(True)
        thread = threading.Thread(target=tarefa, args=(origem, destino), daemon=True)
        thread.start()

    def _tarefa_organizar(self, origem, destino):
        try:
            self.set_status("Organizando arquivos...")
            movidos, ignorados = organizar(origem, destino, MAPEAMENTO_PADRAO, self.log)
            self.log(f"\nConcluído: {movidos} movidos, {ignorados} ignorados.")
            self.set_status(f"Concluído: {movidos} movidos, {ignorados} ignorados.")
        except Exception as e:
            self.log(f"Erro inesperado: {e}")
            self.set_status("Erro durante a organização.")
        finally:
            self.root.after(0, self._travar_botoes, False)

    def _tarefa_remover_duplicatas(self, origem, destino):
        try:
            self.set_status("Procurando duplicatas...")
            removidos = remover_duplicatas(destino, self.log)
            self.set_status(f"Concluído: {removidos} duplicatas removidas.")
        except Exception as e:
            self.log(f"Erro inesperado: {e}")
            self.set_status("Erro ao remover duplicatas.")
        finally:
            self.root.after(0, self._travar_botoes, False)

    def _tarefa_ambos(self, origem, destino):
        try:
            self.set_status("Organizando arquivos...")
            movidos, ignorados = organizar(origem, destino, MAPEAMENTO_PADRAO, self.log)
            self.log(f"\nOrganização concluída: {movidos} movidos, {ignorados} ignorados.\n")

            self.set_status("Procurando duplicatas...")
            removidos = remover_duplicatas(destino, self.log)

            self.set_status(
                f"Concluído: {movidos} movidos, {ignorados} ignorados, {removidos} duplicatas removidas."
            )
        except Exception as e:
            self.log(f"Erro inesperado: {e}")
            self.set_status("Erro durante a execução.")
        finally:
            self.root.after(0, self._travar_botoes, False)

    def executar_criar_pastas(self):
        destino = self.pasta_destino.get().strip()
        if not destino:
            messagebox.showwarning("Atenção", "Selecione a pasta de destino.")
            return

        self._travar_botoes(True)
        thread = threading.Thread(target=self._tarefa_criar_pastas, args=(destino,), daemon=True)
        thread.start()

    def _tarefa_criar_pastas(self, destino):
        try:
            self.set_status("Criando pastas necessárias...")
            criadas = criar_pastas_necessarias(destino, MAPEAMENTO_PADRAO, self.log)
            if criadas:
                self.log(f"\n{len(criadas)} pasta(s) criada(s).")
                self.set_status(f"Concluído: {len(criadas)} pasta(s) criada(s).")
            else:
                self.log("\nTodas as pastas já existiam.")
                self.set_status("Todas as pastas já existiam.")
        except Exception as e:
            self.log(f"Erro inesperado: {e}")
            self.set_status("Erro ao criar pastas.")
        finally:
            self.root.after(0, self._travar_botoes, False)
