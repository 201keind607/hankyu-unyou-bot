# ==========================================
# import
# ==========================================

import config
import common

from routes import hankyu_kyoto


# ==========================================
# 路線取得
# ==========================================

def get_route_data(route):

    if route == "hankyu_kyoto":

        return hankyu_kyoto.get_operations()

    return []


# ==========================================
# 実行
# ==========================================

def main():

    print("===================================")
    print("運用情報取得開始")
    print("===================================")


    for route in config.ROUTES:

        print(f"{route} 取得開始")


        embeds = get_route_data(route)


        if not embeds:

            print(f"{route} 対象データなし")
            continue


        webhook = config.WEBHOOKS.get(route)


        common.send_discord(
            webhook,
            embeds
        )


        print(f"{route} Discord送信完了")


    print("===================================")
    print("運用情報取得終了")
    print("===================================")


# ==========================================
# 起動
# ==========================================

if __name__ == "__main__":

    main()
