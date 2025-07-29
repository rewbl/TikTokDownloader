
import asyncio
from typing import Dict, Set
from datetime import datetime

from DouyinEndpoints.Posts.UserPostVideos import UserPostVideos
from NotionServices.douyin_account_service import NotionDouyinAccountService
from PostMonitor.SingleUserNewPostMonitor import SingleUserNewPostMonitor


class NotionDouyinPostMonitor:

    def __init__(self):
        self.account_service = NotionDouyinAccountService()
        self.monitors: Dict[str, SingleUserNewPostMonitor] = {}  # sec_uid -> monitor
        self.monitor_tasks: Dict[str, asyncio.Task] = {}  # sec_uid -> task
        self.account_refresh_interval = 60  # 每分钟刷新一次账号列表
        self.is_running = False
    
    async def start(self):
        if self.is_running:
            return

        self.is_running = True
        asyncio.create_task(self._refresh_accounts_loop())

    async def _refresh_accounts_loop(self):
        while self.is_running:
            try:
                await self._refresh_accounts()
                await asyncio.sleep(self.account_refresh_interval)
            except Exception as e:
                print(f"刷新账号列表时发生错误: {e}")
                await asyncio.sleep(10)  # 出错时等待10秒再重试
    
    async def _refresh_accounts(self):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 刷新账号列表...")
        
        current_accounts = self.account_service.get_monitor_accounts()
        current_sec_uids = {account['sec_uid'] for account in current_accounts}
        
        monitoring_sec_uids = set(self.monitors.keys())
        
        to_add = current_sec_uids - monitoring_sec_uids
        for account in current_accounts:
            if account['sec_uid'] in to_add:
                await self._add_monitor(account)

        to_remove = monitoring_sec_uids - current_sec_uids
        for sec_uid in to_remove:
            await self._remove_monitor(sec_uid)
        
        if to_add or to_remove:
            print(f"账号列表更新完成: 新增 {len(to_add)} 个，移除 {len(to_remove)} 个")
            print(f"当前监控账号数量: {len(self.monitors)}")
        else:
            print(f"账号列表无变化，当前监控 {len(self.monitors)} 个账号")
    
    async def _add_monitor(self, account: Dict[str, str]):
        sec_uid = account['sec_uid']
        name = account['name']
        page_id = account['page_id']
        
        try:
            user_videos = UserPostVideos(name, sec_uid)
            
            monitor = SingleUserNewPostMonitor(user_videos, page_id)
            
            # 启动监控任务
            task = asyncio.create_task(monitor.check_forever())
            
            # 保存监控器和任务
            self.monitors[sec_uid] = monitor
            self.monitor_tasks[sec_uid] = task
            
            print(f"已添加账号监控: {name} ({sec_uid})")
            
            # 稍微延迟避免同时启动太多任务
            await asyncio.sleep(0.1)
            
        except Exception as e:
            print(f"添加账号监控失败 {name}: {e}")
    
    async def _remove_monitor(self, sec_uid: str):
        """
        移除账号监控
        
        Args:
            sec_uid: 账号的SecUid
        """
        try:
            # 获取监控器信息
            monitor = self.monitors.get(sec_uid)
            task = self.monitor_tasks.get(sec_uid)
            
            if monitor and task:
                name = monitor.user.name
                
                # 取消任务
                task.cancel()
                
                # 等待任务完成
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                
                # 移除监控器和任务
                del self.monitors[sec_uid]
                del self.monitor_tasks[sec_uid]
                
                print(f"已移除账号监控: {name} ({sec_uid})")
            
        except Exception as e:
            print(f"移除账号监控失败 {sec_uid}: {e}")
    
    async def run_forever(self):
        """运行监控器直到手动停止"""
        await self.start()
        
        try:
            while self.is_running:
                await asyncio.sleep(60)
        except KeyboardInterrupt:
            print("收到停止信号...")
        finally:
            await self.stop()
