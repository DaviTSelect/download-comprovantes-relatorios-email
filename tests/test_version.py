import re
import version


def test_version_formato_semver():
    assert re.fullmatch(r"\d+\.\d+\.\d+", version.VERSION), (
        f"VERSION '{version.VERSION}' não está no formato SemVer (MAJOR.MINOR.PATCH)"
    )


def test_version_alias_dunder():
    assert version.__version__ == version.VERSION


def test_campos_obrigatorios():
    for campo in ("VERSION", "APP_NAME", "REPOSITORY", "DESCRIPTION", "AUTHOR"):
        assert getattr(version, campo, ""), f"version.{campo} está vazio ou ausente"
