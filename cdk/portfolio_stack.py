from __future__ import annotations
# ruff: noqa: I001

from typing import Any

import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecr as ecr,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
)


class PortfolioStack(Stack):
    def __init__(self, scope: cdk.App, construct_id: str, **kwargs: Any) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(self, "Vpc", max_azs=2)

        cluster = ecs.Cluster(self, "Cluster", vpc=vpc)

        repo = ecr.Repository(self, "Repo", repository_name="python-mastery-portfolio")

        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "Service",
            cluster=cluster,
            cpu=256,
            desired_count=1,
            memory_limit_mib=512,
            public_load_balancer=True,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_ecr_repository(repo, tag="latest"),
                container_port=8000,
                environment={},
            ),
        )

        # Allow inbound HTTP
        fargate_service.load_balancer.connections.allow_from_any_ipv4(ec2.Port.tcp(80))

        cdk.CfnOutput(
            self,
            "LoadBalancerDNS",
            value=fargate_service.load_balancer.load_balancer_dns_name,
        )
