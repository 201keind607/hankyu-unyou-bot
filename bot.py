import os
import requests
from datetime import datetime, date, timedelta, timezone

# ==========================================
# Discord Webhook
# ==========================================

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK"]

# ==========================================
# 日本時間
# ==========================================

JST = timezone(timedelta(hours=9))

# ==========================================
# API設定
# ==========================================

API_URL = "https://www.elesite-next.com/fastapi/get_unyoutable"

ROUTE_NAME = "阪急京都線"

PARAMS = {
    "rosen_code": "hankyu_kt",
    "day_id": 17,                # 平日
    "edit_mode": "false",
    "selected_shotei_index": -1,
    "route_id": 517
}

# ==========================================
# 運用設定
# 「運用ID : メモ」
# ここだけ編集すればOK
# ==========================================

OPERATIONS = {

    "平日特急": {

        802: "特急A 桂-桂",
        810: "特急B 桂-正雀③"

    },

    "平日準特急": {

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

    r = requests.get(
        API_URL,
        params=params,
        timeout=20
    )

    r.raise_for_status()

    return r.json()

# ==========================================
# unyou_idで検索しやすい辞書へ変換
# ==========================================

def create_unyou_dict(data):

    result = {}

    for table in data["unyou_table"]:

        for group in table["unyou_group"]:

            unyou_id = group.get("unyou_id")

            if unyou_id is not None:

                result[unyou_id] = group

    return result

# ==========================================
# 運用取得
# ==========================================

def get_operation(unyou_dict, unyou_id):

    return unyou_dict.get(unyou_id)# ==========================================
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

    now = datetime.now(JST)

    payload = {

        "embeds": [

            {

                "title": f"🚨 {ROUTE_NAME}",

                "description":
                    f"{now.year}年{now.month}月{now.day}日 "
                    f"{now.hour:02d}時{now.minute:02d}分取得",

                "fields": [

                    {

                        "name": "エラー",

                        "value": message

                    }

                ]

            }

        ]

    }

    send_webhook(payload)


# ==========================================
# カテゴリ別送信
# ==========================================

def send_category(category_name, operation_list, unyou_dict):

    now = datetime.now(JST)

    description = ""

    for unyou_id, memo in operation_list.items():

        group = get_operation(
            unyou_dict,
            unyou_id
        )

        # --------------------------
        # 運用が見つからない
        # --------------------------

        if group is None:

            description += (
                f"■ 運用 {unyou_id}\n"
                f"車両：登録なし\n"
                f"備考：なし\n"
                f"メモ：{memo}\n\n"
            )

            continue

        # --------------------------
        # 車両
        # --------------------------

        sharyo = (
            group.get("display_sharyo")
            or group.get("sharyo")
        )

        if not sharyo:

            sharyo = "登録なし"

        # --------------------------
        # 備考
        # --------------------------

        bikou = group.get(
            "sharyo_bikou"
        )

        if bikou:

            bikou_text = " / ".join(bikou)

        else:

            bikou_text = "なし"

        # --------------------------
        # 表示
        # --------------------------

        description += (

            f"■ 運用 {unyou_id}\n"

            f"車両：{sharyo}\n"

            f"備考：{bikou_text}\n"

            f"メモ：{memo}\n\n"

        )

    payload = {

        "embeds": [

            {

                "title": category_name,

                "description":
                    f"{now.year}年{now.month}月{now.day}日 "
                    f"{now.hour:02d}時{now.minute:02d}分取得",

                "fields": [

                    {

                        "name": category_name,

                        "value": description

                    }

                ]

            }

        ]

    }

    send_webhook(payload)# ==========================================
# 実行
# ==========================================

def main():

    print("===================================")
    print(f"{ROUTE_NAME} 運用情報取得開始")
    print("===================================")

    try:

        # API取得
        data = get_unyou()

        # unyou_id検索用辞書作成
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

            print(f"{category_name} 送信完了")

        print("========================")
        print("全カテゴリ送信完了")
        print("========================")

    except Exception as e:

        print("========================")
        print("API取得失敗")
        print("========================")
        print(e)

        try:

            send_error(
                f"API取得失敗\n\n{e}"
            )

        except Exception as err:

            print("Discord通知失敗")
            print(err)


# ==========================================
# 起動
# ==========================================

if __name__ == "__main__":

    main()
