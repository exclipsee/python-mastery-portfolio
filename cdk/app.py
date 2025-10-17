from __future__ import annotations

# ruff: noqa: I001

import os

import aws_cdk as cdk

from portfolio_stack import PortfolioStack


def main() -> None:
    app = cdk.App()

    env = cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region=os.getenv("CDK_DEFAULT_REGION", "eu-central-1"),
    )

    PortfolioStack(
        app,
        "PortfolioApiStack",
        env=env,
        description="Deploy FastAPI portfolio as ECS Fargate service with ALB",
    )

    app.synth()


if __name__ == "__main__":
    main()
