import streamlit as st
import os
from dotenv import load_dotenv
from validators import apply_validator
from llmclient import get_llm_call_fn

load_dotenv()

st.set_page_config(page_title="Validador Inteligente de Formulários", layout="centered")
st.title("Formulário com Validação Inteligente")

st.sidebar.header("Configuração do LLM")
provider = st.sidebar.selectbox("Provedor", ["openai", "ollama", "stub"])

model = st.sidebar.text_input("Modelo", value="gpt-3.5-turbo" if provider == "openai" else "llama3-70b-8192")
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.1, 0.05)

api_key_input = st.sidebar.text_input("API Key (OpenAI)", type="password")
api_key = api_key_input or os.getenv("OPENAI_API_KEY")

base_url = st.sidebar.text_input("Base URL (OpenAI ou Ollama)", value="https://api.openai.com/v1" if provider == "openai" else "http://localhost:11434")
if not api_key_input:
    st.sidebar.info("Usando chave da variável de ambiente (OPENAI_API_KEY).")

st.subheader("Preencha seus dados")

form_data = {}
campos = {
    "nome_completo": "Nome completo",
    "email": "E-mail",
    "profissao": "Profissão",
    "endereco": "Endereço"
}

call_fn = get_llm_call_fn(
    provider,
    model=model,
    temperature=temperature,
    api_key=api_key,
    base_url=base_url,
    host=base_url
) if provider != "stub" else get_llm_call_fn("stub")

for campo, label in campos.items():
    with st.container():
        st.write(f"### {label}")
        user_input = st.text_input(f"{label}", key=campo)
        if st.button(f"Validar {label}", key=f"btn_{campo}"):
            with st.spinner("Validando..."):
                result = apply_validator(campo, user_input, llm_call_fn=call_fn)
                if result:
                    if result["is_original_valid"]:
                        st.success("Campo válido!")
                        if result["corrected"] and result["corrected"].strip() != user_input.strip():
                            st.info(f"O conteúdo está válido, mas você quis dizer: **{result['corrected']}**?")
                    else:
                        st.error("Campo inválido.")
                        if result["corrected"] and result["corrected"].strip() != user_input.strip():
                            st.warning(f"Você não quis dizer: **{result['corrected']}**?")
                        else:
                            st.info("Não foram encontradas sugestões para correção.")
