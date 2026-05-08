from pathlib import Path
from unittest.mock import patch
from typer.testing import CliRunner
import agents.analyzer
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


def test_test_command_file_not_found():
    result = runner.invoke(app, ["test", "nonexistent.py"])
    assert result.exit_code == 1


def test_test_command_generates_output(tmp_path):
    code_file = tmp_path / "calc.py"
    code_file.write_text("def add(a, b): return a + b")
    with patch("main.analyze_code", return_value="No issues."), \
         patch("main.generate_tests", return_value="def test_add(): assert add(1, 2) == 3"):
        result = runner.invoke(app, ["test", str(code_file)])
    assert result.exit_code == 0
    assert "Generated" in result.stdout


def test_test_command_save_flag(tmp_path):
    code_file = tmp_path / "calc.py"
    code_file.write_text("def add(a, b): return a + b")
    with patch("main.analyze_code", return_value="No issues."), \
         patch("main.generate_tests", return_value="def test_add(): assert add(1, 2) == 3"):
        result = runner.invoke(app, ["test", str(code_file), "--save"])
    assert result.exit_code == 0
    assert "saved to test_calc.py" in result.stdout
    Path("test_calc.py").unlink(missing_ok=True)


def test_chat_command_file_not_found():
    result = runner.invoke(app, ["chat", "nonexistent.py"])
    assert result.exit_code == 1


def test_chat_command_exits_on_quit(tmp_path):
    code_file = tmp_path / "code.py"
    code_file.write_text("def add(a, b): return a + b")
    with patch("main.chat_response", return_value="It adds two numbers."):
        result = runner.invoke(app, ["chat", str(code_file)], input="what does this do?\nquit\n")
    assert result.exit_code == 0
    assert "Chat mode active" in result.stdout


def test_yaml_instructions_injected(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "codelens.yaml").write_text("instructions: Always use Mockito.")
    with patch("agents.analyzer.ollama") as mock_ollama:
        mock_ollama.chat.return_value = {'message': {'content': 'ok'}}
        agents.analyzer.explain_code("def f(): pass")
        system_content = mock_ollama.chat.call_args.kwargs['messages'][0]['content']
        assert "Mockito" in system_content


def test_yaml_missing_no_error(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with patch("agents.analyzer.ollama") as mock_ollama:
        mock_ollama.chat.return_value = {'message': {'content': 'ok'}}
        result = agents.analyzer.explain_code("def f(): pass")
    assert result == 'ok'