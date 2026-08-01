# ==========================================
# import
# ==========================================

import config
import common


# ==========================================
# 運用番号設定
# ==========================================

OPERATIONS = {

    "平日特急": {
        802: "特急A 桂-桂",
        810: "特急B 桂-正雀③",
    },

    "平日準特急": {
        242: "準特急1 河原町6:00→梅田6:44",
        245: "準特急2 河原町7:04→梅田7:55・梅田8:02→河原町8:55",
        735: "準特急3 梅田6:14→河原町7:00",
        246: "準特急4 梅田6:48→河原町7:33",
    },

    "平日急行": {
        682: "朝急行1 天神5:36→梅田6:10",
        810: "朝急行2 天神5:52→梅田6:24→特急運用",
        737: "朝急行3 河原町5:46→梅田6:36",
    },

    "平日淡路行き": {
        # 後で追加
    },

    # 土休日追加予定
}


# ==========================================
# 運用番号検索用辞書作成
# ==========================================

def create_unyou_dict(data):

    result = {}

    for item in data:

        if "unyou_id" in item:

            result[item["unyou_id"]] = item

    return result


# ==========================================
# 車両番号取得
# ==========================================

def get_vehicle_number(data):

    if not data:
        return "取得失敗"


    vehicle = data.get("vehicle")


    if vehicle:
        return vehicle


    return "車両情報なし"


# ==========================================
# Discord Embed作成
# ==========================================

def create_embeds(category, unyou_dict):

    embeds = []


    for unyou_id, memo in OPERATIONS.get(category, {}).items():

        data = unyou_dict.get(unyou_id)


        vehicle = get_vehicle_number(data)


        embeds.append(
            {
                "title": category,
                "description": (
                    f"運用番号：{unyou_id}\n"
                    f"車両：{vehicle}\n"
                    f"備考：{memo}"
                )
            }
        )


    return embeds


# ==========================================
# 阪急京都線取得
# ==========================================

def get_operations():

    params = config.API_PARAMS["hankyu_kyoto"]


    data = common.get_unyou(
        config.API_URL,
        {
            "rosen_code": params["rosen_code"],
            "day_id": config.DAY_ID[params["day_type"]],
            "edit_mode": "false",
            "selected_shotei_index": -1,
            "route_id": params["route_id"],
        }
    )


    unyou_dict = create_unyou_dict(data)


    embeds = []


    for category in OPERATIONS:

        embeds.extend(
            create_embeds(
                category,
                unyou_dict
            )
        )


    return embeds
