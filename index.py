import streamlit as st
import pandas as pd
from plotly.subplots import make_subplots

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("Plotly não está disponível. Alguns gráficos podem não funcionar.")

# Configuração da página
st.set_page_config(
    page_title="Análise de Voleibol Universitário Feminino",
    page_icon="🏐",
    layout="wide"
)

# Dicionários para tradução
TRANSLATIONS = {
    # Times
    'a': 'Time A',
    'b': 'Time B',
    
    # Tipos de saque
    'jump': 'Saque com Salto',
    'float': 'Saque Flutuante', 
    'hybrid': 'Saque Híbrido',
    'tape': 'Saque por Baixo',
    
    # Tipos de ataque
    'hit': 'Ataque Forte',
    'off_speed': 'Ataque Controlado',
    'tip': 'Largada',
    'roll_shot': 'Roll Shot',
    'free_ball': 'Bola Livre',
    'overpass': 'Sobrepasse',
    'blocked': 'Bloqueado',
    
    # Razões de vitória
    'kill': 'Kill',
    'ace': 'Ace',
    'tool': 'Tool (ataque no bloqueio)',
    'blocked': 'Ponto de Bloqueio',
    'hit_error': 'Erro de Ataque',
    'serve_error': 'Erro de Saque',
    'net': 'Rede',
    
    # Avaliações de passe
    'in': 'Dentro',
    'out': 'Fora'
}

@st.cache_data
def load_data():
    df = pd.read_csv('dataset_full.csv')
    return df

def translate_value(value, category):
    """Traduz valores específicos para português"""
    if pd.isna(value):
        return 'Não informado'
    return TRANSLATIONS.get(str(value), str(value))

