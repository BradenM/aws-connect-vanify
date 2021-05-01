"""AWS Connect Vanify Models."""

from datetime import datetime, timezone

from pynamodb.attributes import UnicodeAttribute, UnicodeSetAttribute, UTCDateTimeAttribute
from pynamodb.constants import DATETIME_FORMAT
from pynamodb.models import Model


class VanifyModel(Model):
    class Meta:
        table_name = "ConnectVanify"
        region = "us-east-1"

    contact_id = UnicodeAttribute(attr_name="contactId", hash_key=True)
    caller_id = UnicodeAttribute(range_key=True, attr_name="callerId")
    date = UTCDateTimeAttribute()
    input = UnicodeAttribute(default_for_new=datetime.now)
    results = UnicodeSetAttribute()

    def as_dict(self):
        """Dump instance as dict."""
        date = self.date.astimezone(timezone.utc).strftime(DATETIME_FORMAT)
        attrs = self.attribute_values
        attrs["date"] = date
        attrs["results"] = list(self.results)
        return attrs
