import os
import requests
from datetime import datetime, timedelta, timezone


# ==========================================
# Discord Webhook
# ==========================================

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK"]


# ==========================================
# 日本時間
# ==========================================

JST = timezone(
    timedelta(hours=9)
)


# ==========================================
# API設定
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
        "準特急2 河原町7:04→梅田7:55・梅田8:02→河原町8:55",

        735:
        "準特急3 梅田6:14→河原町7:00",

        246:
        "準特急4 梅田6:48→河原町7:33"

    },


    "平日急行": {

        682:
        "朝急行1 天神5:36→梅田6:10",

        810:
        "朝急行2 天神5:52→梅田6:24→特急運用",

        737:
        "朝急行3 河原町5:46→梅田6:36"

    },


    "平日淡路行き": {

        815:
        "8R 北千里22:07→淡路22:25",

        230:
        "7R 北千里20:49→淡路21:08",

        232:
        "7R 北千里21:52→淡路22:11"

    }

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
# unyou_id検索用辞書作成
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

    response = requests.post(

        WEBHOOK_URL,

        json=payload,

        timeout=20

    )


    response.raise_for_status()



# ==========================================
# エラー通知
# ==========================================

def send_error(message):

    now = datetime.now(JST)


    payload = {

        "embeds": [

            {

                "title":
                    f"🚨 {ROUTE_NAME}",


                "description":
                    f"{now:%Y年%m月%d日 %H時%M分}取得",


                "fields": [

                    {

                        "name":
                            "エラー",


                        "value":
                            str(message)

                    }

                ]

            }

        ]

    }


    send_webhook(
        payload
    )





# ==========================================
# カテゴリ送信
# ==========================================

def send_category(
    category_name,
    operation_list,
    unyou_dict
):

    now = datetime.now(JST)


    messages = []



    for unyou_id, memo in operation_list.items():


        group = get_operation(

            unyou_dict,

            unyou_id

        )



        if group is None:


            messages.append(

                f"■ 運用 {unyou_id}\n"
                f"車両：登録なし\n"
                f"備考：なし\n"
                f"メモ：{memo}"

            )


            continue



        sharyo = (

            group.get(
                "display_sharyo"
            )

            or group.get(
                "sharyo"
            )

            or "登録なし"

        )



        bikou = group.get(
            "sharyo_bikou"
        )



        if bikou:

            bikou_text = " / ".join(
                bikou
            )

        else:

            bikou_text = "なし"



        messages.append(

            f"■ 運用 {unyou_id}\n"
            f"車両：{sharyo}\n"
            f"備考：{bikou_text}\n"
            f"メモ：{memo}"

        )



    description = (

        f"{now:%Y年%m月%d日 %H時%M分}取得\n\n"

        +

        "\n\n".join(messages)

    )



    if category_name in ["平日特急", "平日準特急"]:

        color = 16711680


    elif category_name == "平日急行":

        color = 16776960


    else:

        color = 3447003



    payload = {

        "embeds": [

            {

                "title":
                    category_name,


                "description":
                    description,


                "color":
                    color

            }

        ]

    }


    send_webhook(
        payload
    )# ==========================================
# 実行
# ==========================================

def main():

    print("==============================")
    print(f"{ROUTE_NAME} 運用情報取得開始")
    print("==============================")


    try:

        now = datetime.now(JST)



        # --------------------------
        # 時間帯別送信設定
        # --------------------------

        if now.hour == 7:


            target_categories = [

                "平日準特急",

                "平日急行"

            ]


        elif now.hour == 8:


            target_categories = [

                "平日特急",

            ]


        elif now.hour == 17:


            target_categories = [

                "平日淡路行き",

            ]



        else:

　
　　　　　　　print("対象時間外")
　　　　　　　return



        # --------------------------
        # API取得
        # --------------------------

        data = get_unyou()



        # --------------------------
        # 辞書化
        # --------------------------

        unyou_dict = create_unyou_dict(
            data
        )


        print(
            f"取得件数：{len(unyou_dict)}件"
        )



        # --------------------------
        # Discord送信
        # --------------------------

        for category_name in target_categories:


            print(
                f"{category_name}送信中..."
            )



            send_category(

                category_name,

                OPERATIONS[category_name],

                unyou_dict

            )



            print(
                f"{category_name}送信完了"
            )



        print("==============================")
        print("全カテゴリ送信完了")
        print("==============================")



    except Exception as e:


        print("==============================")
        print("取得失敗")
        print(e)
        print("==============================")


        try:

            send_error(e)


        except Exception as err:

            print(
                "エラー通知失敗"
            )

            print(err)



# ==========================================
# 起動
# ==========================================

if __name__ == "__main__":

    main()
