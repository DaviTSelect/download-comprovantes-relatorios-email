"""Injeta variáveis de ambiente mínimas para que config.py importe sem erros."""
import os

os.environ.setdefault("GRAPH_CLIENT_ID",     "test_client_id")
os.environ.setdefault("GRAPH_CLIENT_SECRET", "test_secret")
os.environ.setdefault("GRAPH_TENANT_ID",     "test_tenant")
os.environ.setdefault("USER_EMAIL",          "test@example.com")
os.environ.setdefault("CONVENIAR_USUARIO",   "test_usuario")
os.environ.setdefault("CONVENIAR_SENHA",     "test_senha")
os.environ.setdefault("CONVENIAR_URL",       "https://example.com")