def safe_plotting(func):
    """Decorator para tratamento seguro de erros nos gráficos"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            st.error(f"Erro ao gerar gráfico: {str(e)}")
            st.info("Tente ajustar os filtros ou verificar os dados disponíveis.")
            return None
    return wrapper

# Carregar dados
try:
    df = load_data()
    
    # Aplicar traduções
    df['team_pt'] = df['team'].apply(lambda x: translate_value(x, 'team'))
    df['serve_type_pt'] = df['serve_type'].apply(lambda x: translate_value(x, 'serve_type'))
    df['hit_type_pt'] = df['hit_type'].apply(lambda x: translate_value(x, 'hit_type'))
    df['win_reason_pt'] = df['win_reason'].apply(lambda x: translate_value(x, 'win_reason'))
    df['block_touch_pt'] = df['block_touch'].apply(lambda x: translate_value(x, 'block_touch'))
    
except Exception as e:
    st.error(f"Erro ao carregar os dados: {str(e)}")
    st.stop()

# Sidebar com filtros
st.sidebar.title("⚙️ Filtros de Análise")
st.sidebar.markdown("Use os filtros para explorar a performance das equipes:")

# Filtros com valores traduzidos
times_disponiveis = df['team_pt'].dropna().unique()
tipos_saque_disponiveis = df['serve_type_pt'].dropna().unique()

times_selecionados = st.sidebar.multiselect(
    "Selecione os times:",
    options=times_disponiveis,
    default=times_disponiveis
)

tipos_saque_selecionados = st.sidebar.multiselect(
    "Tipos de saque:",
    options=tipos_saque_disponiveis,
    default=tipos_saque_disponiveis
)

# Aplicar filtros
df_filtrado = df.copy()
if times_selecionados:
    df_filtrado = df_filtrado[df_filtrado['team_pt'].isin(times_selecionados)]
if tipos_saque_selecionados:
    df_filtrado = df_filtrado[df_filtrado['serve_type_pt'].isin(tipos_saque_selecionados)]

# Verificar se há dados após filtragem
if df_filtrado.empty:
    st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados. Tente ajustar os critérios.")
    st.stop()

# Layout principal
st.title("🏐 Análise Tática: Voleibol Universitário Feminino")
st.markdown("""
**Explore as estratégias e performances das equipes através de dados reais da liga universitária feminina.**
Esta análise revela padrões táticos, eficiência ofensiva e momentos decisivos que definem o resultado das partidas.
""")

# Seção 1: Visão Geral - O Cenário da Partida
st.header("📈 Visão Geral do Jogo")
st.markdown("""
*Entenda o contexto geral da partida e a distribuição fundamental das jogadas.*
""")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_rallys = len(df_filtrado)
    st.metric("Total de Ralis Analisados", total_rallys)

with col2:
    aces = len(df_filtrado[df_filtrado['win_reason'] == 'ace'])
    st.metric("Aces", aces, help="Saque que resulta diretamente em ponto")

with col3:
    kills = len(df_filtrado[df_filtrado['win_reason'] == 'kill'])
    st.metric("Kills", kills, help="Ataque que resulta diretamente em ponto")

with col4:
    rallies_longos = len(df_filtrado[df_filtrado['round'] > 2])
    st.metric("Ralis Longos (>2 ações)", rallies_longos)

# Seção 2: A Batalha do Saque
st.header("🎯 A Batalha do Saque")
st.markdown("""
*O saque é a primeira arma ofensiva. Veja como cada equipe utiliza diferentes estratégias de saque.*
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribuição de Tipos de Saque")
    
    @safe_plotting
    def plot_tipos_saque():
        serve_dist = df_filtrado['serve_type_pt'].value_counts()
        if serve_dist.empty:
            st.info("Nenhum dado de saque disponível com os filtros atuais.")
            return
            
        fig = px.pie(
            values=serve_dist.values,
            names=serve_dist.index,
            title="Estratégias de Saque Utilizadas"
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    plot_tipos_saque()

with col2:
    st.subheader("Eficiência do Saque por Time")
    
    @safe_plotting
    def plot_eficacia_saque():
        # Calcular eficácia do saque (aces vs erros)
        saque_stats = df_filtrado.groupby('team_pt').agg({
            'win_reason': lambda x: (x == 'ace').sum(),
            'lose_reason': lambda x: (x == 'serve_error').sum()
        }).reset_index()
        
        if saque_stats.empty:
            st.info("Dados insuficientes para análise de eficácia de saque.")
            return
            
        saque_stats['Aces'] = saque_stats['win_reason']
        saque_stats['Erros'] = saque_stats['lose_reason']
        
        fig = go.Figure(data=[
            go.Bar(name='Aces', x=saque_stats['team_pt'], y=saque_stats['Aces']),
            go.Bar(name='Erros', x=saque_stats['team_pt'], y=saque_stats['Erros'])
        ])
        fig.update_layout(barmode='group', title="Aces vs Erros de Saque por Time")
        st.plotly_chart(fig, use_container_width=True)
    
    plot_eficacia_saque()

# Seção 3: O Ataque - A Hora da Decisão
st.header("💥 O Ataque: A Hora da Decisão")
st.markdown("""
*Analise as escolhas ofensivas das equipes e sua eficácia em finalizar os pontos.*
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Preferências de Ataque")
    
    @safe_plotting
    def plot_tipos_ataque():
        attack_dist = df_filtrado['hit_type_pt'].value_counts().head(8)
        if attack_dist.empty:
            st.info("Nenhum dado de ataque disponível.")
            return
            
        fig = px.bar(
            x=attack_dist.values,
            y=attack_dist.index,
            orientation='h',
            title="Tipos de Ataque Mais Utilizados",
            labels={'x': 'Quantidade', 'y': 'Tipo de Ataque'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    plot_tipos_ataque()

with col2:
    st.subheader("Eficiência Ofensiva por Time")
    
    @safe_plotting
    def plot_eficacia_ataque():
        # Kills vs Erros de ataque
        ataque_stats = df_filtrado.groupby('team_pt').agg({
            'win_reason': lambda x: (x == 'kill').sum(),
            'lose_reason': lambda x: (x == 'hit_error').sum()
        }).reset_index()
        
        if ataque_stats.empty:
            st.info("Dados insuficientes para análise de eficácia ofensiva.")
            return
            
        ataque_stats['Kills'] = ataque_stats['win_reason']
        ataque_stats['Erros'] = ataque_stats['lose_reason']
        
        fig = px.bar(
            ataque_stats, 
            x='team_pt', 
            y=['Kills', 'Erros'],
            title="Kills vs Erros de Ataque por Time",
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    plot_eficacia_ataque()

# Seção 4: A Defesa - A Arte do Bloqueio
st.header("🛡️ A Defesa: A Arte do Bloqueio")
st.markdown("""
*Explore como as equipes se organizam defensivamente e a eficácia do bloqueio.*
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Estratégias de Bloqueio")
    
    @safe_plotting
    def plot_estrategia_bloqueio():
        bloqueio_stats = df_filtrado['num_blockers'].value_counts().sort_index()
        if bloqueio_stats.empty:
            st.info("Nenhum dado de bloqueio disponível.")
            return
            
        fig = px.bar(
            x=bloqueio_stats.index,
            y=bloqueio_stats.values,
            title="Distribuição de Bloqueadores por Ataque",
            labels={'x': 'Número de Bloqueadores', 'y': 'Quantidade'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    plot_estrategia_bloqueio()

with col2:
    st.subheader("Toques no Bloqueio")
    
    @safe_plotting
    def plot_toques_bloqueio():
        touch_stats = df_filtrado['block_touch_pt'].value_counts()
        if touch_stats.empty:
            st.info("Nenhum dado de toque no bloqueio disponível.")
            return
            
        fig = px.pie(
            values=touch_stats.values,
            names=touch_stats.index,
            title="Frequência de Toques no Bloqueio"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    plot_toques_bloqueio()

# Seção 5: Análise de Localização
st.header("🗺️ Inteligência de Localização")
st.markdown("""
*Entenda os padrões de posicionamento das equipes nas diferentes fases do jogo.*
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Zonas de Recepção")
    
    @safe_plotting
    def plot_zona_recepcao():
        recepcao_data = df_filtrado['receive_location'].value_counts().head(10)
        if recepcao_data.empty:
            st.info("Nenhum dado de recepção disponível.")
            return
            
        fig = px.bar(
            x=recepcao_data.index,
            y=recepcao_data.values,
            title="Zonas Mais Frequentes de Recepção",
            labels={'x': 'Zona da Quadra', 'y': 'Quantidade'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    plot_zona_recepcao()

with col2:
    st.subheader("Zonas de Finalização")
    
    @safe_plotting
    def plot_zona_finalizacao():
        finalizacao_data = df_filtrado['hit_land_location'].value_counts().head(10)
        if finalizacao_data.empty:
            st.info("Nenhum dado de finalização disponível.")
            return
            
        fig = px.bar(
            x=finalizacao_data.index,
            y=finalizacao_data.values,
            title="Zonas Preferidas para Finalização",
            labels={'x': 'Zona da Quadra', 'y': 'Quantidade'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    plot_zona_finalizacao()

# Seção 6: Análise Detalhada - Os Números por Trás do Jogo
st.header("🔍 Análise Detalhada")
st.markdown("""
*Explore os dados brutos e métricas avançadas para insights profundos.*
""")

tab1, tab2, tab3 = st.tabs(["📊 Dados Completos", "📈 Estatísticas", "💡 Insights"])

with tab1:
    st.subheader("Base de Dados Completa")
    st.dataframe(df_filtrado, use_container_width=True)
    
    # Opção de download
    csv = df_filtrado.to_csv(index=False)
    st.download_button(
        label="📥 Baixar Dados Filtrados (CSV)",
        data=csv,
        file_name="dados_voleibol_filtrado.csv",
        mime="text/csv"
    )

with tab2:
    st.subheader("Estatísticas Descritivas")
    
    # Selecionar colunas numéricas para análise
    colunas_numericas = df_filtrado.select_dtypes(include=['number']).columns
    if not colunas_numericas.empty:
        st.dataframe(df_filtrado[colunas_numericas].describe(), use_container_width=True)
    else:
        st.info("Nenhuma coluna numérica disponível para análise estatística.")

with tab3:
    st.subheader("Principais Insights")
    
    # Insights automáticos baseados nos dados
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("🎯 **Destaque Ofensivo**")
        if not df_filtrado.empty:
            tipo_ataque_mais_efetivo = df_filtrado[df_filtrado['win_reason'] == 'kill']['hit_type_pt'].mode()
            if not tipo_ataque_mais_efetivo.empty:
                st.write(f"Ataque mais efetivo: **{tipo_ataque_mais_efetivo.iloc[0]}**")
        
        st.info("🛡️ **Estratégia Defensiva**")
        bloqueio_mais_comum = df_filtrado['num_blockers'].mode()
        if not bloqueio_mais_comum.empty:
            st.write(f"Formação de bloqueio mais comum: **{int(bloqueio_mais_comum.iloc[0])} bloqueadores**")
    
    with col2:
        st.info("⚡ **Momento Decisivo**")
        if not df_filtrado.empty:
            razao_vitoria_principal = df_filtrado['win_reason_pt'].mode()
            if not razao_vitoria_principal.empty:
                st.write(f"Principal razão de vitória: **{razao_vitoria_principal.iloc[0]}**")
        
        st.info("🎪 **Diversidade Tática**")
        tipos_ataque_unicos = df_filtrado['hit_type_pt'].nunique()
        st.write(f"Tipos de ataque diferentes: **{tipos_ataque_unicos}**")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p><strong>Análise Desenvolvida para Ciência de Dados no Esporte</strong></p>
        <p>Dados reais da liga universitária feminina de voleibol • Interface em português</p>
    </div>
    """,
    unsafe_allow_html=True
)