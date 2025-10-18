import streamlit as st
import pandas as pd
from collections import deque

# ---------- INICIALIZAÇÃO ----------
if "livros" not in st.session_state:  
    st.session_state.livros = [
        {"Título": "Fundamentos de Python 🐍", "Autor": "João Silva", "Gênero": "Tecnologia",
         "Quantidade Total": 5, "Emprestados": 0, "Disponíveis": 5, "Status": "Disponível"},
        {"Título": "Algoritmos e Estruturas ⚙️", "Autor": "Maria Souza", "Gênero": "Tecnologia",
         "Quantidade Total": 3, "Emprestados": 0, "Disponíveis": 3, "Status": "Disponível"},
        {"Título": "História do Amazonas 🌳", "Autor": "Carlos Lima", "Gênero": "História",
         "Quantidade Total": 4, "Emprestados": 0, "Disponíveis": 4, "Status": "Disponível"},
        {"Título": "Romance Amazônico ❤️", "Autor": "Ana Pereira", "Gênero": "Romance",
         "Quantidade Total": 2, "Emprestados": 0, "Disponíveis": 2, "Status": "Disponível"},
    ]

if "fila_emprestimos" not in st.session_state:
    st.session_state.fila_emprestimos = deque()

if "pilha_devolucoes" not in st.session_state:
    st.session_state.pilha_devolucoes = []

# ---------- FUNÇÕES ----------
def bubble_sort(livros, chave):
    n = len(livros)
    for i in range(n):
        for j in range(0, n - i - 1):
            if livros[j][chave] > livros[j + 1][chave]:
                livros[j], livros[j + 1] = livros[j + 1], livros[j]
    return livros

def mostrar_tabela(livros):
    df = pd.DataFrame(livros)
    df.index = range(1, len(df) + 1)
    st.dataframe(df.style.set_properties(**{'text-align': 'center'}))

def separar():
    st.markdown("---")

def atualizar_status(livro):
    livro["Status"] = "Indisponível" if livro["Disponíveis"] == 0 else "Disponível"

def atualizar_contadores_gerais():
    total = sum(l["Quantidade Total"] for l in st.session_state.livros)
    emprestados = sum(l["Emprestados"] for l in st.session_state.livros)
    disponiveis = sum(l["Disponíveis"] for l in st.session_state.livros)
    return total, emprestados, disponiveis

# ---------- INTERFACE ----------
st.markdown("<h1 style='text-align: center; color: purple;'> Biblioteca - UEA 📚</h1>", unsafe_allow_html=True)
st.sidebar.markdown("### 🛠 Menu")

menu = st.sidebar.selectbox("Escolha uma opção", [
    "📖 Ver Livros",
    "📥 Empréstimo/Devolução",
    "➕ Cadastrar Livro",
    "✏️ Editar Livro",
    "🗑️ Remover Livro",
    "📊 Estatísticas"
])

# ---------- VER LIVROS ----------
if menu == "📖 Ver Livros":
    st.header("📚 Lista de Livros")

    total, emprestados, disponiveis = atualizar_contadores_gerais()
    st.info(f"**Total de exemplares:** {total} | **Emprestados:** {emprestados} | **Disponíveis:** {disponiveis}")

    # 🔍 Buscar Livro
    st.subheader("🔍 Buscar Livro")
    busca = st.text_input("Digite título ou autor")
    filtro_genero = st.selectbox("Filtrar por gênero", ["Todos"] + list(set([l["Gênero"] for l in st.session_state.livros])))

    # 🔠 Ordenar
    criterio = st.selectbox("Ordenar por:", ["Título", "Autor", "Gênero"])
    if st.button("🔃 Ordenar"):
        bubble_sort(st.session_state.livros, criterio)
        st.success(f"✅ Livros ordenados por {criterio.lower()}!")

    # Filtragem e busca
    resultados = [
        l for l in st.session_state.livros
        if (busca.lower() in l["Título"].lower() or busca.lower() in l["Autor"].lower())
        and (filtro_genero == "Todos" or l["Gênero"] == filtro_genero)
    ]

    if busca and not resultados:
        st.warning("⚠️ Nenhum livro encontrado com esse termo de busca.")
    else:
        mostrar_tabela(resultados if resultados else st.session_state.livros)

# ---------- EMPRÉSTIMO / DEVOLUÇÃO ----------
elif menu == "📥 Empréstimo/Devolução":
    st.header("📤 Empréstimo de Livro")
    disponiveis = [l for l in st.session_state.livros if l["Disponíveis"] > 0]

    if disponiveis:
        livro_emprestar = st.selectbox("Escolha o livro para emprestar", [l["Título"] for l in disponiveis])
        aluno = st.text_input("Nome do aluno")
        if st.button("📥 Emprestar"):
            if not aluno:
                st.warning("⚠️ Digite o nome do aluno antes de realizar o empréstimo!")
            else:
                for l in st.session_state.livros:
                    if l["Título"] == livro_emprestar:
                        l["Emprestados"] += 1
                        l["Disponíveis"] -= 1
                        atualizar_status(l)
                        st.session_state.fila_emprestimos.append({"Aluno": aluno, "Livro": l["Título"]})
                        st.success(f"✅ Livro '{l['Título']}' emprestado para {aluno}!")
                        st.info(f"📘 O livro '{l['Título']}' foi emprestado com sucesso e agora possui {l['Disponíveis']} disponíveis.")
                st.rerun()
    else:
        st.info("📭 Nenhum exemplar disponível para empréstimo.")

    separar()

    # Devolução
    st.header("📥 Devolução de Livro")
    if st.session_state.fila_emprestimos:
        opcoes = [f"{f['Livro']} — {f['Aluno']}" for f in st.session_state.fila_emprestimos]
        devolucao = st.selectbox("Selecione o livro e o aluno", opcoes)

        if st.button("📤 Devolver"):
            livro_devolver, aluno_devolver = devolucao.split(" — ")
            for l in st.session_state.livros:
                if l["Título"] == livro_devolver:
                    l["Emprestados"] -= 1
                    l["Disponíveis"] += 1
                    atualizar_status(l)
                    st.session_state.pilha_devolucoes.append(l["Título"])

                    for f in list(st.session_state.fila_emprestimos):
                        if f["Livro"] == livro_devolver and f["Aluno"] == aluno_devolver:
                            st.session_state.fila_emprestimos.remove(f)
                            break
                    st.success(f"✅ {aluno_devolver} devolveu o livro '{livro_devolver}' com sucesso!")
                    st.info(f"📗 O livro '{livro_devolver}' voltou para a biblioteca e agora possui {l['Disponíveis']} disponíveis.")
            st.rerun()
    else:
        st.info("📭 Nenhum livro emprestado no momento.")

# ---------- CADASTRAR, EDITAR, REMOVER, ESTATÍSTICAS ----------
# (mantém igual ao seu último código, sem alterações nessas partes)

