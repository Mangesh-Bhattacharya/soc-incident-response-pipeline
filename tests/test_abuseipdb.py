import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from socpipeline.abuseipdb import check_ip


def test_missing_api_key_returns_error_without_network_call():
    result = check_ip("1.2.3.4", api_key=None)
    assert result.found is False
    assert "ABUSEIPDB_API_KEY" in result.error


@patch("socpipeline.abuseipdb.requests.get")
def test_known_abusive_ip(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "abuseConfidenceScore": 92,
            "totalReports": 341,
            "countryCode": "RO",
            "isp": "Example Hosting SRL",
            "isTor": True,
        }
    }
    mock_get.return_value = mock_response

    result = check_ip("185.220.101.45", api_key="fake-key")

    assert result.found is True
    assert result.abuse_confidence_score == 92
    assert result.is_tor is True


@patch("socpipeline.abuseipdb.requests.get")
def test_http_error_surfaces_as_not_found(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_get.return_value = mock_response

    result = check_ip("1.2.3.4", api_key="fake-key")

    assert result.found is False
    assert "429" in result.error
