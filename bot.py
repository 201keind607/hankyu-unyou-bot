import requests
from datetime import datetime, date
import os

print("最新版確認")


# ==========================
# 設定
# ==========================

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK"]


TARGET_UNYOU = [
    6088,
    5113
]


MEMO = {
    6088: "特急A 桂-桂",
    5113: "特急B 桂-正雀③"
}


API_URL = "https://www.elesite-next.com/fastapi/get_unyoutable"


ROUTE_NAME = "阪急京都線"



# ==========================
# API取得
# ==========================

def get_unyou():

    params = {

        "rosen_code": "hankyu_kt",

        "day_id": 17,

        "select_date": str(date.today()),

        "edit_mode": "false",

        "selected_shotei_index": -1,

        "route_id": 517
    }


    r = requests.get(
        API_URL,
        params=params
    )

    r.raise_for_status()

    return r.json()



# ==========================
# 検索
# ==========================

def search_unyou(data):

    result = []

    all_ids = []


    for table in data["unyou_table"]:

        for group in table["unyou_group"]:

            unyou_id = group.get("unyou_id")

            all_ids.append(unyou_id)


            if unyou_id in TARGET_UNYOU:

                result.append(group)


    print("取得管理番号:")
    print(all_ids[:100])


    print("対象番号確認:")
    print(
        [
            x for x in all_ids
            if x in TARGET_UNYOU
        ]
    )


    return result



# ==========================
# Discord送信
# ==========================

def send_discord(groups):

    now = datetime.now()

    embeds = []


    for group in groups:

        unyou_id = group["unyou_id"]


        sharyo = group.get("sharyo")


        if sharyo:

            sharyo_text = sharyo

        else:

            sharyo_text = "登録なし"



        bikou = group.get("sharyo_bikou")


        if bikou:

            bikou_text = "\n".join(bikou)

        else:

            bikou_text = "なし"



        text = (

            f"**車両**\n"
            f"{sharyo_text}\n\n"

            f"**備考**\n"
            f"{bikou_text}"

        )


        memo = MEMO.get(
            unyou_id
        )


        if memo:

            text += (

                "\n\n**メモ**\n"
                f"{memo}"

            )


        embeds.append({

            "title": f"管理番号 {unyou_id}",

            "description": text

        })


    payload = {

        "content":
            f"🚃 {ROUTE_NAME} 運用情報\n"
            f"{now.year}年{now.month}月{now.day}日 "
            f"{now.hour}時{now.minute}分取得",

        "embeds": embeds

    }


    r = requests.post(
        WEBHOOK_URL,
        json=payload
    )

    r.raise_for_status()



# ==========================
# 実行
# ==========================

if __name__ == "__main__":

    print("運用取得開始")


    data = get_unyou()


    groups = search_unyou(
        data
    )


    if groups:

        print("対象発見")

        send_discord(groups)

        print("送信完了")


    else:

        print("対象なし")
