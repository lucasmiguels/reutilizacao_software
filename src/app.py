import streamlit as st
import os
from validators import apply_validator
from llmclient import get_llm_call_fn

# === Configuração do Streamlit ===
st.set_page_config(page_title="Validador Inteligente de Formulários", layout="centered")
st.title("Validador de Dados com LLM")

# === Sidebar para configuração do modelo ===
st.sidebar.header("Configuração do LLM")
provider = st.sidebar.selectbox("Provedor", ["stub", "openai", "ollama"])

model = st.sidebar.text_input("Modelo", value="gpt-3.5-turbo" if provider == "openai" else "llama3-70b-8192")
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.1, 0.05)

api_key = st.sidebar.text_input("API Key (OpenAI)", type="password")
base_url = st.sidebar.text_input("Base URL (OpenAI ou Ollama)", value="https://api.openai.com/v1" if provider == "openai" else "http://localhost:11434")

# === Entrada do usuário ===
st.subheader("Dados do Formulário")
campo = st.selectbox("Campo para validação", ["nome_completo", "email", "profissao", "endereco"])
texto = st.text_input("Texto a ser validado")

if st.button("Validar"):
    with st.spinner("Validando..."):
        try:
            call_fn = get_llm_call_fn(
                provider,
                model=model,
                temperature=temperature,
                api_key=api_key,
                base_url=base_url,
                host=base_url
            ) if provider != "stub" else get_llm_call_fn("stub")

            result = apply_validator(campo, texto, llm_call_fn=call_fn)

            if result:
                st.markdown("---")
                col1, col2 = st.columns(2)
                col1.metric("Original", "Válido" if result["is_original_valid"] else "Inválido")

                if result["corrected"] and result["corrected"].strip() != texto.strip():
                    col2.metric("Corrigido", "Válido" if result["is_corrected_valid"] else "Inválido")
                    st.warning(f"Você não quis dizer: **{result['corrected']}**?")
                else:
                    st.success("Parece que o conteúdo está correto!")

        except Exception as e:
            st.error(f"Erro ao validar: {e}")
