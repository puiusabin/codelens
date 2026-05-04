from typer.testing import CliRunner
from main import app

runner = CliRunner()

def test_cli_help():
    """Sanity check: ensures the CLI loads and displays the help menu."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "CodeLens" in result.stdout