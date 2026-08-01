# ==========================================
# import
# ==========================================

from datetime import datetime

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

    },

}


# ==========================================
# 色設定
# ==========================================

COLORS = {

    "平日特急": 16711680,

    "平日準特急": 16711680,

    "平日急行": 16776960,

    "平日淡路行き": 3447003,

}


# ==========================================
# 運用番号辞書作成
# ==========================================

def create_unyou_dict(data):

    unyou_dict = {}

    for item in data:

        if "unyou_id" in item:

            unyou_dict[item["unyou_id"]] = item

    return unyou_dict



# ==========================================
# 車両番号取得
# ==========================================

def get_vehicle_number(data):

    if not data:

        return "取得失敗"


    for key in [
        "vehicle",
        "vehicle_no",
        "car_no",
        "car_number",
        "sharyo"
    ]:

        if key in data:

            return str(data[key])


    return "車両情報なし"



# ==========================================
# Embed作成
# ==========================================

def create_embed(category, unyou_dict):

    fields = []


    for unyou_id, memo in OPERATIONS.get(category, {}).items():

        data = unyou_dict.get(unyou_id)

        vehicle = get_vehicle_number(data)


        fields.append(
            {
                "name": f"運用番号 {unyou_id}",
                "value": (
                    f"車両：{vehicle}\n"
                    f"備考：{memo}"
                ),
                "inline": False
            }
        )


    if not fields:

        return None


    return {

        "title": category,

        "description": (
            f"{datetime.now().strftime('%Y年%m月%d日 %H:%M')}"
            "取得"
        ),

        "color": COLORS.get(
            category,
            3447003
        ),

        "fields": fields

    }



# ==========================================
# 阪急京都線 運用取得
# ==========================================

def get_operations():

    api_params = config.API_PARAMS["hankyu_kyoto"]


    params = {

        "rosen_code": api_params["rosen_code"],

        "day_id": config.DAY_ID[
            api_params["day_type"]
        ],

        "select_date": datetime.now().strftime(
            "%Y-%m-%d"
        ),

        "edit_mode": "false",

        "selected_shotei_index": -1,

        "route_id": api_params["route_id"],

    }


    data = common.get_unyou(
        config.API_URL,
        params
    )


    unyou_dict = create_unyou_dict(data)


    embeds = []


    for category in OPERATIONS:

        embed = create_embed(
            category,
            unyou_dict
        )


        if embed:

            embeds.append(embed)


    return embeds
