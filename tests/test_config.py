import os
import config


def test_expandir_userprofile():
    os.environ["_TEST_PATH"] = r"%USERPROFILE%\Chrome\chrome.exe"
    # Simula o que _expandir faz
    resultado = os.path.expandvars(os.environ["_TEST_PATH"])
    assert "%USERPROFILE%" not in resultado
    assert os.environ.get("USERPROFILE", "") in resultado


def test_expandir_vazio_retorna_none():
    os.environ.pop("_VAR_INEXISTENTE", None)
    valor = os.environ.get("_VAR_INEXISTENTE") or ""
    expandido = os.path.expandvars(valor).strip() or None
    assert expandido is None


def test_vars_obrigatorias_carregadas():
    for var in ("GRAPH_CLIENT_ID", "GRAPH_CLIENT_SECRET", "GRAPH_TENANT_ID",
                "USER_EMAIL", "CONVENIAR_USUARIO", "CONVENIAR_SENHA"):
        assert getattr(config, var, ""), f"config.{var} está vazio"
