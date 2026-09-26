import threading
import tkinter as tk
import os
from tkinter import filedialog, scrolledtext, messagebox
from tkinter import ttk
from AutoReCleaner import (
    encontrar_pasta,
    organizar,
    remover_duplicatas,
    MAPEAMENTO_PADRAO,
    criar_pastas_necessarias,
    carregar_regras,
    salvar_regras,
    aplicar_regras_personalizadas,
    iniciar_monitoramento,
    CAMPOS_DISPONIVEIS,
    OPERADORES_POR_CAMPO,
)

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


# ---------------------------------------------------------------------------
# Diálogo de regra: suporta múltiplas condições (E / OU), estilo File Juggler
# ---------------------------------------------------------------------------
class RegraDialog(tk.Toplevel):
    def __init__(self, parent, regra_existente=None):
        super().__init__(parent)
        self.title("Nova regra" if regra_existente is None else "Editar regra")
        self.configure(bg=COR_FUNDO_PAINEL)
        self.resizable(False, False)
        self.resultado = None
        self.linhas_condicao = []  # cada item: dict com vars + frame
        self.transient(parent)
        self.grab_set()

        pad = {"padx": 10, "pady": 6}

        tk.Label(
            self, text="Se o arquivo bater com estas condições:",
            bg=COR_FUNDO_PAINEL, fg=COR_TEXTO, font=("Segoe UI Semibold", 10),
        ).grid(row=0, column=0, columnspan=3, sticky="w", **pad)

        tk.Label(self, text="Modo:", bg=COR_FUNDO_PAINEL, fg=COR_TEXTO_SECUNDARIO).grid(
            row=1, column=0, sticky="w", padx=10
        )
        self.var_modo = tk.StringVar(value="todas")
        frame_modo = tk.Frame(self, bg=COR_FUNDO_PAINEL)
        frame_modo.grid(row=1, column=1, columnspan=2, sticky="w")
        tk.Radiobutton(
            frame_modo, text="Todas as condições (E)", variable=self.var_modo, value="todas",
            bg=COR_FUNDO_PAINEL, fg=COR_TEXTO, selectcolor=COR_FUNDO_LOG, activebackground=COR_FUNDO_PAINEL,
        ).pack(side="left", padx=4)
        tk.Radiobutton(
            frame_modo, text="Qualquer uma (OU)", variable=self.var_modo, value="qualquer",
            bg=COR_FUNDO_PAINEL, fg=COR_TEXTO, selectcolor=COR_FUNDO_LOG, activebackground=COR_FUNDO_PAINEL,
        ).pack(side="left", padx=4)

        self.frame_condicoes = tk.Frame(self, bg=COR_FUNDO_PAINEL)
        self.frame_condicoes.grid(row=2, column=0, columnspan=3, sticky="w", padx=10, pady=(4, 4))

        ttk.Button(
            self, text="+ Adicionar condição", style="Secundario.TButton", command=self._adicionar_linha_condicao
        ).grid(row=3, column=0, columnspan=3, sticky="w", padx=10, pady=(0, 8))

        tk.Label(
            self, text="Mover para a subpasta:", bg=COR_FUNDO_PAINEL, fg=COR_TEXTO, font=("Segoe UI Semibold", 10),
        ).grid(row=4, column=0, columnspan=2, sticky="w", **pad)
        self.var_pasta = tk.StringVar()
        tk.Entry(self, textvariable=self.var_pasta, width=24).grid(row=5, column=0, columnspan=3, sticky="w", padx=10)

        self.var_ativa = tk.BooleanVar(value=True)
        tk.Checkbutton(
            self, text="Regra ativa", variable=self.var_ativa,
            bg=COR_FUNDO_PAINEL, fg=COR_TEXTO, selectcolor=COR_FUNDO_LOG, activebackground=COR_FUNDO_PAINEL,
        ).grid(row=6, column=0, columnspan=2, sticky="w", padx=10, pady=(8, 0))

        frame_botoes = tk.Frame(self, bg=COR_FUNDO_PAINEL)
        frame_botoes.grid(row=7, column=0, columnspan=3, pady=12)
        ttk.Button(frame_botoes, text="Salvar", style="Azul.TButton", command=self._salvar).pack(side="left", padx=6)
        ttk.Button(frame_botoes, text="Cancelar", style="Secundario.TButton", command=self.destroy).pack(side="left", padx=6)

        if regra_existente:
            self.var_modo.set(regra_existente.get("modo", "todas"))
            self.var_pasta.set(regra_existente.get("pasta_destino", ""))
            self.var_ativa.set(regra_existente.get("ativa", True))
            for condicao in regra_existente.get("condicoes", []):
                self._adicionar_linha_condicao(condicao)
        else:
            self._adicionar_linha_condicao()

    def _adicionar_linha_condicao(self, condicao_existente=None):
        linha = tk.Frame(self.frame_condicoes, bg=COR_FUNDO_PAINEL)
        linha.pack(fill="x", pady=2)

        var_campo = tk.StringVar(value=(condicao_existente or {}).get("campo", CAMPOS_DISPONIVEIS[0]))
        combo_campo = ttk.Combobox(linha, textvariable=var_campo, values=CAMPOS_DISPONIVEIS, state="readonly", width=12)
        combo_campo.pack(side="left", padx=3)

        var_operador = tk.StringVar()
        combo_operador = ttk.Combobox(linha, textvariable=var_operador, state="readonly", width=13)
        combo_operador.pack(side="left", padx=3)

        var_valor = tk.StringVar(value=(condicao_existente or {}).get("valor", ""))
        tk.Entry(linha, textvariable=var_valor, width=14).pack(side="left", padx=3)

        def atualizar_operadores(event=None, cc=condicao_existente):
            opcoes = OPERADORES_POR_CAMPO[var_campo.get()]
            combo_operador["values"] = opcoes
            valor_atual = (cc or {}).get("operador")
            if valor_atual in opcoes:
                var_operador.set(valor_atual)
            elif var_operador.get() not in opcoes:
                var_operador.set(opcoes[0])

        combo_campo.bind("<<ComboboxSelected>>", atualizar_operadores)
        atualizar_operadores()

        info = {"frame": linha, "campo": var_campo, "operador": var_operador, "valor": var_valor}

        def remover():
            self.linhas_condicao.remove(info)
            linha.destroy()

        ttk.Button(linha, text="✕", style="Escolher.TButton", width=3, command=remover).pack(side="left", padx=3)

        self.linhas_condicao.append(info)

    def _salvar(self):
        pasta = self.var_pasta.get().strip()
        if not pasta:
            messagebox.showwarning("Atenção", "Informe a subpasta de destino.", parent=self)
            return
        if not self.linhas_condicao:
            messagebox.showwarning("Atenção", "Adicione pelo menos uma condição.", parent=self)
            return

        condicoes = []
        for info in self.linhas_condicao:
            valor = info["valor"].get().strip()
            if not valor:
                messagebox.showwarning("Atenção", "Preencha o valor de todas as condições.", parent=self)
                return
            condicoes.append({
                "campo": info["campo"].get(),
                "operador": info["operador"].get(),
                "valor": valor,
            })

        self.resultado = {
            "ativa": self.var_ativa.get(),
            "modo": self.var_modo.get(),
            "condicoes": condicoes,
            "pasta_destino": pasta,
        }
        self.destroy()


class OrganizadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoReCleaner")
        self.root.geometry("820x680")
        self.root.minsize(700, 560)
        self.root.configure(bg=COR_FUNDO)
        self.root.protocol("WM_DELETE_WINDOW", self._ao_fechar)

        self.pasta_origem = tk.StringVar(value=encontrar_pasta(["Downloads", "downloads"]))
        self.pasta_destino = tk.StringVar(value=encontrar_pasta(["Downloads", "downloads"]))

        self.regras = carregar_regras()
        self.observer = None  # referência do watchdog.Observer quando o monitoramento estiver ativo
        self.var_teste = tk.BooleanVar(value=False)

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

        # Botão de monitoramento (verde quando ativo)
        style.configure(
            "Monitorar.TButton",
            background=COR_SUCESSO,
            foreground="#0b1626",
            font=fonte_titulo,
            padding=(14, 8),
            borderwidth=0,
        )
        style.map("Monitorar.TButton", background=[("active", "#31c085")])

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

        # Treeview (lista de regras)
        style.configure(
            "Treeview",
            background=COR_FUNDO_LOG,
            fieldbackground=COR_FUNDO_LOG,
            foreground=COR_TEXTO,
            rowheight=24,
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background=COR_AZUL_ESCURO,
            foreground=COR_ACENTO,
            font=fonte_status,
            relief="flat",
        )
        style.map("Treeview", background=[("selected", COR_AZUL_PRIMARIO)])

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

        # -- Painel de regras personalizadas (estilo File Juggler) --
        frame_regras = ttk.LabelFrame(self.root, text="  Regras Personalizadas  ")
        frame_regras.pack(fill="x", **padding)

        colunas = ("ativa", "condicao", "pasta")
        self.tree_regras = ttk.Treeview(frame_regras, columns=colunas, show="headings", height=5)
        self.tree_regras.heading("ativa", text="✔")
        self.tree_regras.heading("condicao", text="Condição")
        self.tree_regras.heading("pasta", text="Pasta de destino")
        self.tree_regras.column("ativa", width=30, anchor="center")
        self.tree_regras.column("condicao", width=380)
        self.tree_regras.column("pasta", width=150)
        self.tree_regras.pack(side="left", fill="x", expand=True, padx=8, pady=8)
        self.tree_regras.bind("<Button-1>", self._alternar_ativa)

        frame_botoes_regras = tk.Frame(frame_regras, bg=COR_FUNDO_PAINEL)
        frame_botoes_regras.pack(side="left", padx=8, fill="y")

        ttk.Button(frame_botoes_regras, text="➕ Adicionar", style="Secundario.TButton",
                   command=self._adicionar_regra).pack(fill="x", pady=2)
        ttk.Button(frame_botoes_regras, text="✏ Editar", style="Secundario.TButton",
                   command=self._editar_regra).pack(fill="x", pady=2)
        ttk.Button(frame_botoes_regras, text="🗑 Remover", style="Secundario.TButton",
                   command=self._remover_regra).pack(fill="x", pady=2)

        frame_reordenar = tk.Frame(frame_botoes_regras, bg=COR_FUNDO_PAINEL)
        frame_reordenar.pack(fill="x", pady=(4, 2))
        ttk.Button(frame_reordenar, text="▲", style="Secundario.TButton",
                   command=lambda: self._mover_regra(-1)).pack(side="left", expand=True, fill="x")
        ttk.Button(frame_reordenar, text="▼", style="Secundario.TButton",
                   command=lambda: self._mover_regra(1)).pack(side="left", expand=True, fill="x")

        tk.Checkbutton(
            frame_botoes_regras, text="Modo teste", variable=self.var_teste,
            bg=COR_FUNDO_PAINEL, fg=COR_TEXTO_SECUNDARIO, selectcolor=COR_FUNDO_LOG,
            activebackground=COR_FUNDO_PAINEL, font=("Segoe UI", 9),
        ).pack(fill="x", pady=(8, 2))

        self.btn_aplicar_regras = ttk.Button(
            frame_botoes_regras, text="▶ Aplicar regras", style="Azul.TButton",
            command=self.executar_regras_personalizadas
        )
        self.btn_aplicar_regras.pack(fill="x", pady=2)

        self.btn_monitorar = ttk.Button(
            frame_botoes_regras, text="👁 Ativar monitoramento", style="Monitorar.TButton",
            command=self._alternar_monitoramento
        )
        self.btn_monitorar.pack(fill="x", pady=(8, 2))

        self._atualizar_lista_regras()

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
        self.btn_aplicar_regras.configure(state=estado)
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

    # -- regras personalizadas -------------------------------------------

    def _atualizar_lista_regras(self):
        self.tree_regras.delete(*self.tree_regras.get_children())
        for i, regra in enumerate(self.regras):
            ativa = "✔" if regra.get("ativa", True) else "✘"
            conector = " E " if regra.get("modo", "todas") == "todas" else " OU "
            condicao_txt = conector.join(
                f'{c["campo"]} {c["operador"]} "{c["valor"]}"' for c in regra.get("condicoes", [])
            )
            self.tree_regras.insert("", "end", iid=str(i), values=(ativa, condicao_txt, regra["pasta_destino"]))

    def _alternar_ativa(self, event):
        item = self.tree_regras.identify_row(event.y)
        coluna = self.tree_regras.identify_column(event.x)
        if not item or coluna != "#1":  # coluna "ativa"
            return
        indice = int(item)
        self.regras[indice]["ativa"] = not self.regras[indice].get("ativa", True)
        salvar_regras(self.regras)
        self._atualizar_lista_regras()

    def _adicionar_regra(self):
        dialog = RegraDialog(self.root)
        self.root.wait_window(dialog)
        if dialog.resultado:
            self.regras.append(dialog.resultado)
            salvar_regras(self.regras)
            self._atualizar_lista_regras()

    def _editar_regra(self):
        selecionado = self.tree_regras.selection()
        if not selecionado:
            messagebox.showinfo("Info", "Selecione uma regra para editar.")
            return
        indice = int(selecionado[0])
        dialog = RegraDialog(self.root, regra_existente=self.regras[indice])
        self.root.wait_window(dialog)
        if dialog.resultado:
            self.regras[indice] = dialog.resultado
            salvar_regras(self.regras)
            self._atualizar_lista_regras()

    def _remover_regra(self):
        selecionado = self.tree_regras.selection()
        if not selecionado:
            messagebox.showinfo("Info", "Selecione uma regra para remover.")
            return
        indice = int(selecionado[0])
        del self.regras[indice]
        salvar_regras(self.regras)
        self._atualizar_lista_regras()

    def _mover_regra(self, direcao):
        selecionado = self.tree_regras.selection()
        if not selecionado:
            return
        i = int(selecionado[0])
        j = i + direcao
        if 0 <= j < len(self.regras):
            self.regras[i], self.regras[j] = self.regras[j], self.regras[i]
            salvar_regras(self.regras)
            self._atualizar_lista_regras()
            self.tree_regras.selection_set(str(j))

    def executar_regras_personalizadas(self):
        origem = self.pasta_origem.get().strip()
        destino = self.pasta_destino.get().strip()
        if not origem or not destino:
            messagebox.showwarning("Atenção", "Selecione as pastas de origem e destino.")
            return
        if not self.regras:
            messagebox.showinfo("Info", "Nenhuma regra cadastrada ainda. Clique em 'Adicionar'.")
            return

        self._travar_botoes(True)
        thread = threading.Thread(target=self._tarefa_regras_personalizadas, args=(origem, destino), daemon=True)
        thread.start()

    def _tarefa_regras_personalizadas(self, origem, destino):
        try:
            simulando = self.var_teste.get()
            self.set_status("Aplicando regras personalizadas..." if not simulando else "Simulando regras (modo teste)...")
            movidos, ignorados = aplicar_regras_personalizadas(
                origem, destino, self.regras, self.log, apenas_simular=simulando
            )
            self.log(f"\nRegras {'simuladas' if simulando else 'aplicadas'}: {movidos} arquivo(s).")
            self.set_status(f"Concluído: {movidos} arquivo(s) processado(s) pelas regras.")
        except Exception as e:
            self.log(f"Erro inesperado: {e}")
            self.set_status("Erro ao aplicar regras.")
        finally:
            self.root.after(0, self._travar_botoes, False)

    # -- monitoramento em tempo real -------------------------------------

    def _alternar_monitoramento(self):
        if self.observer is None:
            origem = self.pasta_origem.get().strip()
            destino = self.pasta_destino.get().strip()
            if not origem or not destino:
                messagebox.showwarning("Atenção", "Selecione as pastas de origem e destino.")
                return
            if not self.regras:
                messagebox.showinfo("Info", "Cadastre ao menos uma regra antes de monitorar.")
                return

            self.observer = iniciar_monitoramento(origem, destino, lambda: self.regras, self.log)
            if self.observer is None:
                # iniciar_monitoramento já loga o motivo (ex: watchdog não instalado)
                return

            self.btn_monitorar.configure(text="⏸ Parar monitoramento", style="Secundario.TButton")
            self.set_status(f"Monitorando '{origem}' em tempo real...")
            self.log(f"Monitoramento iniciado em: {origem}")
        else:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            self.btn_monitorar.configure(text="👁 Ativar monitoramento", style="Monitorar.TButton")
            self.set_status("Monitoramento parado.")
            self.log("Monitoramento parado.")

    def _ao_fechar(self):
        if self.observer is not None:
            self.observer.stop()
            self.observer.join()
        self.root.destroy()
