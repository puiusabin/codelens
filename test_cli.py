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


def test_check_command_file_not_found():
    result = runner.invoke(app, ["check", "nonexistent.py"])
    assert result.exit_code == 1


def test_check_command_shows_critical(tmp_path):
    code_file = tmp_path / "code.py"
    code_file.write_text("def f(a, b): return a / b")
    with patch("main.check_code_smells", return_value="[CRITICAL] Line 1: Division by zero risk"):
        result = runner.invoke(app, ["check", str(code_file)])
    assert result.exit_code == 0
    assert "CRITICAL" in result.stdout


def test_review_command_invalid_url():
    result = runner.invoke(app, ["review", "not-a-github-url"])
    assert result.exit_code == 1


def test_review_command_success(tmp_path):
    config_path = tmp_path / ".codelens_config"
    with patch("config.CONFIG_PATH", config_path), \
         patch("main.fetch_pr_diff", return_value="diff content"), \
         patch("main.analyze_diff", return_value="## Summary\nTest PR"):
        result = runner.invoke(app, ["review", "https://github.com/a/b/pull/1"])
    assert result.exit_code == 0
    assert "PR Review" in result.stdout