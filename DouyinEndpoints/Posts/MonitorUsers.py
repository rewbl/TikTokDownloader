from typing import List, Tuple
from unittest import IsolatedAsyncioTestCase

import pandas as pd


class MonitorUsers:
    users: List[Tuple[str, str, str]]

    def __init__(self, path: str):
        df = pd.read_excel(path)
        df.columns = [col.strip() for col in df.columns]
        selected_df = df[df['Selected'] == 1]
        selected_df = selected_df.fillna('')
        self.users = list(selected_df[['Nickname', 'SecUid', 'Folder']].itertuples(index=False, name=None))


class TestMonitorUsers(IsolatedAsyncioTestCase):

    async def test_run(self):
        monitor = MonitorUsers('c:\\temp\\test\\DouyinUsers.xlsx')
        print(monitor.users)
