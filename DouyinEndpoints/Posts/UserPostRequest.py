class UserPostRequest:
    sec_user_id: str

    def __init__(self, sec_user_id: str = None, name: str = None, max_cursor: str = None):
        self.sec_user_id = sec_user_id
        self.name = name
        self.max_cursor = max_cursor

    def fill_api_params(self, params, ts):
        params["sec_user_id"] = self.sec_user_id
        params["ts"] = str(ts)
        params["_rticket"] = str(ts * 1000)
        if self.max_cursor:
            params["max_cursor"] = self.max_cursor
