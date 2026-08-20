# ==========================================
# import
# ==========================================

from datetime import datetime, timezone, timedelta

import config
import common

from routes import hankyu_kyoto


# ==========================================
# JST
# ==========================================

JST = timezone(
    timedelta(hours=9)
)


# ==========================================
# 時間別対象カテゴリ
# ==========================================

def get_target_categories():

    now = datetime.now(JST)


    if now.hour == 6:

        return [
            "平日朝急行",
            "平日朝準特急",
        ]


    elif now.hour == 9:

        return [
            "平日特急",
        ]


    elif now.hour == 17:

        return [
            "平日淡路行き",
            "平日長岡天神行き",
        ]


    elif now.hour == 18:

        return [
            "平日夜急行",
            "平日夜準特急",
        ]


    else:

        return []



# ==========================================
# 路線取得
# ==========================================

def get_route_data(
    route,
    target_categories
):

    if route == "hankyu_kyoto":

        return hankyu_kyoto.get_operations(
            target_categories
        )

    return []



# ==========================================
# 実行
# ==========================================

def main():

    print("===================================")
    print("運用情報取得開始")
    print("===================================")


    target_categories = get_target_categories()


    if not target_categories:

        print("対象時間外")

        return



    print(
        f"取得対象: {target_categories}"
    )



    for route in config.ROUTES:

        print(
            f"{route} 取得開始"
        )


        embeds = get_route_data(
            route,
            target_categories
        )


        if not embeds:

            print(
                f"{route} 対象データなし"
            )

            continue



        webhook = config.WEBHOOKS.get(
            route
        )


        common.send_discord(
            webhook,
            embeds
        )


        print(
            f"{route} Discord送信完了"
        )


    print("===================================")
    print("運用情報取得終了")
    print("===================================")



# ==========================================
# 起動
# ==========================================

if __name__ == "__main__":

    main()
