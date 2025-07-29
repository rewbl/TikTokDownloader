
import asyncio
from typing import Dict, Set, List
from datetime import datetime

from notion_base import get_database

from DouyinEndpoints.Posts.UserPostVideos import UserPostVideos
from PostMonitor.DouyinPostPage import DouyinAccountPage
from PostMonitor.SingleUserNewPostMonitor import SingleUserNewPostMonitor


class NotionDouyinPostMonitor:

    def __init__(self):
        self.monitors: Dict[str, SingleUserNewPostMonitor] = {}  # sec_uid -> monitor
        self.monitor_tasks: Dict[str, asyncio.Task] = {}  # sec_uid -> task
        self.account_refresh_interval = 60  # 每分钟刷新一次账号列表
        self._add_monitor_semaphore = asyncio.Semaphore(10)  # 限制最大并发数为10

    async def start(self):
        asyncio.create_task(self._refresh_accounts_loop())

    async def _refresh_accounts_loop(self):
        while True:
            try:
                await self._refresh_accounts()
                await asyncio.sleep(self.account_refresh_interval)
            except Exception as e:
                print(f"刷新账号列表时发生错误: {e}")
                await asyncio.sleep(10)  # 出错时等待10秒再重试
    
    async def _refresh_accounts(self):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 刷新账号列表...")
        
        current_accounts = self.__get_monitor_accounts()
        current_sec_uids = {account['sec_uid'] for account in current_accounts}
        
        monitoring_sec_uids = set(self.monitors.keys())
        
        to_add = current_sec_uids - monitoring_sec_uids

        # 并行添加监控器，但限制最大并发数为10
        accounts_to_add = [account for account in current_accounts if account['sec_uid'] in to_add]
        if accounts_to_add:
            tasks = [self._add_monitor(account) for account in accounts_to_add]
            await asyncio.gather(*tasks)

        to_remove = monitoring_sec_uids - current_sec_uids
        for sec_uid in to_remove:
            await self._remove_monitor(sec_uid)
        
        if to_add or to_remove:
            print(f"账号列表更新完成: 新增 {len(to_add)} 个，移除 {len(to_remove)} 个")
            print(f"当前监控账号数量: {len(self.monitors)}")
        else:
            print(f"账号列表无变化，当前监控 {len(self.monitors)} 个账号")
    
    async def _add_monitor(self, account: Dict[str, str]):
        # 使用信号量控制并发数量
        async with self._add_monitor_semaphore:
            sec_uid = account['sec_uid']
            name = account['name']
            page_id = account['page_id']

            try:
                print(f"开始添加账号监控: {name} ({sec_uid})")
                user_videos = UserPostVideos(name, sec_uid)
                monitor = SingleUserNewPostMonitor(user_videos, page_id)
                task = asyncio.create_task(monitor.check_forever())
                self.monitors[sec_uid] = monitor
                self.monitor_tasks[sec_uid] = task
                print(f"✅ 已添加账号监控: {name} ({sec_uid})")
            except Exception as e:
                print(f"❌ 添加账号监控失败 {name}: {e}")
                import traceback
                traceback.print_exc()
    
    async def _remove_monitor(self, sec_uid: str):
        try:
            monitor = self.monitors.get(sec_uid)
            task = self.monitor_tasks.get(sec_uid)
            
            if monitor and task:
                name = monitor.user.name
                task.cancel()
                
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                
                del self.monitors[sec_uid]
                del self.monitor_tasks[sec_uid]
                print(f"已移除账号监控: {name} ({sec_uid})")
        except Exception as e:
            print(f"移除账号监控失败 {sec_uid}: {e}")
    
    def __get_monitor_accounts(self) -> List[Dict[str, str]]:

        try:
            results = (get_database(DouyinAccountPage.DATABASE_ID)
                      .where('Tags')
                      .contains('Monitor Posts')
                      .where('SecUid')
                      .is_not_empty()
                      .where('Name')
                      .is_not_empty()
                      .all())

            accounts = []
            for result in results:
                page_id = result.get('id') or result.get('page_id')
                accounts.append({
                    'page_id': page_id,
                    'name': result['Name'],
                    'sec_uid': result['SecUid']
                })

            return accounts

        except Exception as e:
            print(f"获取监控账号失败: {e}")
            return []