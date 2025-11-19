import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dataset e Metadados", layout="wide")

st.title("📁 Dataset e Metadados")
st.markdown("Informações completas sobre a base de dados utilizada")

if 'df_filtrado' not in st.session_state:
    st.error("Por favor, volte à página inicial para carregar os dados.")
    st.stop()

df = st.session_state.df_filtrado

# Informações do dataset
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Estatísticas do Dataset")
    
    st.metric("Total de Registros", len(df))
    st.metric("Total de Colunas", len(df.columns))
    st.metric("Ralis Únicos", df['rally'].nunique())
    st.metric("Período Coberto", f"{df['rally'].min()} a {df['rally'].max()}")

with col2:
    st.subheader("🔍 Qualidade dos Dados")
    
    complete_records = df.notna().all(axis=1).sum()
    st.metric("Registros Completos", f"{(complete_records/len(df)*100):.1f}%")
    
    numeric_columns = len(df.select_dtypes(include=['number']).columns)
    st.metric("Colunas Numéricas", numeric_columns)
    
    categorical_columns = len(df.select_dtypes(include=['object']).columns)
    st.metric("Colunas Categóricas", categorical_columns)

# Dicionário de variáveis
st.subheader("📖 Dicionário de Variáveis")

variable_dict = {
    'rally': 'Número identificador do rally',
    'round': 'Número da ação dentro do rally', 
    'team': 'Time (a ou b)',
    'receive_location': 'Localização da recepção do saque',
    'digger_location': 'Localização do jogador que faz a defesa',
    'pass_land_location': 'Localização onde o passe aterrissa',
    'hitter_location': 'Localização do atacante',
    'hit_land_location': 'Localização onde o ataque aterrissa',
    'pass_rating': 'Avaliação do passe (in/out)',
    'set_type': 'Tipo de levantamento',
    'set_location': 'Localização do levantamento', 
    'hit_type': 'Tipo de ataque',
    'num_blockers': 'Número de bloqueadores',
    'block_touch': 'Houve toque no bloqueio? (yes/no)',
    'serve_type': 'Tipo de saque',
    'win_reason': 'Razão da vitória no rally',
    'lose_reason': 'Razão da derrota no rally',
    'winning_team': 'Time vencedor do rally'
}

var_df = pd.DataFrame(list(variable_dict.items()), columns=['Variável', 'Descrição'])
st.dataframe(var_df, use_container_width=True, hide_index=True)

# Dados brutos
st.subheader("📋 Dados Brutos")

# Opções de visualização
view_option = st.radio(
    "Tipo de visualização:",
    ["Amostra dos dados", "Dados completos", "Estatísticas descritivas"]
)

if view_option == "Amostra dos dados":
    st.dataframe(df.head(100), use_container_width=True)
    
elif view_option == "Dados completos":
    st.dataframe(df, use_container_width=True)
    
else:
    st.dataframe(df.describe(), use_container_width=True)

# Download dos dados
st.subheader("📥 Download dos Dados")

col3, col4 = st.columns(2)

with col3:
    st.markdown("**Download dos Dados Filtrados**")
    csv = df.to_csv(index=False)
    st.download_button(
        label="📊 Baixar CSV Filtrado",
        data=csv,
        file_name="dados_voleibol_filtrado.csv",
        mime="text/csv"
    )

with col4:
    st.markdown("**Download do Dataset Original**")
    # Aqui você pode adicionar o download do dataset original se necessário
    st.info("Dataset completo disponível no repositório do projeto")

# Informações técnicas
st.subheader("🔧 Informações Técnicas")

col5, col6 = st.columns(2)

with col5:
    st.markdown("""
    **📚 Bibliotecas Utilizadas:**
    - Streamlit (interface web)
    - Pandas (manipulação de dados)
    - Plotly (gráficos interativos)
    - Matplotlib (gráficos estáticos)
    """)

with col6:
    st.markdown("""
    **⚙️ Processamento:**
    - Filtros em tempo real
    - Cache inteligente de dados
    - Tradução automática de termos
    - Tratamento de valores missing
    """)

st.markdown("---")
st.success("""
**🎯 Sobre este Dataset:**
Esta base de dados representa uma amostra significativa do voleibol universitário feminino,
capturando mais de 2.000 ações de jogo com 15+ variáveis por registro. Ideal para análise
tática, scouting de equipes e estudo de padrões de jogo.
""")