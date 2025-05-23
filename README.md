🧠 Validador de Campos de Formulário com LLM (Reutilizável e Extensível)

Este projeto implementa um validador reutilizável de campos de formulário que utiliza modelos de linguagem (LLMs) para corrigir entradas com base em prompts customizados. Ele segue os princípios SOLID para garantir extensibilidade, modularidade e manutenção facilitada.

🚀 Visão Geral

A proposta central do projeto é permitir a validação inteligente e progressiva de campos de entrada em formulários (ex: e-mail, nome, profissão, endereço), com a capacidade de:
- Validar sintaticamente (regex, regras gramaticais etc.),
- Corrigir campos com o auxílio de Large Language Models (LLMs),
- Aplicar múltiplas etapas de correção com prompts reutilizáveis,
- Ser facilmente extensível para novos tipos de campo.

🧱 Estrutura do Projeto

.
├── src/
│   ├── prompts/               # Diretório com prompts organizados por campo
│   ├── llmclient.py           # Fábricas de LLMs (Groq, OpenAI, Ollama, Stub)
│   ├── validators.py          # Implementações dos validadores com registro automático
├── .env                       # Variáveis de ambiente (ex: API_KEY)
├── README.md                  # Documentação principal
├── teste.ipynb                # Jupyter Notebook de testes

🧠 Funcionalidades

- ✅ Validação booleana local por campo (nome, email, profissão, etc.).
- 🤖 Correção com LLM usando prompts customizados.
- 🔁 Execução em múltiplas etapas (pipeline de prompts).
- 🧩 Registro automático de validadores via decorators.
- 🧼 Separação entre validação, correção e lógica de execução (SRP).
- 🧱 Extensível: basta criar uma nova classe Validator e uma pasta de prompts.

🔧 Tecnologias Utilizadas

- Python 3.10+
- OpenAI SDK
- requests (para integração com Ollama)
- dotenv (para variáveis de ambiente)

📦 Como Usar

1. Instale as dependências:
    pip install -r requirements.txt

2. Configure o .env com sua API_KEY:
    API_KEY=sk-...

3. Estruture seus prompts em src/prompts/<campo>/*.txt

4. Execute:

from apply_validator import apply_validator
from llmclient import get_llm_call_fn

llm_fn = get_llm_call_fn(
    provider="groq",
    api_key="sk-...",
    base_url="https://api.groq.com/openai/v1",
    model="llama3-70b-8192",
    temperature=0.2
)

result = apply_validator("email", "lcas#gmial.com", llm_call_fn=llm_fn)
print(result)

Saída:
{
    "is_original_valid": 0,
    "is_corrected_valid": 1,
    "corrected": "lucas@gmail.com"
}

🧠 Princípios SOLID Aplicados

- S — Single Responsibility: cada classe tem uma única responsabilidade.
- O — Open/Closed: sistema aberto a extensões, fechado a modificações.
- L — Liskov Substitution: todos os validadores podem ser substituídos.
- I — Interface Segregation: métodos mínimos para operar.
- D — Dependency Inversion: depende de abstrações (função LLM).

📄 Licença

MIT

👨‍💻 Maria Luiza C. Wuillaume e Lucas Miguel

Desenvolvido com foco em reuso, IA aplicada e arquitetura limpa.