"""AWS Connect Vanify handler."""
import logging
from datetime import datetime
from typing import TypedDict

import phonenumbers
from vanify import convert
from vanify.models import VanifyModel
from vanify.types import ConnectContactFlowEvent

logger = logging.getLogger("vanify")


class VanifyParams(TypedDict):
    inputNumber: str


def create_vanify_entry(params: VanifyParams, contact_id: str, caller_id: str):
    """Create vanify db entry."""
    _caller_id = phonenumbers.parse(caller_id)
    caller_id = phonenumbers.format_number(_caller_id, phonenumbers.PhoneNumberFormat.E164)
    utc_now = datetime.utcnow()
    inst = VanifyModel(caller_id, date=utc_now, input=params["inputNumber"], contact_id=contact_id)
    return inst


def handler(event: ConnectContactFlowEvent, context):
    """Vanify entrypoint."""
    logger.info("entering vanify handler:", event, context)
    params: VanifyParams = event["Details"]["Parameters"]
    contact_id = event["Details"]["ContactData"]["ContactId"]
    caller_id = event["Details"]["ContactData"]["CustomerEndpoint"]["Address"]
    inst = create_vanify_entry(params, contact_id, caller_id)
    result = convert.VanifiedResult.from_phone_number(params["inputNumber"], 5)
    inst.results = result.word_results
    inst.save()
    logger.info("created new vanify db entry: %s", inst.__dict__)
    # create response item.
    resp_body = ",".join(result.word_results)
    prompt_as_tel_tmpl = '<say-as interpret-as="telephone">{}</say-as>'
    prompt_body_resp = ", ".join([prompt_as_tel_tmpl.format(r) for r in result.word_results])
    prompt_resp = f'<speak>Five vanity numbers available for {prompt_as_tel_tmpl.format(params["inputNumber"])} are: {prompt_body_resp} </speak>'
    body = {"results": resp_body, "prompt_response": prompt_resp}
    return body
