"""Connect Api Wrapper."""

import os
from functools import partial
from itertools import chain
from typing import Callable, ClassVar, List, Optional, Tuple

import attr
import boto3
import jmespath
from botocore.client import BaseClient


@attr.s(auto_attribs=True)
class ConnectApi:
    """Interface for interacting with the AWS Connect API."""

    _PAGINATED: ClassVar[List[Tuple[str, str, Optional[Tuple[str, ...]]]]] = [
        (
            "contact_flows",
            "list_contact_flows",
        ),
        (
            "phone_numbers",
            "list_phone_numbers",
            (
                "PhoneNumber",
                "Id",
            ),
        ),
    ]

    get_contact_flow: Callable[[str], Optional[str]] = attr.ib(init=False)
    get_phone_number: Callable[[str], Optional[str]] = attr.ib(init=False)

    _client: Optional[BaseClient] = None
    instance_id: str = os.environ.get("INSTANCE_ID")
    aws_region: str = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

    def __attrs_post_init__(self):
        for opts in self._PAGINATED:
            self._create_paginator(*opts)

    @property
    def client(self) -> BaseClient:
        """Lazily instantiated Boto3 Connect client. """
        if not self._client:
            self._client = boto3.client("connect", region_name=self.aws_region)
        return self._client

    def _create_paginator(self, attribute: str, method: str, key=("Name",), **kwargs):
        """Create dynamic properties/methods for paginated items.

        Examples:
            >>> ivr = ConnectApi()
            >>> ivr.queues
            <botocore.paginate.PageIterator>
            >>> ivr.get_queue('my-queue')
            '123-queue-id'
        Args:
            attribute: base attribute name to use.
            method: boto3 method to paginate.
        Keyword Args:
            key: Keys name used for querying profiles.
                Defaults to Name.
        """

        def do_paginate(client, meth, attr, *args, **kws):
            if not getattr(self, attr, None):
                pager = client.get_paginator(meth)
                kws.update(dict(InstanceId=self.instance_id))
                pager_iterator = pager.paginate(**kws)
                results = pager_iterator.build_full_result()
                setattr(self, attr, results)
            return getattr(self, attr)

        def query_profile(profile_attr, name, key=("Name",), complete=False):
            profiles = getattr(self, profile_attr)
            query = name.strip()
            results = (jmespath.search(f"*[?{k}==`{query}`][]", profiles) for k in key)
            profile = next(chain.from_iterable(results), None)
            if profile:
                if complete:
                    return profile
                return profile.get("Id", None)
            return None

        if not hasattr(self, attribute):
            setattr(self, f"_{attribute}", None)
            self.__class__ = type(
                self.__class__.__name__,
                (self.__class__,),
                {
                    attribute: property(
                        partial(
                            do_paginate,
                            self.client,
                            method,
                            f"_{attribute}",
                            **kwargs,
                        )
                    ),
                    f'get_{attribute.rstrip("s")}': partial(query_profile, attribute, key=key),
                },
            )

    def get_aws_account_id(self) -> str:
        """Retrieve currently authenticated AWS account id."""
        sts = boto3.client("sts", region_name=self.aws_region)
        identity = sts.get_caller_identity()
        return identity["Account"]

    def update_contact_flow(self, content: str, contact_flow: str):
        return self.client.update_contact_flow_content(
            InstanceId=self.instance_id, ContactFlowId=contact_flow, Content=content
        )

    def associate_lambda_arn(self, lambda_arn: str):
        return self.client.associate_lambda_function(
            InstanceId=self.instance_id, FunctionArn=lambda_arn
        )
