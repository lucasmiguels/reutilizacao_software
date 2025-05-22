import re
from dotenv import load_dotenv
from pathlib import Path
from pathlib import Path

load_dotenv()

# === Registro global de validadores ===
VALIDATOR_REGISTRY = {}

BASE_DIR = Path(__file__).resolve().parent  # pasta src/

PRESET_PROMPT_PATHS = {
    "email": BASE_DIR / "prompts" / "email",
    "profissao": BASE_DIR / "prompts" / "profissão",  # cuidado com acento
    "endereco": BASE_DIR / "prompts" / "endereco",  # cuidado com acento
    "nome_completo": BASE_DIR / "prompts" / "nome_completo",  # cuidado com acento


}


def register_validator(name):
    def decorator(cls):
        VALIDATOR_REGISTRY[name] = cls
        return cls
    return decorator


class BaseFieldValidator:
    def __init__(self, llm_call_fn=None, prompt_paths=None):
        self.llm_call_fn = llm_call_fn
        self.prompt_paths = self._resolve_prompt_paths(prompt_paths)

    def _resolve_prompt_paths(self, prompt_paths):
        # Se for string (diretório), converte para lista de arquivos .txt
        if isinstance(prompt_paths, (str, Path)):
            prompt_dir = Path(prompt_paths)
            if not prompt_dir.is_dir():
                raise FileNotFoundError(f"O caminho '{prompt_paths}' não é um diretório válido.")
            return sorted(prompt_dir.glob("*.txt"))

        # Se já for lista de arquivos, apenas retorna
        return prompt_paths or []

    def validate(self, text: str) -> bool:
        raise NotImplementedError()
    
    def correct_with_llm(self, text: str) -> str:
        if not self.llm_call_fn or not self.prompt_paths:
            raise ValueError("LLM function and prompt paths must be provided.")

        current_text = text.strip()
        last_valid = None

        for prompt_path in self.prompt_paths:
            with open(prompt_path, "r", encoding="utf-8") as f:
                template = f.read()

            prompt = template.replace("{input}", current_text)
            result = self.llm_call_fn(prompt).strip()

            if result.lower() == "inválido" or not self.validate(result):
                # Mantém o current_text para a próxima etapa, ignora o inválido
                continue

            # Se for válido, atualiza
            current_text = result
            last_valid = result

        # Retorna o último válido encontrado (ou original se nenhum for válido)
        return last_valid if last_valid is not None else text.strip()
# === Validadores com registro automático ===
# Uso de decorators aberto e fechado e single responsability

@register_validator("email")
class EmailValidator(BaseFieldValidator):
    REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

    def validate(self, text: str) -> bool:
        return bool(self.REGEX.match(text.strip()))


@register_validator("nome_completo")
class NomeCompletoValidator(BaseFieldValidator):
    def validate(self, text: str) -> bool:
        parts = text.strip().split()

        if len(parts) < 2:
            return False

        lowercase_ok = {"de", "da", "do", "das", "dos", "e"}

        for part in parts:
            if part in lowercase_ok:
                continue
            if not part[0].isupper() or not part[1:].islower():
                return False
            if len(part) < 2:
                return False

        return True

@register_validator("profissao")
class ProfissaoValidator(BaseFieldValidator):
    def validate(self, text: str) -> bool:
        clean = text.strip()
        if len(clean) <= 2:
            return False
        words = clean.split()
        lowercase_ok = {"de", "da", "do", "das", "dos", "e"}
        for word in words:
            if word in lowercase_ok:
                continue
            if len(word) < 2 or not word[0].isupper():
                return False

        return True


@register_validator("endereco")
class EnderecoValidator(BaseFieldValidator):
    def validate(self, text: str) -> bool:
        clean = text.strip()
        return any(c.isdigit() for c in clean) and len(clean) > 5
    



# === Função de uso genérico ===
def apply_validator(campo: str, texto: str, llm_call_fn=None, prompt_paths=None):
    try:
        cls = VALIDATOR_REGISTRY.get(campo)
        if not cls:
            print(f"Validador '{campo}' não registrado.")
            return

        # Carrega caminhos de prompt predefinidos, se necessário
        if prompt_paths is None and campo in PRESET_PROMPT_PATHS:
            prompt_paths = PRESET_PROMPT_PATHS[campo]

        validator = cls(llm_call_fn=llm_call_fn, prompt_paths=prompt_paths)

        # Validação original
        try:
            original_valid = int(bool(validator.validate(texto)))
        except Exception as e:
            print(f"Erro na validação sem LLM: {e}")
            return

        # Correção com LLM, se fornecida
        if llm_call_fn:
            try:
                corrected_text = validator.correct_with_llm(texto)
                corrected_valid = int(bool(validator.validate(corrected_text)))
                return {
                    "is_original_valid": original_valid,
                    "is_corrected_valid": corrected_valid,
                    "corrected": corrected_text
                }
            except FileNotFoundError as fe:
                print(f"Erro ao carregar prompt: {fe}")
                return
            except Exception as e:
                print(f"Erro na correção com LLM: {e}")
                return
        else:
            return {
                "is_original_valid": original_valid,
                "is_corrected_valid": None,
                "corrected": None
            }

    except Exception as e:
        print(f"Erro geral: {e}")
        return
