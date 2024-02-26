import motor.motor_asyncio


class PrivateApiResponse:
    category: str
    request_key: str
    request_properties: dict
    response_data: dict

    def __init__(self, category: str, request_key: str, request_properties: dict, response_data: dict):
        self.category = category
        self.request_key = request_key
        self.request_properties = request_properties
        self.response_data = response_data

    def to_document(self):
        return {
            "category": self.category,
            "request_key": self.request_key,
            "request_properties": self.request_properties,
            "response_data": self.response_data
        }


class MainDouyinMongoDb:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            'mongodb://192.168.196.85:27018,192.168.196.86:27018,192.168.196.87:27018/?replicaSet=tiktok')
        self.db = self.client['douyin']
        self.api_response = self.db['api_response']

    async def insert_api_response(self, private_api_response: PrivateApiResponse):
        await self.api_response.insert_one(private_api_response.to_document())
