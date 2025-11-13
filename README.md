# system-solver

Ferramenta para resolver sistemas lineares com números reais ou complexos em duas interfaces: um aplicativo desktop feito com CustomTkinter/Numpy e uma versão web estática acionada diretamente no navegador. O objetivo é agilizar cálculos recorrentes em circuitos elétricos e outras análises matriciais, oferecendo feedback visual, métricas e exportação dos resultados.

## Visão geral
- `solver.py` monta uma UI moderna com CustomTkinter, gera dinamicamente os campos da matriz `A`, do vetor `b` e dos nomes das variáveis (até 10×10), aceita valores com `i` ou `j`, resolve o sistema com `numpy.linalg.solve`, exibe métricas (condicionamento, determinante real, amplitude máxima), barra de progresso e possui ações de copiar/limpar/exportar.
- `index.html` replica o fluxo em uma página responsiva (“Circuit Solver Pocket”) usando apenas HTML/CSS/JS e a biblioteca `math.js` via CDN. A resolução usa determinantes (regra de Cramer) e o usuário pode gerar a matriz, resolver, copiar para a área de transferência ou baixar um `.txt`.

## Funcionalidades principais
- Entrada dinâmica de matrizes/vetores, inclusive com valores complexos e unidades personalizadas.
- Validação com mensagens contextuais (chips/status) e barra de progresso animada durante o cálculo.
- Métricas instantâneas do sistema: `cond(A)`, determinante (parte real) e maior amplitude de `x`.
- Exportação para arquivo `.txt`, cópia automática/manual para a área de transferência e botões de limpeza.
- Paletas de destaque intercambiáveis e alternância claro/escuro, mantendo o visual consistente entre desktop e web.

## Tecnologias e dependências
- Python 3.10+ com `customtkinter`, `numpy` e `pyperclip`.
- Tkinter (incluído na maior parte das distribuições Python).
- Versão web puramente estática com `math.js@13`, sem necessidade de backend.

## Executando a versão desktop (Python)
1. (Opcional) Crie um ambiente virtual:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
2. Instale as dependências:
   ```bash
   pip install customtkinter numpy pyperclip
   ```
3. Execute o aplicativo:
   ```bash
   python3 solver.py
   ```
4. Informe o número de variáveis, preencha a matriz/vetor (suporta `3-2i`, `1+4j`, etc.) e clique em **Resolver Sistema**. Use os botões para copiar ou exportar o relatório.

## Executando a versão web
1. Nenhuma dependência adicional é necessária: abra `index.html` em qualquer navegador moderno.
2. Escolha o tamanho do sistema, preencha `A` e `b`, clique em **Resolver** e acompanhe o passo a passo gerado (inclui determinantes intermediários e formatação dos complexos).
3. Use **Copiar agora** ou **Exportar .txt** para reutilizar o resultado.

## Estrutura do repositório
```
.
├── solver.py    # Aplicativo CustomTkinter com solver baseado em NumPy
├── index.html   # Versão web estática com math.js para cálculos
└── README.md    # Este documento
```

## Próximos passos sugeridos
- Empacotar as dependências Python em um `requirements.txt` ou `pyproject.toml`.
- Adicionar testes automatizados simples (por exemplo, scripts que checam casos conhecidos via NumPy).
- Publicar a versão web (GitHub Pages/Netlify) para facilitar o acesso em dispositivos móveis.
