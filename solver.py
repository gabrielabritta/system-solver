from tkinter import filedialog, messagebox

import customtkinter as ctk  # pip install customtkinter
import numpy as np
import pyperclip  # pip install pyperclip for clipboard

# Paletas globais
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

ACCENT_PRESETS = {
    "Turquesa Neon": ("#00F5D4", "#00BFA6"),
    "Uva Elétrica": ("#C084FC", "#A855F7"),
    "Solar Punk": ("#FACC15", "#EAB308"),
    "Ciano Profundo": ("#06B6D4", "#0891B2"),
}

STATUS_STYLES = {
    "info": ("#1D4ED8", "#E0F2FE"),
    "success": ("#15803D", "#DCFCE7"),
    "warning": ("#F97316", "#FFEDD5"),
    "error": ("#B91C1C", "#FEE2E2"),
}

entries_A = []
entries_b = []
entries_vars = []
frame_A_body = None
frame_b_body = None
frame_vars_body = None
badge_equacoes = None
progress_var = None
solve_progress = None
status_chip = None
metrics_labels = {}
accentable_widgets = []
current_accent = ACCENT_PRESETS["Turquesa Neon"]


def register_accent_widget(widget):
    """Guarda widgets que devem reagir à troca de destaque."""
    accentable_widgets.append(widget)
    widget.configure(fg_color=current_accent[0], hover_color=current_accent[1])
    return widget


def alterar_accent(choice):
    """Atualiza o esquema de cores vibrantes."""
    global current_accent
    current_accent = ACCENT_PRESETS[choice]
    for widget in accentable_widgets:
        widget.configure(fg_color=current_accent[0], hover_color=current_accent[1])
    if solve_progress is not None:
        solve_progress.configure(progress_color=current_accent[0])


def alterar_modo(value):
    """Alterna entre dark/light/system instantaneamente."""
    ctk.set_appearance_mode(value)


def atualizar_status(texto, nivel="info"):
    """Mostra feedback contextual no chip de status."""
    if status_chip is None:
        return
    bg_color, text_color = STATUS_STYLES.get(nivel, STATUS_STYLES["info"])
    status_chip.configure(text=texto, fg_color=bg_color, text_color=text_color)


def reset_metricas(visao="—"):
    """Reseta os cartões de métricas."""
    for label in metrics_labels.values():
        label.configure(text=visao)


def atualizar_metricas(x, matriz):
    """Atualiza cartões com indicadores rápidos do sistema resolvido."""
    if not metrics_labels:
        return
    condicao = np.linalg.cond(matriz)
    determinante = np.linalg.det(matriz)
    intensidade = np.max(np.abs(x))

    metrics_labels["cond"].configure(text=f"{condicao:,.1f}")
    metrics_labels["det"].configure(text=f"{determinante.real:,.2f}")
    metrics_labels["amp"].configure(text=f"{intensidade:.2f}")


def parse_complex(value):
    """Parse string to complex number, handling 'j' for imaginary."""
    try:
        return complex(value.replace("i", "j"))
    except ValueError as exc:
        raise ValueError(f"Valor inválido: {value}. Use formato como '3+4j'.") from exc


def focus_next_widget(widget):
    """Move foco para o próximo widget com Tab/Enter."""
    widget.tk_focusNext().focus()
    return "break"


