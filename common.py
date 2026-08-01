import requests


def get_unyou(api_url, params):
    """
    APIから運用表を取得
    """

    response = requests.get(
        api_url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def send_discord(webhook, embeds):
    """
    Discordへ送信
    """

    if not webhook:
        raise ValueError("Webhookが設定されていません。")

    response = requests.post(
        webhook,
        json={
            "embeds": embeds
        },
        timeout=30
    )

    response.raise_for_status()
