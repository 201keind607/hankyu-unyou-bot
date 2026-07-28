import os
import requests
from datetime import datetime, date

# ==========================================
# Discord Webhook
# ==========================================

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK"]

# ==========================================
# API設定
# ==========================================

API_URL = "https://www.elesite-next.com/fastapi/get_unyoutable"

ROUTE_NAME = "阪急京都線"

PARAMS = {
    "rosen_code": "hankyu_kt",
    "day_id": 17,          # 平日
    "edit_mode": "false",
    "selected_shotei_index": -1,
    "route_id": 517
}

# ==========================================
# 運用設定
# 運用ID : 個別メモ
# ==========================================

OPERATIONS = {

    "平日特急": {
        802: "特急A 桂-桂",
        810: "特急B 桂-正雀③"
    },

    "平日朝準特急": {
        242: "準特急1 河原6:00→梅田6:44",
        245: "準特急2 河原7:04→梅田7:55・梅田8:02→河原8:55",
        735: "準特急3 梅田6:14→河原7:00",
        246: "準特急4 梅田6:48→河原7:33・河原7:41→梅田8:32・梅田8:38→河原9:29"
    },

    "平日急行": {
        682: "朝急行1 天神5:36→梅田6:10",
        810: "朝急行2 天神5:52→梅田6:24→特急運用",
        737: "朝急行3 河原5:46→梅田6:36"
    },

    "平日淡路行き": {
        815: "8R 北千里22:07→淡路22:25",
        230: "7R 北千里20:49→淡路21:08",
        232: "7R 北千里21:52→淡路22:11"
    }

}

# ==========================================
# API取得
# ==========================================

def get_unyou():

    params = PARAMS.copy()
    params["select_date"] = str(date.today())

    r = requests.get(API_URL, params=params, timeout=20)
    r.raise_for_status()

    return r.json()

# ==========================================
# unyou_idから検索しやすい形へ変換
# ==========================================

def create_unyou_dict(data):

    result = {}

    for table in data["unyou_table"]:
        for group in table["unyou_group"]:

            result[group["unyou_id"]] = group

    return result

# ==========================================
# 運用情報取得
# ==========================================

def get_operation(unyou_dict, unyou_id):

    if unyou_id in unyou_dict:
        return unyou_dict[unyou_id]

    return None
# ==========================================
# Discord送信
# ==========================================

def send_webhook(payload):

    r = requests.post(
        WEBHOOK_URL,
        json=payload,
        timeout=20
    )

    r.raise_for_status()


# ==========================================
# API取得失敗通知
# ==========================================

def send_error(message):

    now = datetime.now()

    payload = {
        "content":
            f"🚨 {ROUTE_NAME} 運用情報\n\n"
            f"{now.year}年{now.month}月{now.day}日 
            f"{message}"
    }

    send_webhook(payload)


# ==========================================
# カテゴリ別送信
# ==========================================

def send_category(category_name, operation_list, unyou_dict):

    now = datetime.now()

    description = ""

    for unyou_id, memo in operation_list.items():

        group = get_operation(unyou_dict, unyou_id)

        # --------------------------
        # 運用が見つからない
        # --------------------------

        if group is None:

            description += (
                f"■ 運用{unyou_id}\n"
                f"車両：登録なし\n"
                f"備考：なし\n"
                f"メモ：{memo}\n\n"
            )

            continue

        # --------------------------
        # 車両
        # --------------------------

        sharyo = group.get("sharyo")

        if sharyo:
            sharyo_text = sharyo
        else:
            sharyo_text = "登録なし"

        # --------------------------
        # 車両備考
        # --------------------------

        bikou = group.get("sharyo_bikou")

        if bikou:
            bikou_text = " / ".join(bikou)
        else:
            bikou_text = "なし"

        # --------------------------
        # 表示
        # --------------------------

        description += (
            f"■ 運用{unyou_id}\n"
            f"車両：{sharyo_text}\n"
            f"備考：{bikou_text}\n"
            f"メモ：{memo}\n\n"
        )

    payload = {

        "embeds": [

            {

                "title": category_name,

                "description":
                    f"{now.year}年{now.month}月{now.day}日 "

                "fields": [

                    {

                        "name": category_name,

                        "value": description

                    }

                ]

            }

        ]

    }

    send_webhook(payload)
# ==========================================
# 実行
# ==========================================

def main():

    print("===================================")
    print("阪急京都線 運用情報取得開始")
    print("===================================")

    try:

        # API取得
        data = get_unyou()

        # unyou_idで検索できる辞書へ変換
        unyou_dict = create_unyou_dict(data)

        print(f"取得件数：{len(unyou_dict)}件")

        # カテゴリごとに送信
        for category_name, operation_list in OPERATIONS.items():

            print(f"{category_name} を送信中...")

            send_category(
                category_name,
                operation_list,
                unyou_dict
            )

        print("送信完了")

    except Exception as e:

        print("API取得失敗")
        print(e)

        try:
            send_error("API取得失敗")
        except Exception as err:
            print("Discord通知失敗")
            print(err)


# ==========================================
# 起動
# ==========================================

if __name__ == "__main__":
    main()
