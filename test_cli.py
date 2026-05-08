from unittest.mock import patch
from typer.testing import CliRunner
from main import app

runner = CliRunner()


def test_cli_help():
    """Sanity check: ensures the CLI loads and displays the help menu."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "CodeLens" in result.stdout


def test_init_command_valid_backend(tmp_path):
    config_path = tmp_path / ".codelens_config"
    with patch("config.CONFIG_PATH", config_path):
        result = runner.invoke(app, ["init"], input="ollama\n")
    assert result.exit_code == 0
    assert "Configuration saved" in result.stdout


def test_init_command_invalid_backend(tmp_path):
    config_path = tmp_path / ".codelens_config"
    with patch("config.CONFIG_PATH", config_path):
        result = runner.invoke(app, ["init"], input="invalid\n")
    assert result.exit_code == 1


def test_auth_github_command(tmp_path):
    config_path = tmp_path / ".codelens_config"
    with patch("config.CONFIG_PATH", config_path):
        result = runner.invoke(app, ["auth", "github"], input="ghp_test_token\n")
    assert result.exit_code == 0
    assert "GitHub token saved" in result.stdout