import json
from datetime import datetime

import pytest
from pytest_mock import MockFixture
from vanify import app


@pytest.fixture
def mock_vanify_model(mocker: MockFixture):
    mock_item = mocker.MagicMock()
    mock_item.date = datetime.utcnow()
    mock_item.as_dict = lambda *args: dict(date="today")
    mock_model = mocker.patch.object(app, "VanifyModel")
    mock_model.scan.return_value = [mock_item]
    return mock_model, mock_item


def test_recent(mocker: MockFixture, mock_vanify_model):
    resp = app.recent(mocker.MagicMock(), mocker.MagicMock())
    resp_body = json.loads(resp["body"])
    assert resp["statusCode"] == 200
    assert resp_body == {"recent": [{"date": "today"}]}
