import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Análise de Saque", layout="wide")

st.title("🎯 Análise de Saque")
st.markdown("Explore as estratégias e eficácia do primeiro ataque")

# Recuperar dados da session state
if 'df_filtrado' not in st.session_state:
    st.error("Por favor, volte à página inicial para carregar os dados.")
    st.stop()

df = st.session_state.df_filtrado

# Filtros específicos para saque
st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Filtros de Saque")

tipos_saque = df['serve_type_pt'].dropna().unique()
tipos_selecionados = st.sidebar.multiselect(
    "Tipos de saque:",
    options=tipos_saque,
    default=tipos_saque
)

df_saque = df[df['serve_type_pt'].isin(tipos_selecionados)] if tipos_selecionados else df

# Layout principal
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribuição de Tipos de Saque")
    
    if not df_saque.empty:
        serve_dist = df_saque['serve_type_pt'].value_counts()
        fig1 = px.pie(
            values=serve_dist.values,
            names=serve_dist.index,
            title="Estratégias de Saque Utilizadas",
            hole=0.4
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("Nenhum dado disponível com os filtros atuais.")

with col2:
    st.subheader("Eficácia do Saque por Time")
    
    # Gráfico interativo com slider
    min_rallys = st.slider("Mínimo de ralis por time:", 1, 100, 10)
    
    team_serve_stats = df_saque.groupby('team_pt').agg({
        'win_reason': lambda x: (x == 'ace').sum(),
        'lose_reason': lambda x: (x == 'serve_error').sum()
    }).reset_index()
    
    team_serve_stats = team_serve_stats[team_serve_stats['win_reason'] + team_serve_stats['lose_reason'] >= min_rallys]
    
    if not team_serve_stats.empty:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name='Aces', x=team_serve_stats['team_pt'], y=team_serve_stats['win_reason']))
        fig2.add_trace(go.Bar(name='Erros', x=team_serve_stats['team_pt'], y=team_serve_stats['lose_reason']))
        fig2.update_layout(barmode='group', title=f"Desempenho no Saque (≥{min_rallys} ralis)")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Ajuste o filtro mínimo de ralis.")

# Análise de localização de saque
st.subheader("📍 Padrões de Localização")

col3, col4 = st.columns(2)

with col3:
    st.markdown("**Zonas de Recepção Mais Frequentes**")
    receive_heat = df_saque['receive_location'].value_counts().head(10)
    if not receive_heat.empty:
        fig3 = px.bar(
            x=receive_heat.values,
            y=receive_heat.index.astype(str),
            orientation='h',
            title="Zonas de Recepção"
        )
        st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown("**Evolução por Rally**")
    rally_slice = st.slider("Selecione o número do rally:", 1, 10, 1)
    
    rally_data = df_saque[df_saque['rally'] == rally_slice]
    if not rally_data.empty:
        st.dataframe(rally_data[['team_pt', 'serve_type_pt', 'win_reason_pt']].head())
    else:
        st.info(f"Nenhum dado para rally {rally_slice}")

st.markdown("---")
st.info("""
**💡 Insights sobre Saque:**
- Saques com salto tendem a gerar mais aces mas também mais erros
- A escolha do tipo de saque varia conforme a equipe e o momento do jogo
- Zonas específicas de recepção podem indicar estratégias de posicionamento
""")