def gerar_campos():
    """Gera campos dinâmicos para matriz A, vetor b e nomes."""
    try:
        n = int(entry_n.get())
        if n < 1 or n > 10:
            raise ValueError("Número de variáveis deve ser entre 1 e 10.")

        badge_equacoes.configure(
            text=f"{n} variáveis • {n} equações", text_color="#A5F3FC"
        )

        # Limpa frames antigos
        for container in (frame_A_body, frame_b_body, frame_vars_body):
            for widget in container.winfo_children():
                widget.destroy()

        global entries_A, entries_b, entries_vars
        entries_A = [[None for _ in range(n)] for _ in range(n)]
        for row in range(n):
            for col in range(n):
                label = ctk.CTkLabel(frame_A_body, text=f"A[{row + 1},{col + 1}]")
                label.grid(row=row, column=2 * col, padx=4, pady=4, sticky="e")
                entry = ctk.CTkEntry(
                    frame_A_body,
                    width=110,
                    placeholder_text="ex: 1+2j",
                )
                entry.grid(row=row, column=2 * col + 1, padx=4, pady=4, sticky="w")
                entries_A[row][col] = entry
                entry.bind("<Tab>", lambda e: focus_next_widget(e.widget))
                entry.bind("<Return>", lambda e: focus_next_widget(e.widget))

        entries_b = [None] * n
        for i in range(n):
            label = ctk.CTkLabel(frame_b_body, text=f"b[{i + 1}]")
            label.grid(row=i, column=0, padx=4, pady=4, sticky="e")
            entry = ctk.CTkEntry(frame_b_body, width=120, placeholder_text="ex: 3+4j")
            entry.grid(row=i, column=1, padx=4, pady=4, sticky="w")
            entries_b[i] = entry
            entry.bind("<Tab>", lambda e: focus_next_widget(e.widget))
            entry.bind("<Return>", lambda e: focus_next_widget(e.widget))

        entries_vars = [None] * n
        for i in range(n):
            label = ctk.CTkLabel(frame_vars_body, text=f"Var[{i + 1}]")
            label.grid(row=i, column=0, padx=4, pady=4, sticky="e")
            entry = ctk.CTkEntry(
                frame_vars_body,
                width=160,
                placeholder_text=f"x{i + 1}",
            )
            entry.insert(0, f"x{i + 1}")
            entry.grid(row=i, column=1, padx=4, pady=4, sticky="w")
            entries_vars[i] = entry

        atualizar_status("Campos prontos. Preencha e dispare o solver ⚡", "info")

    except ValueError as ve:
        atualizar_status(str(ve), "warning")
        messagebox.showerror("Erro", str(ve))


def resolver_sistema():
    """Resolve Ax=b e entrega métricas + texto formatado."""
    try:
        n = int(entry_n.get())
        if not entries_A or len(entries_A) != n:
            gerar_campos()

        progress_var.set(0.2)
        app.update_idletasks()

        A = np.zeros((n, n), dtype=complex)
        for i in range(n):
            for j in range(n):
                A[i, j] = parse_complex(entries_A[i][j].get().strip() or "0")

        progress_var.set(0.45)
        app.update_idletasks()

        b = np.zeros(n, dtype=complex)
        for i in range(n):
            b[i] = parse_complex(entries_b[i].get().strip() or "0")

        progress_var.set(0.7)
        app.update_idletasks()

        x = np.linalg.solve(A, b)

        unidade = combo_unidade.get()
        resultado = "Resultados:\n\n"
        for i in range(n):
            var_name = entries_vars[i].get().strip() or f"x{i + 1}"
            real_part = x[i].real
            imag_part = x[i].imag
            if np.isclose(imag_part, 0):
                valor = f"{real_part:.4g}"
            else:
                sinal = " + " if imag_part > 0 else " - "
                valor = f"{real_part:.4g}{sinal}{abs(imag_part):.4g}j"
            resultado += f"{var_name} = {valor}{unidade}\n"

        text_saida.configure(state="normal")
        text_saida.delete("1.0", ctk.END)
        text_saida.insert(ctk.END, resultado)
        text_saida.configure(state="disabled")

        progress_var.set(1.0)
        app.after(400, lambda: progress_var.set(0.0))

        atualizar_metricas(x, A)
        atualizar_status("Sistema resolvido com sucesso ✨", "success")

        if switch_clipboard.get():
            pyperclip.copy(resultado)
            messagebox.showinfo(
                "Info", "Resultado copiado para a área de transferência!"
            )

    except np.linalg.LinAlgError:
        progress_var.set(0.0)
        atualizar_status("Sistema singular ou sem solução única!", "error")
        messagebox.showerror(
            "Erro", "Sistema singular ou sem solução única! Verifique as equações."
        )
    except ValueError as ve:
        progress_var.set(0.0)
        atualizar_status(str(ve), "warning")
        messagebox.showerror("Erro de Entrada", str(ve))
    except Exception as exc:
        progress_var.set(0.0)
        atualizar_status("Ops! Erro inesperado.", "error")
        messagebox.showerror("Erro Geral", f"Ocorreu um erro: {exc}")


