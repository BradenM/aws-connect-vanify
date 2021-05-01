"""AWS Connect Vanify deploy main."""
from pathlib import Path

import typer

from .connect import ConnectApi

FLOW_NAME = "vf-vanifyNumber"


def get_flow_tmpl() -> str:
    """Retrieve vanify contact flow template."""
    ROOT = Path(__file__).parent
    flow_path = ROOT / "flow.json"
    return flow_path.read_text()


app = typer.Typer(name="aws-connect-vanify")


@app.command()
def deploy_flow(service_name: str, stage: str):
    """Deploy AWS Connect vanify contact flow."""
    typer.secho(
        f"Deploying flow: {service_name} @ {stage}", bold=True, fg=typer.colors.BRIGHT_WHITE
    )
    connect = ConnectApi()
    lambda_arn = connect.get_lambda_arn(service_name=service_name, stage=stage, name="vanify")
    flow_content = get_flow_tmpl().replace("<LAMBDA_ARN>", lambda_arn)
    flow_id = connect.get_contact_flow(FLOW_NAME)
    if not flow_id:
        typer.secho(
            f"Could not find Flow ID for {FLOW_NAME}, creating...",
            bold=True,
            fg=typer.colors.BRIGHT_YELLOW,
        )
        connect.create_contact_flow(FLOW_NAME, flow_content)
    else:
        typer.secho(f"Got Flow ID: {flow_id}", bold=True, fg=typer.colors.BRIGHT_WHITE)
        connect.update_contact_flow(flow_content, flow_id)
    typer.secho("Updated contact flow!", fg=typer.colors.BRIGHT_GREEN)
    connect.associate_lambda_arn(lambda_arn=lambda_arn)
    typer.secho("Associated lambda with instance!", fg=typer.colors.BRIGHT_GREEN)


@app.callback()
def main():
    """AWS Connect Vanify deploy helper."""


if __name__ == "__main__":
    app()
