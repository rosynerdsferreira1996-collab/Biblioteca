from collections import deque

# ---------- ESTRUTURAS ----------
def inicializar_biblioteca():
    return [
        {"Título": "Fundamentos de Python 🐍", "Autor": "Rosielly Silva", "Gênero": "Tecnologia",
         "Quantidade Total": 5, "Emprestados": 0, "Disponíveis": 5, "Status": "Disponível"},
        {"Título": "Algoritmos e Estruturas ⚙️", "Autor": "Maria Souza", "Gênero": "Tecnologia",
         "Quantidade Total": 3, "Emprestados": 0, "Disponíveis": 3, "Status": "Disponível"},
        {"Título": "História do Amazonas 🌳", "Autor": "Carlos Lima", "Gênero": "História",
         "Quantidade Total": 4, "Emprestados": 0, "Disponíveis": 4, "Status": "Disponível"},
        {"Título": "Romance Amazônico ❤️", "Autor": "Ana Pereira", "Gênero": "Romance",
         "Quantidade Total": 2, "Emprestados": 0, "Disponíveis": 2, "Status": "Disponível"},
    ]

def inicializar_fila():
    return deque()

def inicializar_pilha():
    return []

# ---------- FUNÇÕES PRINCIPAIS ----------
def atualizar_status(livro):
    livro["Status"] = "Indisponível" if livro["Disponíveis"] == 0 else "Disponível"

def atualizar_contadores_gerais(livros):
    total = sum(l["Quantidade Total"] for l in livros)
    emprestados = sum(l["Emprestados"] for l in livros)
    disponiveis = sum(l["Disponíveis"] for l in livros)
    return total, emprestados, disponiveis

# ---------- ORDENAÇÃO ----------
def bubble_sort(livros, chave):
    n = len(livros)
    for i in range(n):
        for j in range(0, n - i - 1):
            if livros[j][chave] > livros[j + 1][chave]:
                livros[j], livros[j + 1] = livros[j + 1], livros[j]
    return livros


