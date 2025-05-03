import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def sugerir_email_correto(email_input):
    prompt = f"""
Você é um corretor de e-mails inteligente.

Dado um endereço de e-mail digitado por um usuário, você deve verificar se ele está correto.

- Se o e-mail estiver **correto**, responda apenas com "Válido".
- Se estiver **mal digitado**, corrija o email e devolva o **e-mail completo corrigido**.
- Se não for possível corrigir, responda com "Inválido".

Você sempre deve responder com **apenas uma palavra**

E-mail: {email_input}
"""

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip()

print(sugerir_email_correto("joao@gmial.com"))      # joao@gmail.com
print(sugerir_email_correto("maria@hotmial.com"))   # maria@hotmail.com
print(sugerir_email_correto("carlos#email.com"))    # Inválido
print(sugerir_email_correto("teste@gmail.com"))     # Válido
print(sugerir_email_correto("solabge@gmail.com"))    
