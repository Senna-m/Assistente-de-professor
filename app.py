import streamlit as st

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Assistente de Professor - Análises Clínicas",
    page_icon="🧪",
    layout="centered",
)


# ============================================================
# ESTILOS
# ============================================================
def load_css() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #f4fbff 0%, #eef7ff 100%);
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


load_css()


# ============================================================
# PROMPT DO SISTEMA
# ============================================================
def get_system_prompt(professor_name: str, specialty: str = "curso técnico em análises clínicas") -> str:
    return f"""Você é um assistente especializado em {specialty}, criado para apoiar o professor {professor_name} no planejamento e condução das aulas.

## Seu papel
Auxiliar o professor {professor_name} de forma objetiva, prática e resumida — você é um suporte técnico, não o professor.

## O que você pode fazer
- Montar planos de aula com base no conteúdo, tempo disponível e nível dos alunos
- Criar atividades práticas, exercícios e roteiros de laboratório
- Sugerir avaliações, questões teóricas e critérios de correção
- Organizar conteúdos por semana, módulo ou unidade
- Responder dúvidas sobre técnica laboratorial, segurança, biossegurança e metodologia de ensino
- Concertar textos para adicinar no sistema de diario de classe, apostilas ou apresentações

## Formato das respostas
- Seja direto e conciso
- Use listas e passos curtos quando necessário
- Destaque pontos importantes em **negrito**
- Quando fizer sentido, organize em tópicos como: objetivo, materiais, procedimento, observações e avaliação

## Regras de comportamento
- Pergunte as informações que faltarem antes de montar um plano completo (tema, turma, duração, nível dos alunos, objetivo da aula)
- Não invente dados sobre os alunos ou resultados laboratoriais
- Use linguagem técnica, mas explique termos quando necessário
- Se a pergunta estiver fora do escopo de análises clínicas, redirecione educadamente
- Sempre lembre da segurança, biossegurança e ética profissional

## Contexto padrão
- Aula para curso técnico em análises clínicas
- Ambiente de laboratório ou sala de aula
- Alunos em formação inicial, salvo indicação contrária
"""


# ============================================================
# CLIENTE GEMINI
# ============================================================
def get_client():
    try:
        import google.genai as genai
    except Exception:
        return None

    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = None

    if not api_key:
        return None

    return genai.Client(api_key=api_key)


# ============================================================
# GERAÇÃO DE RESPOSTA
# ============================================================
def gerar_resposta(pergunta: str, professor_name: str) -> str:
    prompt = f"{get_system_prompt(professor_name)}\n\nPergunta do professor:\n{pergunta}"
    client = get_client()

    if client is None:
        return (
            "O assistente está em modo offline no momento. "
            "Para ativar a resposta com IA, configure a chave GEMINI_API_KEY em Streamlit Secrets."
        )

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        return getattr(response, "text", str(response))
    except Exception as exc:
        return f"Não foi possível gerar a resposta no momento. Detalhes: {exc}"


# ============================================================
# INTERFACE
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Olá! Sou o assistente do professor para o curso técnico em análises clínicas. Posso ajudar com planos de aula, atividades práticas, avaliações e explicações técnicas.",
        }
    ]

if "professor_name" not in st.session_state:
    st.session_state.professor_name = ""

st.title("🧪 Assistente de Professor")
st.caption("Suporte rápido para aulas, laboratório e planejamento didático em análises clínicas")

with st.sidebar:
    st.header("Configuração")
    professor_name = st.text_input(
        "Nome do professor",
        value=st.session_state.professor_name,
        placeholder="Ex.: Prof. Ana",
    )
    if professor_name:
        st.session_state.professor_name = professor_name

    st.markdown("### O que posso ajudar?")
    st.markdown("- Planejar aulas")
    st.markdown("- Criar atividades práticas")
    st.markdown("- Montar avaliações")
    st.markdown("- Explicar procedimentos e biossegurança")

    if st.button("Limpar conversa"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Olá! Sou o assistente do professor para o curso técnico em análises clínicas. Posso ajudar com planos de aula, atividades práticas, avaliações e explicações técnicas.",
            }
        ]
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

prompt = st.chat_input("Digite sua dúvida ou solicitação")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    professor_name = st.session_state.professor_name or "Professor"
    resposta = gerar_resposta(prompt, professor_name)
    st.session_state.messages.append({"role": "assistant", "content": resposta})
    with st.chat_message("assistant"):
        st.write(resposta)