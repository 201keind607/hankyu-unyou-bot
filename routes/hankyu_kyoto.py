# ==========================================
# import
# ==========================================

from datetime import datetime, timezone, timedelta

import jpholiday

import config
import common



# ==========================================
# JST
# ==========================================

JST = timezone(
    timedelta(hours=9)
)



# ==========================================
# 運用設定
# ==========================================

OPERATIONS = {

    # ======================================
    # 平日ダイヤ
    # ======================================

    "weekday": {


        "平日朝急行": {

            682: "朝急行1 天神5:36→梅田6:10",

            810: "朝急行2 天神5:52→梅田6:24→特急運用",

            737: "朝急行3 河原町5:46→梅田6:36",

        },


        "平日朝準特急": {

            242: "準特急1 河原町6:00→梅田6:44",

            245: "準特急2 河原町7:04→梅田7:55・梅田8:02→河原町8:55",

            735: "準特急3 梅田6:14→河原町7:00",

            246: "準特急4 梅田6:48→河原町7:33",

        },


        "平日朝特急": {

            802: "特急A 桂-桂",

            810: "特急B 桂-正雀③",

        },


        "平日淡路行き": {

            815: "8R 北千里22:07→淡路22:25",

            230: "7R 北千里20:49→淡路21:08",

            232: "7R 北千里21:52→淡路21:11",

        },


        "平日長岡天神行き": {

            991: "河原町21:56-22:15長岡天神",

        },


        "平日夜準特急": {

            737: "夜準特急1 梅田22:24→河原23:08",

            729: "夜準特急2 梅田22:36→河原23:20",

            817: "夜準特急3 梅田22:48→河原23:32",

            248: "夜準特急4 梅田23:00→河原23:44",

            253: "夜準特急5 河原22:17→梅田23:02",

            244: "夜準特急6 河原22:30→梅田23:17",

            813: "夜準特急7 河原22:44→梅田23:32",

        },


        "平日夜急行": {

            253: "夜急行1 梅田23:15→河原24:04",

            244: "夜急行2 梅田23:30→河原24:19",

            813: "夜急行3 梅田23:45→河原24:34",

        },

    },


    # ======================================
    # 土休日ダイヤ
    # ======================================

    "holiday": {


        # 後で土休日運用を追加


    },

}
# ==========================================
# 色設定
# ==========================================

COLORS = {

    "平日朝急行": 16776960,

    "平日朝準特急": 16711680,

    "平日朝特急": 16711680,

    "平日淡路行き": 3447003,

    "平日長岡天神行き": 3447003,

    "平日夜準特急": 16711680,

    "平日夜急行": 16776960,

}



# ==========================================
# ダイヤ判定
# ==========================================

def get_day_type(now):

    if (
        now.weekday() >= 5
        or jpholiday.is_holiday(
            now.date()
        )
    ):

        return "holiday"

    else:

        return "weekday"



def get_day_id(day_type):

    return config.DAY_ID[
        day_type
    ]



# ==========================================
# 運用番号辞書作成
# ==========================================

def create_unyou_dict(data):

    unyou_dict = {}

    for item in data:

        if "unyou_id" in item:

            unyou_dict[
                item["unyou_id"]
            ] = item


    print(unyou_dict.keys())
    return unyou_dict



# ==========================================
# 車両取得
# ==========================================

def get_vehicle_number(data):

    if not data:

        return "登録なし"


    for key in [

        "vehicle",

        "vehicle_no",

        "car_no",

        "car_number",

        "sharyo"

    ]:

        if key in data:

            return str(
                data[key]
            )


    return "登録なし"


# ==========================================
# Embed作成
# ==========================================

def create_embed(
    category,
    operations,
    unyou_dict
):

    fields = []

    for unyou_id, memo in operations.items():

        group = unyou_dict.get(
            unyou_id
        )

        if group is None:

            vehicle = "登録なし"
            bikou_text = "なし"

        else:

            vehicle = (

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
        print(group)
        print(unyou_id, type(unyou_id))


        fields.append(

            {

                "name": f"運用 {unyou_id}",

                "value": (

                    f"車両：{vehicle}\n"

                    f"備考：{bikou_text}\n"

                    f"メモ：{memo}"

                ),

                "inline": False

            }

        )


    if not fields:

        return None


    now = datetime.now(JST)


    return {

        "title": category,

        "description": (

            f"{now.strftime('%Y年%m月%d日 %H時%M分')}取得"

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

def get_operations(
    target_categories
):


    api_params = config.API_PARAMS[
        "hankyu_kyoto"
    ]


    now = datetime.now(JST)


    day_type = get_day_type(
        now
    )


    print(
        f"ダイヤ種別: {day_type}"
    )


    day_id = get_day_id(
        day_type
    )


    params = {

        "rosen_code":

            api_params["rosen_code"],


        "day_id":

            day_id,


        "select_date":

            now.strftime(
                "%Y-%m-%d"
            ),


        "edit_mode":

            "false",


        "selected_shotei_index":

            -1,


        "route_id":

            api_params["route_id"],

    }



    data = common.get_unyou(

        config.API_URL,

        params

    )
    print(data["unyou_table"][0])
    print(len(data))
    print(type(data))
    print(data.keys())
    for key, value in data.items():
        print(key, type(value))


    unyou_dict = create_unyou_dict(
    data["unyou_table"]
    )


    embeds = []



    for category in target_categories:


        operations = OPERATIONS.get(

            day_type,

            {}

        ).get(

            category,

            {}

        )


        if not operations:

            continue



        embed = create_embed(

            category,

            operations,

            unyou_dict

        )


        if embed:

            embeds.append(
                embed
            )


    return embeds
