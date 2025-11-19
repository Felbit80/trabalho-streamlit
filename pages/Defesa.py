import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Análise de Defesa", layout="wide")

st.title("🛡️ Análise de Defesa")
st.markdown("Estratégias defensivas e eficácia no bloqueio")

if 'df_filtrado' not in st.session_state:
    st.error("Por favor, volte à página inicial para carregar os dados.")
    st.stop()

df = st.session_state.df_filtrado

# Filtros específicos para defesa
st.sidebar.markdown("---")
st.sidebar.subheader("🛡️ Filtros de Defesa")

num_blockers_options = df['num_blockers'].dropna().unique()
blockers_selecionados = st.sidebar.multiselect(
    "Número de bloqueadores:",
    options=num_blockers_options,
    default=num_blockers_options
)

df_defesa = df[df['num_blockers'].isin(blockers_selecionados)] if blockers_selecionados else df

# Layout principal
col1, col2 = st.columns(2)

with col1:
    st.subheader("Estratégias de Bloqueio")
    
    blockers_dist = df_defesa['num_blockers'].value_counts().sort_index()
    fig1 = px.bar(
        x=blockers_dist.index.astype(str),
        y=blockers_dist.values,
        title="Distribuição de Bloqueadores por Ataque",
        color=blockers_dist.values,
        color_continuous_scale='blues'
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Toques no Bloqueio")
    
    block_touch_dist = df_defesa['block_touch'].value_counts()
    fig2 = px.pie(
        values=block_touch_dist.values,
        names=block_touch_dist.index,
        title="Frequência de Toques no Bloqueio",
        hole=0.3
    )
    st.plotly_chart(fig2, use_container_width=True)

# Análise de eficácia
st.subheader("📊 Eficácia Defensiva por Time")

col3, col4 = st.columns(2)

with col3:
    st.markdown("**Pontos de Bloqueio por Time**")
    
    block_points = df_defesa[df_defesa['win_reason'] == 'blocked']['team_pt'].value_counts()
    if not block_points.empty:
        fig3 = px.bar(
            x=block_points.values,
            y=block_points.index,
            orientation='h',
            title="Pontos Diretos de Bloqueio",
            color=block_points.values
        )
        st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown("**Relação Bloqueio vs Ataque**")
    
    # Slider interativo para análise
    min_actions = st.slider("Mínimo de ações defensivas:", 1, 50, 10)
    
    defense_stats = df_defesa.groupby('team_pt').agg({
        'win_reason': lambda x: (x == 'blocked').sum(),
        'num_blockers': 'count'
    }).reset_index()
    
    defense_stats = defense_stats[defense_stats['num_blockers'] >= min_actions]
    defense_stats['Eficiência'] = defense_stats['win_reason'] / defense_stats['num_blockers'] * 100
    
    if not defense_stats.empty:
        fig4 = px.scatter(
            defense_stats,
            x='num_blockers',
            y='Eficiência',
            size='win_reason',
            color='team_pt',
            hover_name='team_pt',
            title="Eficiência do Bloqueio vs Volume Defensivo",
            size_max=30
        )
        st.plotly_chart(fig4, use_container_width=True)

# Análise de rallys defensivos
st.subheader("🔄 Comportamento em Rallys Longos")

col5, col6 = st.columns(2)

with col5:
    st.markdown("**Defesa em Rallys Complexos**")
    complex_rallies = df_defesa[df_defesa['round'] > 2]
    
    if not complex_rallies.empty:
        block_complex = complex_rallies['num_blockers'].value_counts().sort_index()
        fig5 = px.line(
            x=block_complex.index.astype(str),
            y=block_complex.values,
            title="Estratégia de Bloqueio em Rallys Longos",
            markers=True
        )
        st.plotly_chart(fig5, use_container_width=True)

with col6:
    st.markdown("**Evolução Defensiva**")
    
    # Seleção interativa de métrica
    metric = st.selectbox("Selecione a métrica:", ['num_blockers', 'block_touch'])
    
    rally_evolution = df_defesa.groupby('rally')[metric].mean().reset_index()
    if not rally_evolution.empty:
        fig6 = px.area(
            rally_evolution,
            x='rally',
            y=metric,
            title=f"Evolução de {metric} por Rally"
        )
        st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")
st.info("""
**💡 Insights sobre Defesa:**
- Bloqueio triplo é mais comum em situações de ataque forte
- Times com maior volume defensivo nem sempre são os mais eficientes
- Rallys longos tendem a ter estratégias de bloqueio mais conservadoras
- Toques no bloqueio frequentemente resultam em transição ofensiva
""")