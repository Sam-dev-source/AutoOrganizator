import threading
import tkinter as tk
import os
from tkinter import filedialog, scrolledtext, messagebox
from tkinter import ttk
from AutoOrgPORTABLE_VERSION import encontrar_pasta, encontrar_pasta, organizar, remover_duplicatas, MAPEAMENTO_PADRAO, criar_pastas_necessarias


class OrganizadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Organizador de Arquivos")
        self.root.geometry("700x520")
        self.root.minsize(600, 450)
 
        self.pasta_origem = tk.StringVar(value=encontrar_pasta(["Downloads", "downloads"]))
        self.pasta_destino = tk.StringVar(value=encontrar_pasta(["Downloads", "downloads"]))
 
        self._montar_layout()
 
    # -- construção da UI ---------------------------------------------------
 
    def _montar_layout(self):
        padding = {"padx": 10, "pady": 6}
 
        frame_pastas = ttk.LabelFrame(self.root, text="Pastas")
        frame_pastas.pack(fill="x", **padding)
 
        self._linha_pasta(frame_pastas, "Origem (Downloads):", self.pasta_origem)
        self._linha_pasta(frame_pastas, "Destino:", self.pasta_destino)
 
        frame_botoes = ttk.Frame(self.root)
        frame_botoes.pack(fill="x", **padding)
 
        self.btn_organizar = ttk.Button(
            frame_botoes, text="Organizar arquivos", command=self.executar_organizar
        )
        self.btn_organizar.pack(side="left", padx=5)
 
        self.btn_duplicatas = ttk.Button(
            frame_botoes, text="Remover duplicatas", command=self.executar_remover_duplicatas
        )
        self.btn_duplicatas.pack(side="left", padx=5)
 
        self.btn_ambos = ttk.Button(
            frame_botoes, text="Organizar + Remover duplicatas", command=self.executar_ambos
        )
        self.btn_ambos.pack(side="left", padx=5)
        
        self.btn_criar_pastas = ttk.Button(
        frame_botoes, text="Criar pastas necessárias", command=self.executar_criar_pastas
        )
        self.btn_criar_pastas.pack(side="left", padx=5)
 
        self.progress = ttk.Progressbar(self.root, mode="indeterminate")
        self.progress.pack(fill="x", padx=10, pady=(0, 6))
 
        frame_log = ttk.LabelFrame(self.root, text="Log")
        frame_log.pack(fill="both", expand=True, **padding)
 
        self.log_text = scrolledtext.ScrolledText(frame_log, state="disabled", wrap="word")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
 
        self.status_var = tk.StringVar(value="Pronto.")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, anchor="w", relief="sunken")
        status_bar.pack(fill="x", side="bottom")
 
    def _linha_pasta(self, parent, rotulo, variavel):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", padx=5, pady=4)
 
        ttk.Label(frame, text=rotulo, width=20).pack(side="left")
        entry = ttk.Entry(frame, textvariable=variavel)
        entry.pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(frame, text="Escolher...", command=lambda: self._escolher_pasta(variavel)).pack(side="left")
 
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
