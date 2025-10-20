from tads.biblioteca import *
import streamlit as st
import pandas as pd
import time
import base64

from tads.biblioteca import  (
    inicializar_biblioteca, inicializar_fila, inicializar_pilha,
    atualizar_status, atualizar_contadores_gerais, bubble_sort
)


# ---------- INICIALIZAÇÃO ----------
if "livros" not in st.session_state:
    st.session_state.livros = inicializar_biblioteca()

if "fila_emprestimos" not in st.session_state:
    st.session_state.fila_emprestimos = inicializar_fila()

if "pilha_devolucoes" not in st.session_state:
    st.session_state.pilha_devolucoes = inicializar_pilha()

# ---------- FUNÇÕES VISUAIS ----------
def mostrar_tabela(livros):
    df = pd.DataFrame(livros)
    df.index = range(1, len(df) + 1)
    st.dataframe(df.style.set_properties(**{'text-align': 'center'}))

def separar():
    st.markdown("---")

# ---------- INTERFACE ----------
#--------- FUNDO DO TITULO -----------
def set_background(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background("biblioteca_fundo.jpeg")

# ---------- CABEÇALHO FIXO COM PARALLAX ----------
with open("biblioteca_fundo.jpeg", "rb") as f:
    header_img = base64.b64encode(f.read()).decode()

st.markdown(f"""
<style>

/* ----- Cabeçalho fixo com parallax ----- */
.titulo-fundo {{
    background-image: url("data:image/jpeg;base64,{header_img}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 200px;
    z-index: 999;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}} 

/* Camada translúcida */
.titulo-overlay {{
    background: rgba(0,0,0,0.55);
    border-radius: 18px;
    padding: 25px 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 18px;
    backdrop-filter: blur(6px);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    margin-top: 30px; /* <-- AQUI abaixa o título */
}}

.titulo-overlay:hover {{
    transform: scale(1.04);
    box-shadow: 0 0 25px rgba(255,255,255,0.3);
}}

.titulo-overlay img {{
    width: 75px;
    transition: transform 0.3s ease;
}}

.titulo-overlay:hover img {{
    transform: rotate(-5deg) scale(1.1);
}}

.titulo-overlay h1 {{
    color: #fff;
    font-weight: bold;
    font-size: 40px;
    margin: 0;
    letter-spacing: 1.5px;
    text-shadow: 2px 2px 6px rgba(0,0,0,0.5);
}} 

/* Espaço pro conteúdo não ficar escondido */
.spacer {{
    height: 230px;
}}
</style>

<!-- Cabeçalho fixo com parallax -->
<div class="titulo-fundo">
    <div class="titulo-overlay">
        <img src="https://upload.wikimedia.org/wikipedia/commons/c/ca/Brasaouea.png">
        <h1>BIBLIOTECA - NESNAP/UEA</h1>
    </div>
</div>

<div class="spacer"></div>
""", unsafe_allow_html=True)

#---------MENU-------

st.sidebar.markdown("### 🛠 Menu")

menu = st.sidebar.selectbox("Escolha uma opção", [
    "📖 Ver Livros",
    "📥 Empréstimo/Devolução",
    "➕ Cadastrar Livro",
    "✏️ Editar Cadastro",
    "🗑️ Remover Livro",
    "📊 Estatísticas"
])


# ---------- VER LIVROS ----------
if menu == "📖 Ver Livros":
    st.header("📚 Lista de Livros")

    total, emprestados, disponiveis = atualizar_contadores_gerais(st.session_state.livros)
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
        livro_emprestar = st.selectbox(
            "Escolha o livro para emprestar",
            [l["Título"] for l in disponiveis]
        )
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
                        st.session_state.fila_emprestimos.append(
                            {"Aluno": aluno, "Livro": l["Título"]}
                        )

                        # 🔔 Cria espaço para mensagem temporária
                        msg = st.empty()
                        msg.success(f"✅ Livro '{l['Título']}' emprestado para {aluno}!")
                        st.info(f"📘 Agora restam {l['Disponíveis']} disponíveis.")
                        time.sleep(3)  # fica 3 segundos na tela
                        msg.empty()    # limpa a mensagem
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
elif menu == "✏️ Editar Cadastro":
    st.header("✏️ Editar Cadastro")
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
    total, emprestados, disponiveis = atualizar_contadores_gerais(st.session_state.livros)
    st.metric("📚 Total de Exemplares", total)
    st.metric("📕 Emprestados", emprestados)
    st.metric("📗 Disponíveis", disponiveis)

    df = pd.DataFrame(st.session_state.livros)
    top_emprestados = df.sort_values(by="Emprestados", ascending=False).head(5)
    st.subheader("🏆 Top 5 Livros Mais Emprestados")
    st.bar_chart(top_emprestados.set_index("Título")["Emprestados"])