def limpar_tudo():
    """Limpa todos os campos e métricas."""
    entry_n.delete(0, ctk.END)
    for container in (frame_A_body, frame_b_body, frame_vars_body):
        for widget in container.winfo_children():
            widget.destroy()
    text_saida.configure(state="normal")
    text_saida.delete("1.0", ctk.END)
    text_saida.configure(state="disabled")
    badge_equacoes.configure(text="Pronto para até 10 variáveis", text_color="#94A3B8")
    switch_clipboard.deselect()
    progress_var.set(0.0)
    reset_metricas()
    atualizar_status("Workspace limpo. Pronto para um novo circuito.", "info")


def preencher_exemplo():
    """Popula um circuito de demonstração vibrante."""
    exemplo_A = [
        [4 + 2j, -1, 0.5j],
        [1 - 1j, 3 + 0.2j, -0.6],
        [0.5, 1.2j, 2.5],
    ]
    exemplo_b = [5 + 3j, 2 - 1j, 4]
    exemplo_vars = ["I1", "I2", "I3"]

    entry_n.delete(0, ctk.END)
    entry_n.insert(0, "3")
    gerar_campos()

    for i, linha in enumerate(exemplo_A):
        for j, valor in enumerate(linha):
            entries_A[i][j].delete(0, ctk.END)
            entries_A[i][j].insert(0, f"{valor}")

    for i, valor in enumerate(exemplo_b):
        entries_b[i].delete(0, ctk.END)
        entries_b[i].insert(0, f"{valor}")

    for i, nome in enumerate(exemplo_vars):
        entries_vars[i].delete(0, ctk.END)
        entries_vars[i].insert(0, nome)

    combo_unidade.set(" A")
    atualizar_status("Exemplo carregado. Apenas aperte Resolver! ⚙️", "success")


def salvar_resultado():
    """Exporta o relatório de resultados para um .txt."""
    texto = text_saida.get("1.0", ctk.END).strip()
    if not texto:
        atualizar_status("Nada para exportar ainda.", "warning")
        messagebox.showwarning("Aviso", "Calcule um sistema antes de salvar.")
        return

    caminho = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Texto", "*.txt"), ("Todos os arquivos", "*.*")],
        title="Salvar resultado como...",
    )
    if caminho:
        with open(caminho, "w", encoding="utf-8") as arquivo:
            arquivo.write(texto)
        atualizar_status("Resultado exportado com sucesso.", "success")


def copiar_resultado_agora():
    """Atalho manual para copiar o resultado."""
    texto = text_saida.get("1.0", ctk.END).strip()
    if not texto:
        atualizar_status("Nenhum resultado para copiar.", "warning")
        return
    pyperclip.copy(texto)
    atualizar_status("Resultado copiado! 📋", "success")


# Cria janela principal
app = ctk.CTk()
app.title("Super Resolvedor de Sistemas Lineares - Circuitos")
app.geometry("1024x760")
app.minsize(940, 700)

progress_var = ctk.DoubleVar(value=0.0)

# Frame principal com scroll
scroll_frame = ctk.CTkScrollableFrame(app, orientation="vertical")
scroll_frame.pack(fill="both", expand=True, padx=24, pady=24)
scroll_frame.grid_columnconfigure(0, weight=1)

# Hero / Header
header_frame = ctk.CTkFrame(scroll_frame, corner_radius=18, border_width=1)
header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 18))
header_frame.grid_columnconfigure((0, 1, 2), weight=1)

title_label = ctk.CTkLabel(
    header_frame,
    text="Circuit Solver Studio ⚡",
    font=ctk.CTkFont(size=26, weight="bold"),
)
title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 4), sticky="w")

subtitle_label = ctk.CTkLabel(
    header_frame,
    text="Monte sistemas complexos, visualize métricas críticas e exporte insights em segundos.",
    text_color="#94A3B8",
)
subtitle_label.grid(row=1, column=0, columnspan=2, padx=20, sticky="w")

