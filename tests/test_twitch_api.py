from unittest.mock import patch

import pytest

from twitch_api import get_category_id

CLIENT_ID = "test_client_id"
OAUTH_TOKEN = "test_oauth_token"

def test_get_category_id_success() -> None:
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "data": [{"id": "12345"}]
        }

        result = get_category_id("test_category", CLIENT_ID, OAUTH_TOKEN)
        assert result == "12345"
        mock_get.assert_called_once_with(
            "https://api.twitch.tv/helix/games",
            headers={"Client-ID": CLIENT_ID, "Authorization": f"Bearer {OAUTH_TOKEN}"},
            params={"name": "test_category"},
        )