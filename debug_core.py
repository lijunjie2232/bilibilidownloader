from bilibilicore.api import Season, User, Video

if __name__ == "__main__":
    user = User()
    result = user.nav_me()
    season = Season()
    result = season.get_view("BV1g1CKYUExu")

    pass
