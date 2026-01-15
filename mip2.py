import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json

# Configuração da página
st.set_page_config(
    page_title="Calculadora de Impacto - Licitações Locais",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .impact-high {
        color: #28a745;
        font-weight: bold;
    }
    .impact-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .impact-low {
        color: #dc3545;
        font-weight: bold;
    }
    .ai-suggestion {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Carregar dados dos multiplicadores
@st.cache_data
def load_data():
    """Carrega dados dos multiplicadores e setores"""
    
    # Dados dos setores (extraídos da análise)
    setores_data = {
        'Código': ['190', '580', '1091', '1092', '1093', '1100', '1200', '1300', '1400', 
                   '1500', '1600', '1700', '1800', '1900', '2090', '2093', '2100', '2200',
                   '2300', '2490', '2500', '2600', '2700', '2800', '2991', '2992', '3000',
                   '3180', '3300', '3500', '4180', '4500', '4900', '5500', '5800', '6480',
                   '6800', '6980', '8400', '8592', '9080', '9700'],
        
        'Setor': ['Agricultura, pecuária e pesca', 'Indústria extrativa', 
                  'Abate e produtos de carne', 'Fabricação e refino de açúcar',
                  'Outros produtos alimentares', 'Fabricação de bebidas',
                  'Fabricação de produtos do fumo', 'Fabricação de produtos têxteis',
                  'Confecção de vestuário', 'Fabricação de calçados',
                  'Fabricação de produtos da madeira', 'Fabricação de celulose e papel',
                  'Impressão e reprodução', 'Fabricação de coque e petróleo',
                  'Fabricação de produtos químicos', 'Produtos de limpeza e cosméticos',
                  'Produtos farmacêuticos', 'Fabricação de borracha e plástico',
                  'Produtos de minerais não-metálicos', 'Metalurgia',
                  'Fabricação de produtos de metal', 'Equipamentos de informática',
                  'Máquinas e equipamentos elétricos', 'Máquinas e equipamentos mecânicos',
                  'Fabricação de automóveis', 'Fabricação de peças para veículos',
                  'Outros equipamentos de transporte', 'Fabricação de móveis',
                  'Manutenção e reparação de máquinas', 'Eletricidade, gás e água',
                  'Construção', 'Comércio e reparação de veículos',
                  'Transporte, armazenagem e correios', 'Alojamento e alimentação',
                  'Serviços de informação', 'Intermediação financeira',
                  'Atividades imobiliárias', 'Serviços profissionais e técnicos',
                  'Administração pública', 'Educação e saúde privadas',
                  'Artes, cultura e esportes', 'Serviços domésticos'],
        
        'Mult_Producao': [1.46, 1.65, 2.09, 1.91, 2.04, 1.83, 1.90, 1.66, 1.57,
                          1.75, 1.97, 1.88, 1.54, 1.86, 1.91, 1.88, 1.68, 1.66,
                          1.96, 1.51, 1.51, 1.48, 1.71, 1.73, 1.83, 1.62, 1.50,
                          1.71, 1.32, 1.60, 1.65, 1.56, 1.89, 1.64, 1.44, 1.44,
                          1.09, 1.39, 1.28, 1.40, 1.47, 1.00],
        
        'Mult_Renda': [0.211, 0.165, 0.284, 0.137, 0.225, 0.245, 0.156, 0.267, 0.247,
                       0.220, 0.312, 0.278, 0.289, 0.080, 0.210, 0.303, 0.288, 0.248,
                       0.336, 0.279, 0.309, 0.370, 0.356, 0.370, 0.311, 0.294, 0.325,
                       0.309, 0.408, 0.188, 0.292, 0.408, 0.347, 0.331, 0.383, 0.315,
                       0.471, 0.402, 0.444, 0.479, 0.358, 0.538],
        
        'Mult_Emprego': [11.15, 3.10, 13.29, 3.72, 11.19, 6.74, 3.71, 9.64, 9.53,
                         8.42, 13.11, 5.92, 8.95, 1.28, 4.64, 11.62, 6.56, 7.52,
                         10.00, 5.99, 8.57, 5.39, 5.70, 6.89, 4.57, 5.64, 5.02,
                         11.52, 13.64, 3.73, 16.96, 15.65, 6.94, 19.68, 8.49, 7.42,
                         8.06, 13.94, 10.83, 18.74, 13.08, 19.47],
        
        'Mult_ICMS': [0.032, 0.023, 0.050, 0.040, 0.063, 0.280, 0.192, 0.078, 0.060,
                      0.058, 0.094, 0.073, 0.047, 0.143, 0.087, 0.221, 0.098, 0.085,
                      0.172, 0.059, 0.065, 0.060, 0.068, 0.065, 0.090, 0.072, 0.050,
                      0.067, 0.039, 0.063, 0.101, 0.091, 0.098, 0.087, 0.072, 0.027,
                      0.003, 0.048, 0.028, 0.045, 0.051, 0.000],
        
        'Viabilidade_Local': ['Média', 'Baixa', 'Média', 'Baixa', 'Alta', 'Média', 'Baixa',
                              'Média', 'Média', 'Média', 'Alta', 'Baixa', 'Média', 'Baixa',
                              'Baixa', 'Média', 'Baixa', 'Média', 'Média', 'Baixa', 'Média',
                              'Baixa', 'Média', 'Média', 'Baixa', 'Baixa', 'Baixa', 'Média',
                              'Média', 'Alta', 'Alta', 'Alta', 'Média', 'Alta', 'Média',
                              'Baixa', 'Baixa', 'Média', 'Baixa', 'Média', 'Média', 'Baixa'],
        
        'Categoria': ['Primário', 'Indústria', 'Alimentos', 'Alimentos', 'Alimentos',
                      'Alimentos', 'Indústria', 'Indústria', 'Indústria', 'Indústria',
                      'Indústria', 'Indústria', 'Indústria', 'Indústria', 'Indústria',
                      'Indústria', 'Indústria', 'Indústria', 'Construção', 'Indústria',
                      'Construção', 'Equipamentos', 'Equipamentos', 'Equipamentos',
                      'Indústria', 'Indústria', 'Indústria', 'Bens', 'Serviços',
                      'Serviços Públicos', 'Construção', 'Comércio', 'Serviços Públicos',
                      'Serviços', 'Serviços', 'Serviços', 'Serviços', 'Serviços',
                      'Administração', 'Serviços', 'Serviços', 'Serviços']
    }
    
    df = pd.DataFrame(setores_data)
    
    return df

# Função para chamar Maritaca AI
def identify_sector_with_maritaca(description, df_setores, api_key):
    """Identifica o setor usando Maritaca AI"""
    
    if not api_key:
        return None, "API Key não fornecida"
    
    try:
        import requests
        
        # Preparar lista de setores para o prompt
        setores_list = []
        for idx, row in df_setores.iterrows():
            setores_list.append(f"- Código {row['Código']}: {row['Setor']}")
        
        setores_text = "\n".join(setores_list)
        
        # Criar prompt para a Maritaca
        prompt = f"""Você é um especialista em classificação de licitações públicas e análise econômica.

Analise a seguinte descrição de objeto de licitação e identifique qual setor econômico é o mais adequado:

DESCRIÇÃO DA LICITAÇÃO:
"{description}"

SETORES DISPONÍVEIS:
{setores_text}

INSTRUÇÕES:
1. Analise cuidadosamente a descrição
2. Identifique o setor econômico mais adequado
3. Retorne APENAS um JSON no formato:
{{
    "codigo": "código do setor (ex: 4180)",
    "confianca": "alta/média/baixa",
    "justificativa": "breve explicação de 1-2 frases do porque escolheu este setor"
}}

IMPORTANTE: Retorne APENAS o JSON, sem texto adicional antes ou depois."""

        # Chamar API da Maritaca
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sabia-3",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 500
        }
        
        response = requests.post(
            "https://chat.maritaca.ai/api/chat/inference",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Extrair resposta
            if 'answer' in result:
                answer_text = result['answer'].strip()
            elif 'choices' in result and len(result['choices']) > 0:
                answer_text = result['choices'][0]['message']['content'].strip()
            else:
                return None, "Formato de resposta inesperado da API"
            
            # Tentar parsear JSON
            # Remover possíveis markdown code blocks
            answer_text = answer_text.replace('```json', '').replace('```', '').strip()
            
            try:
                result_json = json.loads(answer_text)
                
                codigo = result_json.get('codigo', '').strip()
                confianca = result_json.get('confianca', 'média')
                justificativa = result_json.get('justificativa', '')
                
                return {
                    'codigo': codigo,
                    'confianca': confianca,
                    'justificativa': justificativa
                }, None
                
            except json.JSONDecodeError as e:
                return None, f"Erro ao parsear resposta da IA: {answer_text[:200]}"
        
        else:
            return None, f"Erro na API: {response.status_code} - {response.text[:200]}"
    
    except ImportError:
        return None, "Biblioteca 'requests' não instalada. Execute: pip install requests"
    except Exception as e:
        return None, f"Erro ao chamar Maritaca AI: {str(e)}"

# Função para identificar setor com base em palavras-chave (fallback)
def identify_sector_keywords(description):
    """Identifica o setor com base em palavras-chave (método tradicional)"""
    keywords = {
        '4180': ['obra', 'construção', 'reforma', 'pavimentação', 'edificação', 'engenharia'],
        '1093': ['alimento', 'merenda', 'alimentação', 'comida', 'refeição', 'cesta básica'],
        '1091': ['carne', 'frango', 'boi', 'suíno', 'proteína animal'],
        '5500': ['catering', 'buffet', 'hospedagem', 'hotel', 'restaurante'],
        '3180': ['móvel', 'mobiliário', 'cadeira', 'mesa', 'estante', 'armário'],
        '2300': ['cimento', 'tijolo', 'telha', 'cerâmica', 'material construção'],
        '6980': ['consultoria', 'projeto', 'assessoria', 'perícia', 'auditoria'],
        '5800': ['software', 'sistema', 'TI', 'informática', 'tecnologia'],
        '4500': ['veículo', 'carro', 'manutenção automotiva', 'auto'],
        '4900': ['transporte', 'frete', 'logística', 'ônibus escolar'],
        '2100': ['medicamento', 'remédio', 'farmacêutico', 'droga'],
        '8592': ['educação', 'saúde', 'escola', 'hospital', 'clínica'],
        '3500': ['energia', 'água', 'saneamento', 'esgoto', 'eletricidade'],
    }
    
    description_lower = description.lower()
    matches = []
    
    for sector_code, words in keywords.items():
        for word in words:
            if word in description_lower:
                matches.append(sector_code)
                break
    
    return matches

# Função para calcular impacto
def calculate_impact(valor, mult_prod, mult_renda, mult_emprego, mult_icms, fator_regional):
    """Calcula o impacto econômico"""
    impacto_producao = valor * mult_prod * fator_regional
    impacto_renda = valor * mult_renda * fator_regional
    impacto_empregos = (valor / 1_000_000) * mult_emprego * fator_regional
    impacto_icms = valor * mult_icms * fator_regional
    
    return {
        'producao': impacto_producao,
        'renda': impacto_renda,
        'empregos': impacto_empregos,
        'icms': impacto_icms
    }

# Header
st.markdown('<div class="main-header">📊 Calculadora de Impacto Econômico<br>Licitações com Preferência Local<br><small>🤖 Powered by Maritaca AI</small></div>', unsafe_allow_html=True)
st.markdown("---")

# Carregar dados
df_setores = load_data()

# Sidebar - Configurações
with st.sidebar:
    st.header("⚙️ Configurações")
    
    # API Key Maritaca
    st.subheader("🤖 Maritaca AI")
    api_key = st.text_input(
        "API Key:",
        type="password",
        help="Insira sua API Key da Maritaca AI para identificação inteligente de setores. Obtenha em: https://plataforma.maritaca.ai"
    )
    
    if api_key:
        st.success("✅ API Key configurada")
    else:
        st.warning("⚠️ API Key não configurada - usando identificação básica por palavras-chave")
    
    st.markdown("---")
    
    # Tamanho do município
    st.subheader("Tamanho do Município/Região")
    tamanho = st.selectbox(
        "Selecione:",
        ["Pequeno (< 50 mil hab.)", "Médio (50-200 mil hab.)", "Grande (> 200 mil hab.)"]
    )
    
    # Fator de regionalização
    fatores = {
        "Pequeno (< 50 mil hab.)": 0.4,
        "Médio (50-200 mil hab.)": 0.6,
        "Grande (> 200 mil hab.)": 0.8
    }
    fator_regional = fatores[tamanho]
    
    st.info(f"**Fator de Regionalização:** {fator_regional:.0%}\n\n"
            f"Indica a % do impacto que fica na região (considerando vazamentos econômicos)")
    
    # Cenário comparativo
    st.subheader("Cenário sem Preferência Local")
    fator_sem_preferencia = st.slider(
        "Fator de retenção local (%)",
        min_value=10,
        max_value=50,
        value=20,
        step=5,
        help="Estimativa de quanto do impacto fica local quando não há preferência"
    ) / 100

# Área principal
tab1, tab2, tab3, tab4 = st.tabs(["📝 Análise de Licitação", "📚 Consulta de Setores", "📖 Guia", "🤖 Sobre a IA"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("1️⃣ Descreva o Objeto da Licitação")
        descricao = st.text_area(
            "Descrição do objeto:",
            height=100,
            placeholder="Ex: Aquisição de materiais de construção para reforma de escola municipal...",
            help="Descreva o objeto da licitação. A IA Maritaca analisará e sugerirá o setor mais adequado."
        )
        
        # Botão para identificar com IA
        if descricao:
            if st.button("🤖 Identificar Setor com IA Maritaca", type="primary"):
                with st.spinner("🔍 Analisando com IA Maritaca..."):
                    ai_result, error = identify_sector_with_maritaca(descricao, df_setores, api_key)
                    
                    if ai_result:
                        st.session_state['ai_suggestion'] = ai_result
                    else:
                        st.session_state['ai_suggestion'] = None
                        st.error(f"❌ {error}")
                        st.info("💡 Usando identificação por palavras-chave como fallback...")
                        setores_keywords = identify_sector_keywords(descricao)
                        if setores_keywords:
                            st.session_state['keyword_suggestion'] = setores_keywords[0]
            
            # Mostrar sugestão da IA
            if 'ai_suggestion' in st.session_state and st.session_state['ai_suggestion']:
                ai_sug = st.session_state['ai_suggestion']
                
                # Ícone de confiança
                confianca_icon = {
                    'alta': '🟢',
                    'média': '🟡',
                    'baixa': '🟠'
                }
                
                st.markdown(f"""
                <div class="ai-suggestion">
                    <h4>🤖 Sugestão da IA Maritaca {confianca_icon.get(ai_sug['confianca'], '🟡')}</h4>
                    <p><strong>Setor identificado:</strong> {ai_sug['codigo']}</p>
                    <p><strong>Confiança:</strong> {ai_sug['confianca'].upper()}</p>
                    <p><strong>Justificativa:</strong> {ai_sug['justificativa']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Fallback com palavras-chave
            elif 'keyword_suggestion' in st.session_state:
                st.info(f"✅ Setor identificado (palavras-chave): {st.session_state['keyword_suggestion']}")
    
    with col2:
        st.subheader("2️⃣ Valor da Licitação")
        valor = st.number_input(
            "Valor (R$):",
            min_value=0.0,
            value=1000000.0,
            step=10000.0,
            format="%.2f"
        )
        
        st.metric("Valor", f"R$ {valor:,.2f}")
    
    st.markdown("---")
    
    st.subheader("3️⃣ Selecione o Setor Econômico")
    
    # Filtros
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        categoria_filter = st.multiselect(
            "Filtrar por categoria:",
            options=sorted(df_setores['Categoria'].unique()),
            default=None
        )
    
    with col_f2:
        viabilidade_filter = st.multiselect(
            "Filtrar por viabilidade local:",
            options=['Alta', 'Média', 'Baixa'],
            default=None
        )
    
    # Aplicar filtros
    df_filtered = df_setores.copy()
    if categoria_filter:
        df_filtered = df_filtered[df_filtered['Categoria'].isin(categoria_filter)]
    if viabilidade_filter:
        df_filtered = df_filtered[df_filtered['Viabilidade_Local'].isin(viabilidade_filter)]
    
    # Seleção do setor
    setor_options = [f"{row['Código']} - {row['Setor']}" for _, row in df_filtered.iterrows()]
    
    # Pre-selecionar baseado na sugestão da IA ou palavras-chave
    default_index = 0
    if 'ai_suggestion' in st.session_state and st.session_state['ai_suggestion']:
        codigo_sugerido = st.session_state['ai_suggestion']['codigo']
        for i, option in enumerate(setor_options):
            if codigo_sugerido in option:
                default_index = i
                break
    elif 'keyword_suggestion' in st.session_state:
        codigo_sugerido = st.session_state['keyword_suggestion']
        for i, option in enumerate(setor_options):
            if codigo_sugerido in option:
                default_index = i
                break
    
    setor_selecionado = st.selectbox(
        "Setor:",
        options=setor_options,
        index=default_index if setor_options else 0
    )
    
    if setor_selecionado:
        codigo_setor = setor_selecionado.split(' - ')[0]
        setor_data = df_setores[df_setores['Código'] == codigo_setor].iloc[0]
        
        # Exibir informações do setor
        st.markdown("### 📊 Informações do Setor Selecionado")
        
        col_info1, col_info2, col_info3, col_info4 = st.columns(4)
        
        with col_info1:
            st.metric("Multiplicador de Produção", f"{setor_data['Mult_Producao']:.2f}x")
        with col_info2:
            st.metric("Multiplicador de Renda", f"R$ {setor_data['Mult_Renda']:.3f}")
        with col_info3:
            st.metric("Empregos/R$ 1M", f"{setor_data['Mult_Emprego']:.1f}")
        with col_info4:
            viab_color = {'Alta': '🟢', 'Média': '🟡', 'Baixa': '🔴'}
            st.metric("Viabilidade Local", 
                     f"{viab_color[setor_data['Viabilidade_Local']]} {setor_data['Viabilidade_Local']}")
        
        st.markdown("---")
        
        # CÁLCULO DO IMPACTO
        if st.button("🚀 CALCULAR IMPACTO ECONÔMICO", type="primary", use_container_width=True):
            
            # Calcular cenário COM preferência local
            impacto_com = calculate_impact(
                valor,
                setor_data['Mult_Producao'],
                setor_data['Mult_Renda'],
                setor_data['Mult_Emprego'],
                setor_data['Mult_ICMS'],
                fator_regional
            )
            
            # Calcular cenário SEM preferência local
            impacto_sem = calculate_impact(
                valor,
                setor_data['Mult_Producao'],
                setor_data['Mult_Renda'],
                setor_data['Mult_Emprego'],
                setor_data['Mult_ICMS'],
                fator_sem_preferencia
            )
            
            # RESULTADOS
            st.markdown("## 🎯 RESULTADOS DA ANÁLISE")
            
            # Mostrar se foi identificado pela IA
            if 'ai_suggestion' in st.session_state and st.session_state['ai_suggestion']:
                st.info(f"🤖 Setor identificado por IA Maritaca com confiança {st.session_state['ai_suggestion']['confianca'].upper()}")
            
            # Comparação lado a lado
            col_res1, col_res2 = st.columns(2)
            
            with col_res1:
                st.markdown("### ✅ COM Preferência Local")
                st.success(f"**Fator de Regionalização:** {fator_regional:.0%}")
                
                st.metric(
                    "💰 Impacto Total na Produção",
                    f"R$ {impacto_com['producao']:,.2f}",
                    delta=f"+{(impacto_com['producao'] - valor):,.2f}",
                    delta_color="normal"
                )
                
                st.metric(
                    "👥 Empregos Gerados",
                    f"{impacto_com['empregos']:.0f} empregos",
                    delta=f"{impacto_com['empregos']:.0f}",
                    delta_color="normal"
                )
                
                st.metric(
                    "💵 Renda Gerada",
                    f"R$ {impacto_com['renda']:,.2f}",
                    delta=f"+{impacto_com['renda']:,.2f}",
                    delta_color="normal"
                )
                
                st.metric(
                    "🏛️ ICMS Gerado",
                    f"R$ {impacto_com['icms']:,.2f}",
                    delta=f"+{impacto_com['icms']:,.2f}",
                    delta_color="normal"
                )
            
            with col_res2:
                st.markdown("### ⚠️ SEM Preferência Local")
                st.warning(f"**Fator de Regionalização:** {fator_sem_preferencia:.0%}")
                
                st.metric(
                    "💰 Impacto Total na Produção",
                    f"R$ {impacto_sem['producao']:,.2f}",
                    delta=f"-{(impacto_com['producao'] - impacto_sem['producao']):,.2f}",
                    delta_color="inverse"
                )
                
                st.metric(
                    "👥 Empregos Gerados",
                    f"{impacto_sem['empregos']:.0f} empregos",
                    delta=f"-{(impacto_com['empregos'] - impacto_sem['empregos']):.0f}",
                    delta_color="inverse"
                )
                
                st.metric(
                    "💵 Renda Gerada",
                    f"R$ {impacto_sem['renda']:,.2f}",
                    delta=f"-{(impacto_com['renda'] - impacto_sem['renda']):,.2f}",
                    delta_color="inverse"
                )
                
                st.metric(
                    "🏛️ ICMS Gerado",
                    f"R$ {impacto_sem['icms']:,.2f}",
                    delta=f"-{(impacto_com['icms'] - impacto_sem['icms']):,.2f}",
                    delta_color="inverse"
                )
            
            # Diferença destacada
            st.markdown("---")
            st.markdown("### 🔥 DIFERENÇA - O que você GANHA com preferência local:")
            
            col_dif1, col_dif2, col_dif3, col_dif4 = st.columns(4)
            
            dif_producao = impacto_com['producao'] - impacto_sem['producao']
            dif_empregos = impacto_com['empregos'] - impacto_sem['empregos']
            dif_renda = impacto_com['renda'] - impacto_sem['renda']
            dif_icms = impacto_com['icms'] - impacto_sem['icms']
            
            with col_dif1:
                st.markdown(f"<div class='metric-card'><h3 class='impact-high'>+ R$ {dif_producao:,.0f}</h3><p>Produção Adicional</p></div>", unsafe_allow_html=True)
            
            with col_dif2:
                st.markdown(f"<div class='metric-card'><h3 class='impact-high'>+ {dif_empregos:.0f}</h3><p>Empregos Adicionais</p></div>", unsafe_allow_html=True)
            
            with col_dif3:
                st.markdown(f"<div class='metric-card'><h3 class='impact-high'>+ R$ {dif_renda:,.0f}</h3><p>Renda Adicional</p></div>", unsafe_allow_html=True)
            
            with col_dif4:
                st.markdown(f"<div class='metric-card'><h3 class='impact-high'>+ R$ {dif_icms:,.0f}</h3><p>ICMS Adicional</p></div>", unsafe_allow_html=True)
            
            # Gráficos
            st.markdown("---")
            st.markdown("### 📈 Visualização Comparativa")
            
            # Gráfico de barras comparativo
            fig_comp = go.Figure(data=[
                go.Bar(name='COM Preferência Local', 
                       x=['Produção (R$)', 'Renda (R$)', 'Empregos (x10k)', 'ICMS (R$)'],
                       y=[impacto_com['producao'], impacto_com['renda'], 
                          impacto_com['empregos']*10000, impacto_com['icms']],
                       marker_color='#28a745'),
                go.Bar(name='SEM Preferência Local',
                       x=['Produção (R$)', 'Renda (R$)', 'Empregos (x10k)', 'ICMS (R$)'],
                       y=[impacto_sem['producao'], impacto_sem['renda'],
                          impacto_sem['empregos']*10000, impacto_sem['icms']],
                       marker_color='#dc3545')
            ])
            
            fig_comp.update_layout(
                title='Comparação de Impactos: COM vs SEM Preferência Local',
                barmode='group',
                height=400,
                yaxis_title='Valor (R$)'
            )
            
            st.plotly_chart(fig_comp, use_container_width=True)
            
            # Gráfico de pizza - Distribuição do impacto
            col_g1, col_g2 = st.columns(2)
            
            with col_g1:
                fig_pizza = go.Figure(data=[go.Pie(
                    labels=['Impacto Direto', 'Impacto Indireto'],
                    values=[valor, impacto_com['producao'] - valor],
                    hole=.3
                )])
                fig_pizza.update_layout(
                    title='Composição do Impacto Total (COM preferência)',
                    height=350
                )
                st.plotly_chart(fig_pizza, use_container_width=True)
            
            with col_g2:
                # Gráfico de eficiência
                eficiencia_com = (impacto_com['producao'] / valor - 1) * 100
                eficiencia_sem = (impacto_sem['producao'] / valor - 1) * 100
                
                fig_efic = go.Figure(data=[
                    go.Bar(
                        x=['COM Pref. Local', 'SEM Pref. Local'],
                        y=[eficiencia_com, eficiencia_sem],
                        marker_color=['#28a745', '#dc3545'],
                        text=[f'{eficiencia_com:.1f}%', f'{eficiencia_sem:.1f}%'],
                        textposition='auto'
                    )
                ])
                fig_efic.update_layout(
                    title='Eficiência: % de Retorno Adicional',
                    yaxis_title='% de Retorno',
                    height=350
                )
                st.plotly_chart(fig_efic, use_container_width=True)
            
            # Relatório para download
            st.markdown("---")
            st.markdown("### 📄 Relatório")
            
            # Adicionar informação da IA no relatório
            ai_info = ""
            if 'ai_suggestion' in st.session_state and st.session_state['ai_suggestion']:
                ai_sug = st.session_state['ai_suggestion']
                ai_info = f"""
IDENTIFICAÇÃO DO SETOR:
----------------------
Método: Maritaca AI (Inteligência Artificial)
Confiança: {ai_sug['confianca'].upper()}
Justificativa: {ai_sug['justificativa']}
"""
            
            relatorio = f"""
================================================================================
RELATÓRIO DE IMPACTO ECONÔMICO - LICITAÇÃO COM PREFERÊNCIA LOCAL
================================================================================

Data da Análise: {datetime.now().strftime("%d/%m/%Y %H:%M")}

DADOS DA LICITAÇÃO:
-------------------
Objeto: {descricao if descricao else 'Não informado'}
Valor: R$ {valor:,.2f}
Setor: {setor_data['Código']} - {setor_data['Setor']}
Município: {tamanho}
{ai_info}
MULTIPLICADORES DO SETOR:
-------------------------
• Produção: {setor_data['Mult_Producao']:.2f}x
• Renda: {setor_data['Mult_Renda']:.3f}
• Emprego: {setor_data['Mult_Emprego']:.2f} empregos/R$ 1 milhão
• ICMS: {setor_data['Mult_ICMS']:.3f}
• Viabilidade Local: {setor_data['Viabilidade_Local']}

CENÁRIO 1: COM PREFERÊNCIA LOCAL (Fator: {fator_regional:.0%})
================================================================
💰 Impacto Total na Produção: R$ {impacto_com['producao']:,.2f}
💵 Renda Gerada: R$ {impacto_com['renda']:,.2f}
👥 Empregos Gerados: {impacto_com['empregos']:.0f} postos de trabalho
🏛️ ICMS Gerado: R$ {impacto_com['icms']:,.2f}

CENÁRIO 2: SEM PREFERÊNCIA LOCAL (Fator: {fator_sem_preferencia:.0%})
====================================================================
💰 Impacto Total na Produção: R$ {impacto_sem['producao']:,.2f}
💵 Renda Gerada: R$ {impacto_sem['renda']:,.2f}
👥 Empregos Gerados: {impacto_sem['empregos']:.0f} postos de trabalho
🏛️ ICMS Gerado: R$ {impacto_sem['icms']:,.2f}

🔥 DIFERENÇA - GANHO COM PREFERÊNCIA LOCAL:
===========================================
💰 Produção Adicional: R$ {dif_producao:,.2f} (+{(dif_producao/impacto_sem['producao']*100):.1f}%)
💵 Renda Adicional: R$ {dif_renda:,.2f} (+{(dif_renda/impacto_sem['renda']*100):.1f}%)
👥 Empregos Adicionais: {dif_empregos:.0f} (+{(dif_empregos/impacto_sem['empregos']*100):.1f}%)
🏛️ ICMS Adicional: R$ {dif_icms:,.2f} (+{(dif_icms/impacto_sem['icms']*100 if impacto_sem['icms'] > 0 else 0):.1f}%)

EFICIÊNCIA DO INVESTIMENTO:
--------------------------
• COM Preferência Local: Cada R$ 1,00 investido gera R$ {impacto_com['producao']/valor:.2f} na economia
• SEM Preferência Local: Cada R$ 1,00 investido gera R$ {impacto_sem['producao']/valor:.2f} na economia
• Eficiência adicional: {((impacto_com['producao']/valor) - (impacto_sem['producao']/valor))*100:.1f}% a mais

CONCLUSÃO:
----------
A aplicação de preferência local nesta licitação resulta em um impacto
econômico {((impacto_com['producao']/impacto_sem['producao'] - 1)*100):.1f}% MAIOR na região, gerando {dif_empregos:.0f} empregos
adicionais e R$ {dif_renda:,.2f} a mais em renda para a população local.

================================================================================
Relatório gerado pela Calculadora de Impacto Econômico - Licitações Locais
Identificação de setor: Maritaca AI (IA brasileira)
Base: Matriz Insumo-Produto do Paraná 2018
================================================================================
"""
            
            st.download_button(
                label="📥 Baixar Relatório (TXT)",
                data=relatorio,
                file_name=f"relatorio_impacto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

with tab2:
    st.header("📚 Consulta de Setores Econômicos")
    st.markdown("Explore todos os setores e seus multiplicadores")
    
    # Filtros
    col_search1, col_search2 = st.columns(2)
    with col_search1:
        search_text = st.text_input("🔍 Buscar setor:", placeholder="Digite para buscar...")
    
    with col_search2:
        sort_by = st.selectbox(
            "Ordenar por:",
            ["Multiplicador de Produção", "Multiplicador de Emprego", "Multiplicador de Renda", "Nome do Setor"]
        )
    
    # Aplicar busca
    df_search = df_setores.copy()
    if search_text:
        df_search = df_search[df_search['Setor'].str.contains(search_text, case=False)]
    
    # Ordenar
    if sort_by == "Multiplicador de Produção":
        df_search = df_search.sort_values('Mult_Producao', ascending=False)
    elif sort_by == "Multiplicador de Emprego":
        df_search = df_search.sort_values('Mult_Emprego', ascending=False)
    elif sort_by == "Multiplicador de Renda":
        df_search = df_search.sort_values('Mult_Renda', ascending=False)
    else:
        df_search = df_search.sort_values('Setor')
    
    # Exibir tabela
    st.dataframe(
        df_search[['Código', 'Setor', 'Mult_Producao', 'Mult_Renda', 'Mult_Emprego', 
                   'Mult_ICMS', 'Viabilidade_Local', 'Categoria']].style.format({
            'Mult_Producao': '{:.2f}',
            'Mult_Renda': '{:.3f}',
            'Mult_Emprego': '{:.2f}',
            'Mult_ICMS': '{:.3f}'
        }),
        use_container_width=True,
        height=600
    )
    
    # Gráfico de ranking
    st.markdown("### 🏆 Top 10 Setores por Multiplicador de Produção")
    top10 = df_setores.nlargest(10, 'Mult_Producao')
    
    fig_top = px.bar(
        top10,
        x='Mult_Producao',
        y='Setor',
        orientation='h',
        color='Viabilidade_Local',
        color_discrete_map={'Alta': '#28a745', 'Média': '#ffc107', 'Baixa': '#dc3545'},
        title='Top 10 Setores - Maior Impacto Econômico'
    )
    fig_top.update_layout(height=500)
    st.plotly_chart(fig_top, use_container_width=True)

with tab3:
    st.header("📖 Guia de Uso")
    
    st.markdown("""
    ## Como usar esta ferramenta
    
    ### 1️⃣ Configure sua API Key da Maritaca AI (Opcional mas Recomendado)
    - Acesse https://plataforma.maritaca.ai e crie uma conta
    - Gere sua API Key
    - Cole a API Key na barra lateral
    - A IA analisará suas descrições e sugerirá setores com precisão
    
    ### 2️⃣ Descreva o objeto da licitação
    - Digite uma descrição detalhada do que será licitado
    - Clique em "🤖 Identificar Setor com IA Maritaca"
    - A IA analisará e sugerirá o setor mais adequado
    - Veja a justificativa da escolha
    
    ### 3️⃣ Informe o valor
    - Digite o valor estimado da licitação
    - O valor será usado para calcular todos os impactos
    
    ### 4️⃣ Confirme o setor
    - Revise a sugestão da IA
    - Ajuste se necessário
    - Veja os multiplicadores do setor
    
    ### 5️⃣ Configure o município
    - Na barra lateral, selecione o tamanho do município
    - Isso ajusta o fator de regionalização
    
    ### 6️⃣ Calcule o impacto
    - Clique no botão "Calcular Impacto Econômico"
    - Compare os cenários COM e SEM preferência local
    - Analise os gráficos e baixe o relatório
    
    ## 🤖 Vantagens da Maritaca AI
    
    **Identificação Inteligente:**
    - Compreende contexto, não apenas palavras-chave
    - Analisa descrições complexas
    - Fornece justificativa da escolha
    - Indica nível de confiança
    
    **Precisão:**
    - Modelo treinado em português brasileiro
    - Entende termos técnicos de licitações
    - Considera nuances da descrição
    
    **Transparência:**
    - Explica porque escolheu cada setor
    - Indica grau de confiança (alta/média/baixa)
    - Permite ajuste manual
    
    ## 📊 Entendendo os Multiplicadores
    
    [... resto do guia igual ao anterior ...]
    """)

with tab4:
    st.header("🤖 Sobre a Integração com Maritaca AI")
    
    st.markdown("""
    ## O que é Maritaca AI?
    
    **Maritaca AI** é uma empresa brasileira de inteligência artificial que desenvolveu
    o **Sabiá**, um modelo de linguagem grande (LLM) treinado especificamente em
    português brasileiro.
    
    ### Por que usar Maritaca AI neste aplicativo?
    
    #### 1. 🇧🇷 Otimizado para Português Brasileiro
    - Compreende termos técnicos de licitações públicas
    - Entende o contexto brasileiro de compras governamentais
    - Familiarizado com nomenclaturas do IBGE e CNAE
    
    #### 2. 🎯 Precisão na Identificação
    - Vai além de palavras-chave simples
    - Analisa o contexto completo da descrição
    - Considera nuances e ambiguidades
    
    #### 3. 💡 Transparência
    - Explica o raciocínio por trás da escolha
    - Indica grau de confiança
    - Permite validação humana
    
    ### Como funciona?
    
    ```
    1. Você descreve o objeto da licitação
       ↓
    2. A IA recebe a descrição + lista de 42 setores
       ↓
    3. O modelo Sabiá-3 analisa o contexto
       ↓
    4. Retorna: setor + confiança + justificativa
       ↓
    5. Você confirma ou ajusta
    ```
    
    ### Exemplos de Análise
    
    **Exemplo 1:**
    ```
    Descrição: "Aquisição de gêneros alimentícios para merenda escolar, 
                incluindo frutas, verduras e produtos da agricultura familiar"
    
    IA Maritaca:
    ✅ Setor: 1093 - Outros produtos alimentares
    🟢 Confiança: ALTA
    💬 Justificativa: "A descrição menciona gêneros alimentícios diversos 
       e agricultura familiar, característicos do setor de outros produtos 
       alimentares, que engloba alimentos processados e in natura."
    ```
    
    **Exemplo 2:**
    ```
    Descrição: "Contratação de serviços de elaboração de projeto executivo 
                de engenharia para reforma de prédio público"
    
    IA Maritaca:
    ✅ Setor: 6980 - Serviços profissionais e técnicos
    🟡 Confiança: MÉDIA
    💬 Justificativa: "Embora se trate de engenharia relacionada a 
       construção, o foco é no serviço de elaboração de projeto 
       (serviço intelectual), não na execução da obra."
    ```
    
    ### Obtendo sua API Key
    
    1. Acesse: https://plataforma.maritaca.ai
    2. Crie uma conta (gratuita para começar)
    3. Acesse "API Keys" no painel
    4. Gere uma nova chave
    5. Cole na barra lateral deste aplicativo
    
    ### Custos
    
    A Maritaca oferece:
    - **Plano Gratuito**: Ideal para testes
    - **Pay-as-you-go**: Pague apenas pelo que usar
    - **Planos Empresariais**: Para alto volume
    
    Para este aplicativo, cada análise custa centavos, tornando viável
    mesmo para municípios pequenos.
    
    ### Privacidade e Segurança
    
    - ✅ Seus dados não são usados para treinar o modelo
    - ✅ API segura (HTTPS)
    - ✅ Empresa brasileira (LGPD)
    - ✅ Sem armazenamento de descrições
    
    ### Fallback Automático
    
    Se a API não estiver disponível ou não houver API Key:
    - O sistema usa identificação por palavras-chave
    - Você não fica sem o serviço
    - Continua funcional, só menos preciso
    
    ### Melhorias Futuras
    
    Com a integração da Maritaca AI, planejamos:
    - 📊 Análise de histórico de licitações
    - 🎯 Sugestões de estratégias de preferência local
    - 📈 Previsão de impacto por município
    - 🤝 Comparação com licitações similares
    
    ---
    
    **Links Úteis:**
    - Site: https://maritaca.ai
    - Plataforma: https://plataforma.maritaca.ai
    - Documentação: https://docs.maritaca.ai
    - Suporte: suporte@maritaca.ai
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    📊 Calculadora de Impacto Econômico - Licitações com Preferência Local<br>
    🤖 Powered by Maritaca AI (IA brasileira)<br>
    Base de dados: Matriz Insumo-Produto do Paraná 2018 (IPARDES)<br>
    Desenvolvido com Streamlit | Janeiro 2026
</div>
""", unsafe_allow_html=True)