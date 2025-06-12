import streamlit as st
import os
from dotenv import load_dotenv
import importlib
import validators  # ou outro módulo que você queira forçar a recarga
importlib.reload(validators)
from llmclient import get_llm_call_fn
from pathlib import Path
import pandas as pd


importlib.reload(validators)
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
PROMPT_DIR = BASE_DIR / "prompts"

HEADER_CSV_PATH = BASE_DIR / "header.csv"

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

st.sidebar.info(
    "**Temperatura** controla a aleatoriedade do LLM:\n"
    "* 0 - 0.3 → respostas mais determinísticas\n"
    "* 0.7 - 1.0 → respostas mais criativas"
)


header_df = pd.read_csv(HEADER_CSV_PATH)
campos = dict(zip(header_df["validador"], header_df["label"]))

st.subheader("Preencha seus dados")

form_data = {}
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
                result = validators.apply_validator(campo, user_input, llm_call_fn=call_fn)
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

# === Modal: Criar novo validador ===
st.markdown("---")
st.markdown("### Criar novo validador")

with st.expander("➕ Adicionar novo prompt personalizado"):
    campo = st.text_input("Nome do campo (ex: cpf)", key="new_field")
    label = st.text_input("Label (nome visível no formulário)", key="new_label")
    nome_validacao = st.text_input("Nome da validação (arquivo .txt)", key="new_prompt")
    conteudo_prompt = st.text_area("Prompt de validação", height=200, key="prompt_content")

    if st.button("Salvar prompt personalizado"):
        if not campo or not nome_validacao or not conteudo_prompt or not label:
            st.warning("Preencha todos os campos antes de salvar.")
        else:
            if HEADER_CSV_PATH.exists():
                header_df = pd.read_csv(HEADER_CSV_PATH)
            else:
                header_df = pd.DataFrame(columns=["validador", "label"])

            if campo not in header_df["validador"].values:
                new_row = pd.DataFrame([{"validador": campo, "label": label}])
                header_df = pd.concat([header_df, new_row], ignore_index=True)
                header_df.to_csv(HEADER_CSV_PATH, index=False)
        
            # === Salva prompt no arquivo txt ===
            pasta_campo = PROMPT_DIR / campo
            pasta_campo.mkdir(parents=True, exist_ok=True)
            caminho_arquivo = pasta_campo / f"{nome_validacao}.txt"

            if caminho_arquivo.exists():
                st.warning("Esse arquivo já existe. Substituindo...")


            conteudo_limpo = conteudo_prompt.strip()
            if "{input}" not in conteudo_limpo:
                conteudo_limpo += "\n\nEntrada: {input}"

            with open(caminho_arquivo, "w", encoding="utf-8") as f:
                f.write(conteudo_limpo)


            st.success(f"Prompt salvo em `{caminho_arquivo}`!")
            st.rerun()  # recarrega a página para refletir o novo campo
