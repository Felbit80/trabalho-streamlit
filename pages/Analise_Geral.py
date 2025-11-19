import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

st.set_page_config(page_title="Análise Geral", layout="wide")

st.title("📊 Análise Geral Integrada")
st.markdown("Visão completa do desempenho das equipes")

if 'df_filtrado' not in st.session_state:
    st.error("Por favor, volte à página inicial para carregar os dados.")
    st.stop()

df = st.session_state.df_filtrado

# Métricas consolidadas
st.subheader("🏆 Performance Consolidada")

col1, col2, col3, col4 = st.columns(4)

with col1:
    win_rate_a = len(df[(df['winning_team'] == 'a') & (df['team_pt'] == 'Time A')]) / len(df[df['team_pt'] == 'Time A']) * 100
    st.metric("Time A - Taxa de Vitória", f"{win_rate_a:.1f}%")

with col2:
    win_rate_b = len(df[(df['winning_team'] == 'b') & (df['team_pt'] == 'Time B')]) / len(df[df['team_pt'] == 'Time B']) * 100
    st.metric("Time B - Taxa de Vitória", f"{win_rate_b:.1f}%")

with col3:
    avg_rally_length = df['round'].mean()
    st.metric("Duração Média do Rally", f"{avg_rally_length:.1f} ações")

with col4:
    efficiency_diff = abs(win_rate_a - win_rate_b)
    st.metric("Diferença de Eficiência", f"{efficiency_diff:.1f}%")

# Dashboard interativo
st.subheader("📈 Dashboard de Performance")

# Seleção de métrica para análise comparativa
metric_option = st.selectbox(
    "Selecione a métrica para análise:",
    ['win_reason', 'hit_type', 'serve_type', 'num_blockers']
)

col5, col6 = st.columns(2)

with col5:
    # Heatmap de performance
    st.markdown("**Mapa de Calor de Performance**")
    
    performance_data = df.groupby(['team_pt', metric_option]).size().unstack(fill_value=0)
    if not performance_data.empty:
        fig1 = px.imshow(
            performance_data,
            title=f"Performance por Time - {metric_option}",
            aspect="auto",
            color_continuous_scale="viridis"
        )
        st.plotly_chart(fig1, use_container_width=True)

with col6:
    # Evolução temporal
    st.markdown("**Evolução por Rally**")
    
    rally_range = st.slider("Intervalo de rallys:", 1, 50, (1, 10))
    rally_data = df[(df['rally'] >= rally_range[0]) & (df['rally'] <= rally_range[1])]
    
    rally_stats = rally_data.groupby('rally').agg({
        'winning_team': 'count',
        'round': 'mean'
    }).reset_index()
    
    if not rally_stats.empty:
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig2.add_trace(
            go.Scatter(x=rally_stats['rally'], y=rally_stats['winning_team'], name="Ralis"),
            secondary_y=False,
        )
        
        fig2.add_trace(
            go.Scatter(x=rally_stats['rally'], y=rally_stats['round'], name="Duração Média"),
            secondary_y=True,
        )
        
        fig2.update_layout(title_text="Evolução do Jogo por Rally")
        st.plotly_chart(fig2, use_container_width=True)

# Análise de correlação
st.subheader("🔗 Análise de Correlações")

col7, col8 = st.columns(2)

with col7:
    st.markdown("**Relação entre Variáveis**")
    
    # Criar matriz numérica para correlação
    numeric_df = df.select_dtypes(include=['number'])
    if not numeric_df.empty:
        fig3 = px.imshow(
            numeric_df.corr(),
            title="Matriz de Correlação",
            color_continuous_scale="RdBu",
            aspect="auto"
        )
        st.plotly_chart(fig3, use_container_width=True)

with col8:
    st.markdown("**Fatores de Sucesso**")
    
    success_factors = []
    for col in ['num_blockers', 'round']:
        if col in df.columns:
            correlation = df[df['win_reason'] == 'kill'][col].mean() - df[df['lose_reason'] == 'hit_error'][col].mean()
            success_factors.append({'Fator': col, 'Impacto': correlation})
    
    if success_factors:
        factors_df = pd.DataFrame(success_factors)
        fig4 = px.bar(
            factors_df,
            x='Fator',
            y='Impacto',
            title="Impacto nos Resultados",
            color='Impacto',
            color_continuous_scale='balance'
        )
        st.plotly_chart(fig4, use_container_width=True)

# Insights automáticos
st.markdown("---")
st.subheader("💡 Insights Automáticos")

col9, col10 = st.columns(2)

with col9:
    st.info("**🎯 Padrões Ofensivos**")
    
    # Insight 1: Tipo de ataque mais efetivo
    best_attack = df[df['win_reason'] == 'kill']['hit_type_pt'].mode()
    if not best_attack.empty:
        st.write(f"- Ataque mais efetivo: **{best_attack.iloc[0]}**")
    
    # Insight 2: Saque mais perigoso
    dangerous_serve = df[df['win_reason'] == 'ace']['serve_type_pt'].mode()
    if not dangerous_serve.empty:
        st.write(f"- Saque mais perigoso: **{dangerous_serve.iloc[0]}**")

with col10:
    st.info("**🛡️ Padrões Defensivos**")
    
    # Insight 3: Estratégia de bloqueio
    common_block = df['num_blockers'].mode()
    if not common_block.empty:
        st.write(f"- Bloqueio mais comum: **{int(common_block.iloc[0])} bloqueadores**")
    
    # Insight 4: Rally ideal
    optimal_rally = df[df['win_reason'] == 'kill']['round'].median()
    st.write(f"- Duração ideal do rally: **{optimal_rally:.0f} ações**")

st.markdown("---")
st.success("""
**📋 Resumo Executivo:**
Esta análise revela os padrões fundamentais que diferenciam equipes de alto desempenho. 
Os dados mostram que a eficiência não está apenas nas ações individuais, mas na 
integração coerente entre saque, ataque e defesa.
""")