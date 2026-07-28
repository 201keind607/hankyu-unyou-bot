import os
import requests
from datetime import datetime, timedelta, timezone


# ==========================================
# Discord
# ==========================================

WEBHOOK_URL = os.environ.get(
    "DISCORD_WEBHOOK"
)


# ==========================================
# 日本時間
# ==========================================

JST = timezone(
    timedelta(hours=9)
)


# ==========================================
# API
# ==========================================

API_URL = (
    "https://www.elesite-next.com/"
    "fastapi/get_unyoutable"
)


ROUTE_NAME = "阪急京都線"


PARAMS = {

    "rosen_code": "hankyu_kt",

    "day_id": 17,

    "edit_mode": "false",

    "selected_shotei_index": -1,

    "route_id": 517

}


# ==========================================
# 運用設定
# ==========================================

OPERATIONS = {


    "平日特急": {

        802: "特急A 桂-桂",

        810: "特急B 桂-正雀③"

    },


    "平日準特急": {

        242:
        "準特急1 河原町6:00→梅田6:44",

        245:
        "準特急2 河原町7:04→梅田7:55"

    },


    "平日急行": {

        682:
        "朝急行1 天神5:36→梅田6:10",

        810:
        "朝急行2 天神5:52→梅田6:24"

    },


    "平日淡路行き": {

        815:
        "8R 北千里22:07→淡路22:25",

        230:
        "7R 北千里20:49→淡路21:08"

    }
    # ==========================================
# API取得
# ==========================================

def get_unyou():

    params = PARAMS.copy()

    params["select_date"] = str(
        datetime.now(JST).date()
    )


    response = requests.get(

        API_URL,

        params=params,

        timeout=20

    )


    response.raise_for_status()


    return response.json()



# ==========================================
# 運用辞書作成
# ==========================================

def create_unyou_dict(data):

    result = {}


    for table in data.get(
        "unyou_table",
        []
    ):

        for group in table.get(
            "unyou_group",
            []
        ):

            unyou_id = group.get(
                "unyou_id"
            )


            if unyou_id is not None:

                result[unyou_id] = group


    return result



# ==========================================
# 運用取得
# ==========================================

def get_operation(
    unyou_dict,
    unyou_id
):

    return unyou_dict.get(
        unyou_id
    )
    # ==========================================
# Discord送信
# ==========================================

def send_webhook(payload):

    if not WEBHOOK_URL:

        print(
            "Webhook未設定"
        )

        return


    requests.post(

        WEBHOOK_URL,

        json=payload,

        timeout=20

    ).raise_for_status()



# ==========================================
# カテゴリ送信
# ==========================================

def send_category(
    name,
    operations,
    unyou_dict
):

    now = datetime.now(JST)


    lines = []


    for unyou_id, memo in operations.items():

        group = get_operation(
            unyou_dict,
            unyou_id
        )


        if group:

            sharyo = (
                group.get(
                    "display_sharyo"
                )
                or "登録なし"
            )


            bikou = group.get(
                "sharyo_bikou"
            )


            if bikou:

                bikou = " / ".join(
                    bikou
                )

            else:

                bikou = "なし"


        else:

            sharyo = "登録なし"

            bikou = "なし"



        lines.append(

            f"■ {unyou_id}\n"
            f"車両：{sharyo}\n"
            f"備考：{bikou}\n"
            f"メモ：{memo}"

        )



    payload = {

        "embeds":[

            {

                "title":name,

                "description":

                f"{now:%Y年%m月%d日 %H:%M}取得\n\n"
                +
                "\n\n".join(lines)

            }

        ]

    }


    send_webhook(
        payload
    )

}
