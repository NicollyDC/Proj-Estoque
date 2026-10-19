import tkinter as tk
from tkinter import ttk, messagebox


def criar_indicador_sync(parent, tracker):
    """Indicador local que nunca declara sincronização sem confirmação remota."""
    indicador = tk.Label(
        parent,
        text="💾 Somente local",
        bg="#FFFFFF",
        fg="#2563EB",
        font=("Segoe UI", 8, "bold"),
        anchor="w",
        cursor="hand2",
    )

    def obter_estado():
        status = tracker.status()
        state = status.state
        if state not in {"syncing", "failed"} and status.pending_count:
            state = "pending"
        if state == "synced":
            return status, state, "✓ Sincronizado", "#15803D"
        if state == "pending":
            quantidade = status.pending_count
            texto = f"● {quantidade} alteração{'ões' if quantidade != 1 else ''} pendente{'s' if quantidade != 1 else ''}"
            return status, state, texto, "#B45309"
        if state == "syncing":
            return status, state, "↻ Sincronizando...", "#2563EB"
        if state == "failed":
            return status, state, "! Falha na sincronização", "#B91C1C"
        return status, "local_only", "💾 Somente local", "#2563EB"

    def atualizar():
        if not indicador.winfo_exists():
            return
        try:
            _, _, texto, cor = obter_estado()
        except Exception:
            texto, cor = "💾 Somente local", "#2563EB"
        indicador.configure(text=texto, fg=cor)

    def mostrar_detalhes(_event=None):
        status, state, _, _ = obter_estado()
        if state == "local_only":
            detalhe = (
                "Os dados continuam salvos localmente no SQLite.\n"
                "A sincronização com a nuvem ainda não está configurada."
            )
        elif state == "pending":
            quantidade = status.pending_count
            detalhe = (
                "Os dados estão salvos localmente no SQLite.\n"
                f"{quantidade} alteração(ões) aguardando sincronização."
            )
        elif state == "synced":
            detalhe = (
                "Sincronizado com a nuvem.\n"
                f"Última sincronização: {status.last_sync_at or 'não informada'}"
            )
        elif state == "syncing":
            detalhe = "As alterações permanecem salvas localmente enquanto a sincronização estiver em andamento."
        else:
            detalhe = (
                "A sincronização não foi concluída. As alterações continuam salvas "
                "localmente e permanecem pendentes. Tente novamente mais tarde."
            )
        messagebox.showinfo("Status da sincronização", detalhe, parent=indicador.winfo_toplevel())

    unsubscribe = tracker.add_listener(lambda: indicador.after_idle(atualizar) if indicador.winfo_exists() else None)
    indicador.bind("<Button-1>", mostrar_detalhes)
    indicador.bind(
        "<Destroy>",
        lambda event: unsubscribe() if event.widget is indicador else None,
    )
    atualizar()
    return indicador


def criar_sidebar(parent, notebook, titulo_estabelecimento, nome_usuario, perfil, voltar, abrir_usuarios=None, estilo_notebook="Hotel.TNotebook", sync_tracker=None):
    """Navegação lateral para as páginas que já são mantidas pelo Notebook."""
    paleta = {"sidebar": "#FFFFFF", "bg": "#F5F7FB", "text": "#1E293B", "muted": "#64748B", "border": "#E2E8F0", "blue": "#2563EB", "blue_soft": "#EFF6FF"}
    bar = tk.Frame(parent, bg=paleta["sidebar"], width=218, highlightbackground=paleta["border"], highlightthickness=1)
    bar.pack(side="left", fill="y")
    bar.pack_propagate(False)
    tk.Label(bar, text="📦  Controle de Estoque", bg=paleta["sidebar"], fg=paleta["text"], font=("Segoe UI", 12, "bold"), anchor="w").pack(fill="x", padx=17, pady=(22, 3))
    tk.Label(bar, text=titulo_estabelecimento, bg=paleta["sidebar"], fg=paleta["muted"], font=("Segoe UI", 9), anchor="w").pack(fill="x", padx=18, pady=(0, 22))
    tk.Label(bar, text="MENU PRINCIPAL", bg=paleta["sidebar"], fg=paleta["muted"], font=("Segoe UI", 8, "bold"), anchor="w").pack(fill="x", padx=18, pady=(0, 8))
    nav = tk.Frame(bar, bg=paleta["sidebar"])
    nav.pack(fill="x", padx=9)
    items = (("⌂", "Visão Geral"), ("▤", "Notas"), ("▦", "Produtos"), ("↻", "Controle de Saídas"), ("▥", "Relatórios"))
    buttons = []

    def selecionar(indice):
        notebook.select(indice)
        for i, button in enumerate(buttons):
            ativo = i == indice
            button.configure(bg=paleta["blue_soft"] if ativo else paleta["sidebar"], fg=paleta["blue"] if ativo else paleta["muted"], activebackground=paleta["blue_soft"] if ativo else "#F8FAFC")

    for index, (icone, rotulo) in enumerate(items):
        button = tk.Button(nav, text=f"{icone}   {rotulo}", command=lambda i=index: selecionar(i), bg=paleta["sidebar"], fg=paleta["muted"], activebackground=paleta["blue_soft"], activeforeground=paleta["blue"], relief="flat", bd=0, padx=11, pady=10, anchor="w", font=("Segoe UI", 10, "bold"), cursor="hand2")
        button.pack(fill="x", pady=2)
        buttons.append(button)
    if abrir_usuarios:
        tk.Label(bar, text="CONFIGURAÇÕES", bg=paleta["sidebar"], fg=paleta["muted"], font=("Segoe UI", 8, "bold"), anchor="w").pack(fill="x", padx=18, pady=(20, 7))
        tk.Button(bar, text="♙   Usuários", command=abrir_usuarios, bg=paleta["sidebar"], fg=paleta["muted"], activebackground=paleta["blue_soft"], activeforeground=paleta["blue"], relief="flat", bd=0, padx=18, pady=10, anchor="w", font=("Segoe UI", 10, "bold"), cursor="hand2").pack(fill="x", padx=9)
    footer = tk.Frame(bar, bg=paleta["sidebar"])
    footer.pack(side="bottom", fill="x", padx=13, pady=14)
    tk.Frame(footer, bg=paleta["border"], height=1).pack(fill="x", pady=(0, 11))
    tk.Label(footer, text=nome_usuario or "Usuário", bg=paleta["sidebar"], fg=paleta["text"], font=("Segoe UI", 9, "bold"), anchor="w").pack(fill="x")
    tk.Label(footer, text=perfil or "", bg=paleta["sidebar"], fg=paleta["muted"], font=("Segoe UI", 8), anchor="w").pack(fill="x", pady=(1, 8))
    if sync_tracker is not None:
        criar_indicador_sync(footer, sync_tracker).pack(fill="x", pady=(0, 8))
    ttk.Button(footer, text="↩  Voltar ao painel", command=voltar, style="Padrao.TButton").pack(fill="x")

    try:
        ttk.Style().layout(f"{estilo_notebook}.Tab", [])
    except tk.TclError:
        pass
    notebook.after_idle(lambda: selecionar(0))
    return bar