badge_equacoes = ctk.CTkLabel(
    header_frame,
    text="Pronto para até 10 variáveis",
    fg_color="#1E293B",
    text_color="#94A3B8",
    corner_radius=50,
    padx=16,
    pady=6,
)
badge_equacoes.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="w")

appearance_selector = ctk.CTkSegmentedButton(
    header_frame,
    values=["Dark", "Light", "System"],
    command=alterar_modo,
)
appearance_selector.grid(row=0, column=2, padx=20, pady=(20, 10), sticky="e")
appearance_selector.set("Dark")

accent_menu = ctk.CTkOptionMenu(
    header_frame,
    values=list(ACCENT_PRESETS.keys()),
    command=alterar_accent,
    width=180,
)
accent_menu.grid(row=1, column=2, padx=20, pady=10, sticky="e")
accent_menu.set("Turquesa Neon")

# Toolbar primária
toolbar_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
toolbar_frame.grid(row=1, column=0, sticky="ew", pady=(0, 12))
toolbar_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

label_n = ctk.CTkLabel(toolbar_frame, text="Nº de variáveis/equações:")
label_n.grid(row=0, column=0, padx=10, pady=6, sticky="w")

entry_n = ctk.CTkEntry(toolbar_frame, width=110, placeholder_text="ex: 3")
entry_n.grid(row=0, column=1, padx=10, pady=6, sticky="w")
entry_n.bind("<Return>", lambda e: gerar_campos())

btn_gerar = register_accent_widget(
    ctk.CTkButton(toolbar_frame, text="Gerar Campos", command=gerar_campos)
)
btn_gerar.grid(row=0, column=2, padx=10, pady=6)

btn_demo = register_accent_widget(
    ctk.CTkButton(toolbar_frame, text="Carregar Exemplo", command=preencher_exemplo)
)
btn_demo.grid(row=0, column=3, padx=10, pady=6)

# Frames para A, b e vars
frame_A = ctk.CTkFrame(scroll_frame, corner_radius=16, border_width=1)
frame_A.grid(row=2, column=0, sticky="ew", pady=10)
frame_A.grid_columnconfigure(0, weight=1)
ctk.CTkLabel(
    frame_A, text="Matriz A (coeficientes)", font=ctk.CTkFont(weight="bold")
).grid(row=0, column=0, padx=16, pady=(16, 4), sticky="w")
frame_A_body = ctk.CTkFrame(frame_A, fg_color="transparent")
frame_A_body.grid(row=1, column=0, padx=16, pady=(4, 16), sticky="ew")
for coluna in range(20):
    frame_A_body.grid_columnconfigure(coluna, weight=1)

frame_b = ctk.CTkFrame(scroll_frame, corner_radius=16, border_width=1)
frame_b.grid(row=3, column=0, sticky="ew", pady=10)
frame_b.grid_columnconfigure(0, weight=1)
ctk.CTkLabel(
    frame_b, text="Vetor b (resultados)", font=ctk.CTkFont(weight="bold")
).grid(row=0, column=0, padx=16, pady=(16, 4), sticky="w")
frame_b_body = ctk.CTkFrame(frame_b, fg_color="transparent")
frame_b_body.grid(row=1, column=0, padx=16, pady=(4, 16), sticky="ew")
frame_b_body.grid_columnconfigure((0, 1), weight=1)

frame_vars = ctk.CTkFrame(scroll_frame, corner_radius=16, border_width=1)
frame_vars.grid(row=4, column=0, sticky="ew", pady=10)
frame_vars.grid_columnconfigure(0, weight=1)
ctk.CTkLabel(
    frame_vars, text="Nomes das Variáveis (opcional)", font=ctk.CTkFont(weight="bold")
).grid(row=0, column=0, padx=16, pady=(16, 4), sticky="w")
frame_vars_body = ctk.CTkFrame(frame_vars, fg_color="transparent")
frame_vars_body.grid(row=1, column=0, padx=16, pady=(4, 16), sticky="ew")
frame_vars_body.grid_columnconfigure((0, 1), weight=1)

