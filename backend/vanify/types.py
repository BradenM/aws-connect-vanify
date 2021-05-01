"""AWS Connect Vanify Types."""

from typing import Dict, Literal, Optional, TypedDict

ContactFlowInitMethod = Literal["INBOUND", "OUTBOUND", "TRANSFER", "CALLBACK", "API"]
ContactFlowChannel = Literal["VOICE", "CHAT"]


class ContactFlowEndpoint(TypedDict):
    Address: str
    Type: str


class ContactFlowQueue(TypedDict):
    ARN: str
    Name: str


class ConnectEventContactData(TypedDict):
    Attributes: Dict[str, str]
    Channel: ContactFlowChannel
    ContactId: str
    CustomerEndpoint: ContactFlowEndpoint
    InitialContactId: str
    InitiationMethod: ContactFlowInitMethod
    InstanceArn: str
    PreviousContactId: str
    Queue: Optional[ContactFlowQueue]
    SystemEndpoint: Optional[ContactFlowEndpoint]
    MediaStreams: Dict


class ConnectEventDetails(TypedDict):
    ContactData: ConnectEventContactData
    Parameters: Dict[str, str]


class ConnectContactFlowEvent(TypedDict):
    Details: ConnectEventDetails
    Name: str
