# ==========================================
# import
# ==========================================

import config
import common

from routes import hankyu_kyoto


# ==========================================
# 路線処理
# ==========================================

def run_route(route_name):

    if route_name == "hankyu_kyoto":

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

        embeds = run_route(route)


        if embeds:

            common.send_discord(
                config.WEBHOOKS[route],
                embeds
            )


        print(f"{route} 送信完了")


    print("===================================")
    print("運用情報取得終了")
    print("===================================")


# ==========================================
# 起動
# ==========================================

if __name__ == "__main__":

    main()