# Unidade + switch + status
controls_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
controls_frame.grid(row=5, column=0, sticky="ew", pady=(4, 6))
controls_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

label_unidade = ctk.CTkLabel(controls_frame, text="Unidade padrão:")
label_unidade.grid(row=0, column=0, padx=10, pady=6, sticky="w")

combo_unidade = ctk.CTkComboBox(
    controls_frame,
    values=[" V", " A", " Ω"],
    width=140,
)
combo_unidade.grid(row=0, column=1, padx=10, pady=6, sticky="w")
combo_unidade.set(" A")

switch_clipboard = ctk.CTkSwitch(
    controls_frame,
    text="Copiar resultado automaticamente?",
)
switch_clipboard.grid(row=0, column=2, padx=10, pady=6, sticky="w")

status_chip = ctk.CTkLabel(
    controls_frame,
    text="Configure o sistema e clique em Resolver.",
    fg_color=STATUS_STYLES["info"][0],
    text_color=STATUS_STYLES["info"][1],
    corner_radius=20,
    padx=16,
    pady=6,
)
status_chip.grid(row=0, column=3, padx=10, pady=6, sticky="e")

# Barra de progresso
solve_progress = ctk.CTkProgressBar(
    scroll_frame,
    variable=progress_var,
    height=12,
    progress_color=current_accent[0],
)
solve_progress.grid(row=6, column=0, sticky="ew", pady=(6, 12), padx=4)

# Botões principais
buttons_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
buttons_frame.grid(row=7, column=0, pady=10, sticky="ew")
buttons_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

btn_resolver = register_accent_widget(
    ctk.CTkButton(buttons_frame, text="Resolver Sistema", command=resolver_sistema)
)
btn_resolver.grid(row=0, column=0, padx=10, pady=6, sticky="ew")

btn_limpar = register_accent_widget(
    ctk.CTkButton(buttons_frame, text="Limpar Tudo", command=limpar_tudo)
)
btn_limpar.grid(row=0, column=1, padx=10, pady=6, sticky="ew")

btn_exportar = register_accent_widget(
    ctk.CTkButton(buttons_frame, text="Exportar .txt", command=salvar_resultado)
)
btn_exportar.grid(row=0, column=2, padx=10, pady=6, sticky="ew")

btn_copiar = register_accent_widget(
    ctk.CTkButton(buttons_frame, text="Copiar Agora", command=copiar_resultado_agora)
)
btn_copiar.grid(row=0, column=3, padx=10, pady=6, sticky="ew")

# Métricas resumidas
metrics_frame = ctk.CTkFrame(scroll_frame, corner_radius=16, border_width=1)
metrics_frame.grid(row=8, column=0, sticky="ew", pady=12)
metrics_frame.grid_columnconfigure((0, 1, 2), weight=1)

metric_titles = [
    ("Cond(A)", "cond"),
    ("Det(A) (parte real)", "det"),
    ("Maior amplitude |x|", "amp"),
]

for idx, (titulo, chave) in enumerate(metric_titles):
    card = ctk.CTkFrame(metrics_frame, corner_radius=14)
    card.grid(row=0, column=idx, padx=12, pady=12, sticky="ew")
    ctk.CTkLabel(card, text=titulo, text_color="#94A3B8").pack(pady=(14, 4))
    valor = ctk.CTkLabel(
        card,
        text="—",
        font=ctk.CTkFont(size=22, weight="bold"),
    )
    valor.pack(pady=(0, 14))
    metrics_labels[chave] = valor

# Resultado com scroll
resultado_frame = ctk.CTkFrame(scroll_frame, corner_radius=16, border_width=1)
resultado_frame.grid(row=9, column=0, sticky="ew", pady=(10, 0))
resultado_frame.grid_columnconfigure(0, weight=1)

ctk.CTkLabel(
    resultado_frame,
    text="Resultado formatado",
    font=ctk.CTkFont(size=16, weight="bold"),
).grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")

text_saida = ctk.CTkTextbox(
    resultado_frame,
    height=180,
    font=("JetBrains Mono", 12),
    corner_radius=12,
)
text_saida.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="ew")
text_saida.configure(state="disabled")

app.mainloop()
