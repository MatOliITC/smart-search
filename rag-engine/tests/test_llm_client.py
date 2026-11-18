import pytest

import config
from errors import RagError
from llm_client import create_client


@pytest.mark.parametrize('api_key', [None, ''])
def test_missing_api_key(monkeypatch, api_key):
    monkeypatch.setitem(
        config.PROVIDERS,
        'openai',
        {'base_url': 'https://example.com/v1', 'api_key': api_key},
    )
    with pytest.raises(RagError) as info:
        create_client('openai')
    assert info.value.code == 'MISSING_API_KEY'


def test_unknown_provider():
    with pytest.raises(RagError) as info:
        create_client('opeani')
    assert info.value.code == 'UNKNOWN_PROVIDER'


def test_valid_provider_returns_client(monkeypatch):
    monkeypatch.setitem(
        config.PROVIDERS,
        'openai',
        {'base_url': 'https://example.com/v1', 'api_key': 'sk-test'},
    )
    client = create_client('openai')
    assert str(client.base_url).startswith('https://example.com/v1')
