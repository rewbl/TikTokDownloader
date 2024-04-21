import motor.motor_asyncio


class MainDouyinMongoDb:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            'mongodb://app:Supers8*@192.168.196.83:27018,192.168.196.98:27018,192.168.196.85:27018,192.168.196.86:27018,192.168.196.87:27018/?replicaSet=tiktok')
        self.db = self.client['douyin']
        self.api_responses = self.db['api_responses']
        self.following_lists = self.db['following_lists']
        self.following_relations = self.db['following_relations']
        self.douyin_users = self.db['douyin_users']
        self.douyin_follow_list_candidates = self.db['douyin_users_follow_no_lists_view']
        self.douyin_follow_view = self.db['douyin_users_follow_view']



DouyinDb = MainDouyinMongoDb()