"""AWS Connect Vanify Models."""

from datetime import datetime

from pynamodb.attributes import UnicodeAttribute, UnicodeSetAttribute, UTCDateTimeAttribute
from pynamodb.models import Model


class VanifyModel(Model):
    class Meta:
        table_name = "ConnectVanify"
        region = "us-east-1"

    caller_id = UnicodeAttribute(hash_key=True, attr_name="callerId")
    date = UTCDateTimeAttribute()
    contact_id = UnicodeAttribute(attr_name="contactId")
    input = UnicodeAttribute(default_for_new=datetime.now)
    results = UnicodeSetAttribute()
