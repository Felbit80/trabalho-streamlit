import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Análise de Voleibol Universitário",
    page_icon="🏐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carregar dados uma vez para toda a aplicação
@st.cache_data
def load_data():
    return pd.read_csv('dataset_full.csv')

# Dicionário de tradução
TRANSLATIONS = {
    'a': 'Time A', 'b': 'Time B',
    'jump': 'Saque com Salto', 'float': 'Saque Flutuante', 'hybrid': 'Saque Híbrido',
    'hit': 'Ataque Forte', 'off_speed': 'Ataque Controlado', 'tip': 'Largada',
    'roll_shot': 'Roll Shot', 'free_ball': 'Bola Livre', 'overpass': 'Sobrepasse',
    'kill': 'Kill', 'ace': 'Ace', 'tool': 'Tool', 'blocked': 'Ponto de Bloqueio',
    'hit_error': 'Erro de Ataque', 'serve_error': 'Erro de Saque', 'net': 'Rede',
    'in': 'Dentro', 'out': 'Fora'
}

def translate_value(value):
    if pd.isna(value): return 'Não informado'
    return TRANSLATIONS.get(str(value), str(value))

# Carregar e preparar dados
df = load_data()
df['team_pt'] = df['team'].apply(translate_value)
df['serve_type_pt'] = df['serve_type'].apply(translate_value)
df['hit_type_pt'] = df['hit_type'].apply(translate_value)
df['win_reason_pt'] = df['win_reason'].apply(translate_value)

# Sidebar global
st.sidebar.title("🏐 Navegação")
st.sidebar.markdown("Selecione a página para análise:")

st.sidebar.markdown("---")
st.sidebar.title("⚙️ Filtros Globais")

# Filtros que se aplicam a todas as páginas
times_selecionados = st.sidebar.multiselect(
    "Selecione os times:",
    options=df['team_pt'].unique(),
    default=df['team_pt'].unique()
)

# Aplicar filtro global
df_filtrado = df[df['team_pt'].isin(times_selecionados)] if times_selecionados else df

# Armazenar dados filtrados na session state para usar em outras páginas
st.session_state.df_filtrado = df_filtrado
st.session_state.translate_value = translate_value

# Página Principal
st.title("🏐 Análise Tática de Voleibol Universitário")
st.markdown("---")

st.markdown("""
## 📖 Sobre este Dashboard

Este projeto apresenta uma análise completa de dados reais da liga universitária feminina de voleibol, 
com **2.000+ registros** de partidas. Através de visualizações interativas, exploramos os padrões táticos 
que definem o jogo moderno.

### 🎯 Objetivo do Dashboard

- **Identificar padrões** ofensivos e defensivos das equipes
- **Analisar eficiência** em diferentes fases do jogo  
- **Fornecer insights** para tomada de decisão técnica
- **Visualizar tendências** através de dados históricos

### 🧭 Como Navegar

Utilize a **barra lateral** para:
- 🔍 **Selecionar páginas** específicas de análise
- ⚙️ **Aplicar filtros** que se refletem em todas as visualizações
- 📊 **Explorar gráficos** interativos com diferentes perspectivas

### 📈 Estrutura das Análises

1. **🎯 Saque** - Primeira arma ofensiva
2. **⚡ Ataque** - Eficiência e escolhas ofensivas  
3. **🛡️ Defesa** - Organização e bloqueio
4. **📊 Análise Geral** - Visão integrada do jogo
5. **📁 Dataset** - Dados brutos e metadados

### 📊 Sobre os Dados

- **Fonte**: Liga Universitária Feminina de Voleibol
- **Período**: Temporada 2023-2024
- **Amostra**: 2.000+ ralis analisados
- **Variáveis**: 15+ métricas por jogada
""")

# Métricas rápidas na página inicial
st.markdown("---")
st.subheader("📈 Visão Geral dos Dados Filtrados")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_rallys = len(df_filtrado)
    st.metric("Total de Ralis", total_rallys)

with col2:
    aces = len(df_filtrado[df_filtrado['win_reason'] == 'ace'])
    st.metric("Aces", aces)

with col3:
    kills = len(df_filtrado[df_filtrado['win_reason'] == 'kill'])
    st.metric("Kills", kills)

with col4:
    rallies_complexos = len(df_filtrado[df_filtrado['round'] > 2])
    st.metric("Ralis Complexos", rallies_complexos)

st.info("💡 **Dica**: Use os filtros na sidebar para refinar sua análise. As seleções se aplicam a todas as páginas!")