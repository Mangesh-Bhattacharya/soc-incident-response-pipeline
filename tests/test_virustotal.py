import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from socpipeline.virustotal import check_file_hash


def test_missing_api_key_returns_error_without_network_call():
    result = check_file_hash("deadbeef", api_key=None)
    assert result.found is False
    assert "VT_API_KEY" in result.error


@patch("socpipeline.virustotal.requests.get")
def test_known_malicious_hash(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "attributes": {
                "last_analysis_stats": {"malicious": 58, "suspicious": 2, "harmless": 10, "undetected": 4},
                "reputation": -40,
                "type_description": "Win32 EXE",
            }
        }
    }
    mock_get.return_value = mock_response

    result = check_file_hash("275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0", api_key="fake-key")

    assert result.found is True
    assert result.malicious == 58
    assert result.total_engines == 74


@patch("socpipeline.virustotal.requests.get")
def test_unknown_hash_returns_not_found(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    result = check_file_hash("0" * 64, api_key="fake-key")

    assert result.found is False
    assert result.error is None
