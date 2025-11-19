import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Análise de Ataque", layout="wide")

st.title("⚡ Análise de Ataque")
st.markdown("Eficiência e padrões ofensivos das equipes")

if 'df_filtrado' not in st.session_state:
    st.error("Por favor, volte à página inicial para carregar os dados.")
    st.stop()

df = st.session_state.df_filtrado

# Filtros específicos para ataque
st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Filtros de Ataque")

tipos_ataque = df['hit_type_pt'].dropna().unique()
tipos_ataque_selecionados = st.sidebar.multiselect(
    "Tipos de ataque:",
    options=tipos_ataque,
    default=tipos_ataque
)

df_ataque = df[df['hit_type_pt'].isin(tipos_ataque_selecionados)] if tipos_ataque_selecionados else df

# Métricas de ataque
col1, col2, col3 = st.columns(3)

with col1:
    kill_rate = len(df_ataque[df_ataque['win_reason'] == 'kill']) / len(df_ataque) * 100
    st.metric("Taxa de Kill", f"{kill_rate:.1f}%")

with col2:
    erro_rate = len(df_ataque[df_ataque['lose_reason'] == 'hit_error']) / len(df_ataque) * 100
    st.metric("Taxa de Erro", f"{erro_rate:.1f}%")

with col3:
    tool_rate = len(df_ataque[df_ataque['win_reason'] == 'tool']) / len(df_ataque) * 100
    st.metric("Taxa de Tool", f"{tool_rate:.1f}%")

# Gráficos principais
col4, col5 = st.columns(2)

with col4:
    st.subheader("Preferências de Ataque por Time")
    
    # Gráfico interativo com seleção de time
    team_attack = st.selectbox("Selecione o time:", df_ataque['team_pt'].unique())
    
    team_data = df_ataque[df_ataque['team_pt'] == team_attack]
    attack_dist = team_data['hit_type_pt'].value_counts()
    
    if not attack_dist.empty:
        fig1 = px.bar(
            x=attack_dist.values,
            y=attack_dist.index,
            orientation='h',
            title=f"Tipos de Ataque - {team_attack}",
            color=attack_dist.values,
            color_continuous_scale='viridis'
        )
        st.plotly_chart(fig1, use_container_width=True)

with col5:
    st.subheader("Eficácia por Tipo de Ataque")
    
    # Calcular eficácia por tipo de ataque
    attack_stats = []
    for attack_type in df_ataque['hit_type_pt'].unique():
        subset = df_ataque[df_ataque['hit_type_pt'] == attack_type]
        kills = len(subset[subset['win_reason'] == 'kill'])
        errors = len(subset[subset['lose_reason'] == 'hit_error'])
        total = len(subset)
        efficiency = (kills - errors) / total * 100 if total > 0 else 0
        
        attack_stats.append({
            'Tipo': attack_type,
            'Eficiência': efficiency,
            'Total': total
        })
    
    attack_df = pd.DataFrame(attack_stats)
    attack_df = attack_df[attack_df['Total'] > 5]  # Filtrar tipos com amostra significativa
    
    if not attack_df.empty:
        fig2 = px.scatter(
            attack_df, 
            x='Total', 
            y='Eficiência',
            size='Total',
            color='Eficiência',
            hover_name='Tipo',
            title="Eficiência vs Frequência dos Tipos de Ataque",
            size_max=50
        )
        st.plotly_chart(fig2, use_container_width=True)

# Análise de localização
st.subheader("🎯 Padrões de Finalização")

col6, col7 = st.columns(2)

with col6:
    st.markdown("**Zonas de Aterrissagem**")
    location_data = df_ataque['hit_land_location'].value_counts().head(15)
    if not location_data.empty:
        fig3 = px.bar(
            x=location_data.index.astype(str),
            y=location_data.values,
            title="Zonas Preferidas para Finalização"
        )
        st.plotly_chart(fig3, use_container_width=True)

with col7:
    st.markdown("**Evolução do Ataque por Set**")
    set_data = df_ataque.groupby('rally').agg({
        'win_reason': lambda x: (x == 'kill').sum(),
        'lose_reason': lambda x: (x == 'hit_error').sum()
    }).reset_index()
    
    if not set_data.empty:
        fig4 = px.line(
            set_data, 
            x='rally', 
            y=['win_reason', 'lose_reason'],
            title="Kills e Erros por Rally",
            labels={'value': 'Quantidade', 'variable': 'Tipo'}
        )
        st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.info("""
**💡 Insights sobre Ataque:**
- Ataques fortes têm maior taxa de kill mas também maior risco
- Times diferentes mostram preferências por tipos específicos de ataque
- Zonas 4 e 1 são as mais utilizadas para finalização
- A eficiência tende a cair em rallies mais longos
""")