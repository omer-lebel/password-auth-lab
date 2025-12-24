class TargetUserState:
    def __init__(self, username):
        self.username = username
        self.locked = False
        self.captcha_required = False
        self.hacked = False
        self.captcha_token = None
