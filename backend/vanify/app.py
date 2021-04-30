"""AWS Connect Vanify handler."""

from typing import TypedDict

from .types import ConnectContactFlowEvent


class VanifyParams(TypedDict):
    inputNumber: str


def handler(event: ConnectContactFlowEvent, context):
    params: VanifyParams = event["Details"]["Parameters"]
    body = {"output": params["inputNumber"]}
    return body
