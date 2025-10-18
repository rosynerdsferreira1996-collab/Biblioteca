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
    st.session_state.fila_emprestimos = deque()  # fila de empréstimos (ordem de saída)

if "pilha_devolucoes" not in st.session_state:
    st.session_state.pilha_devolucoes = []  # pilha de devoluções (último a devolver)

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
                        st.info(f"ℹ️ {aluno} agora está com o livro '{l['Título']}'.")
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
                    st.info("ℹ️ A tabela e os status foram atualizados automaticamente.")
            st.rerun()
    else:
        st.info("📭 Nenhum livro emprestado no momento.")

# ---------- CADASTRAR LIVRO ----------
elif menu == "➕ Cadastrar Livro":
    st.header("📥 Cadastrar Novo Livro")
    titulo = st.text_input("Título")
    autor = st.text_input("Autor")
    genero = st.text_input("Gênero")
    quantidade = st.number_input("Quantidade total", min_value=1, step=1)

    if st.button("➕ Adicionar Livro"):
        if not titulo or not autor or not genero:
            st.warning("⚠️ Preencha todos os campos antes de adicionar o livro!")
        else:
            novo = {
                "Título": titulo,
                "Autor": autor,
                "Gênero": genero,
                "Quantidade Total": quantidade,
                "Emprestados": 0,
                "Disponíveis": quantidade,
                "Status": "Disponível"
            }
            st.session_state.livros.append(novo)
            st.success(f"📚 Livro '{titulo}' adicionado à biblioteca com {quantidade} exemplares!")
            st.rerun()

# ---------- EDITAR LIVRO ----------
elif menu == "✏️ Editar Livro":
    st.header("✏️ Editar Livro")
    if st.session_state.livros:
        livro_editar = st.selectbox("Selecione o livro para editar", [l["Título"] for l in st.session_state.livros])
        livro = next(l for l in st.session_state.livros if l["Título"] == livro_editar)

        novo_titulo = st.text_input("Novo Título", value=livro["Título"])
        novo_autor = st.text_input("Novo Autor", value=livro["Autor"])
        novo_genero = st.text_input("Novo Gênero", value=livro["Gênero"])
        nova_qtd = st.number_input("Nova Quantidade Total", min_value=livro["Emprestados"], step=1, value=livro["Quantidade Total"])

        if st.button("💾 Salvar Alterações"):
            dif = nova_qtd - livro["Quantidade Total"]
            livro["Título"] = novo_titulo
            livro["Autor"] = novo_autor
            livro["Gênero"] = novo_genero
            livro["Quantidade Total"] = nova_qtd
            livro["Disponíveis"] += dif
            if livro["Disponíveis"] < 0:
                livro["Disponíveis"] = 0
            atualizar_status(livro)
            st.success(f"✅ Alterações salvas! O livro '{livro['Título']}' foi atualizado com sucesso.")
            st.info("ℹ️ A tabela de livros foi atualizada automaticamente.")
            st.rerun()
    else:
        st.info("📚 Nenhum livro cadastrado para editar.")

# ---------- REMOVER LIVRO ----------
elif menu == "🗑️ Remover Livro":
    st.header("🗑️ Remover Livro da Biblioteca")
    if st.session_state.livros:
        livro_remover = st.selectbox("Selecione o livro para remover", [l["Título"] for l in st.session_state.livros])
        confirmar = st.checkbox("Confirmar remoção permanente")
        if st.button("❌ Remover Livro"):
            if confirmar:
                st.session_state.livros = [l for l in st.session_state.livros if l["Título"] != livro_remover]
                st.success(f"📕 Livro '{livro_remover}' removido da biblioteca!")
                st.rerun()
            else:
                st.warning("⚠️ Marque a opção de confirmação para remover o livro.")
    else:
        st.info("📚 Nenhum livro cadastrado na biblioteca.")

# ---------- ESTATÍSTICAS ----------
elif menu == "📊 Estatísticas":
    st.header("📊 Estatísticas da Biblioteca")
    total, emprestados, disponiveis = atualizar_contadores_gerais()
    st.metric("📚 Total de Exemplares", total)
    st.metric("📕 Emprestados", emprestados)
    st.metric("📗 Disponíveis", disponiveis)

    df = pd.DataFrame(st.session_state.livros)
    top_emprestados = df.sort_values(by="Emprestados", ascending=False).head(5)
    st.subheader("🏆 Top 5 Livros Mais Emprestados")
    st.bar_chart(top_emprestados.set_index("Título")["Emprestados"])
