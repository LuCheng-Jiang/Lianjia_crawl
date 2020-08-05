import redis
import pickle
import threading
import time

class RedisLock(object):


    def __init__(self,lock_name,host="localhost",port=6379,db =0):
        self.redis = redis.StrictRedis(host=host,port=port,db=db)
        self.lock_name = lock_name

    def acquire_lock(self,thread_id=None,expires=10,block=True):  #佳=加个阻塞操作
        """
        :param thread_id   表明每个线程的唯一标识，用来判断解锁
        @return:
        """
        #如果lock_name存在,ret = 0

        if thread_id is None:
            thread_id = self._get_thread_id()
        print(thread_id)

        while block:
            ret = self.redis.setnx(self.lock_name, pickle.dumps(thread_id))
            if ret==1:
                self.redis.expire(self.lock_name,expires)
                print("上锁成功")
                return True
            # else:
            #     print("上锁失败")
            #     return False
            time.sleep(1)

    def release_lock(self,thread_id=None):
        if thread_id is None:
            thread_id = self._get_thread_id()
        print(thread_id)
        ret  = self.redis.get(self.lock_name)

        if ret is not None or pickle.loads(ret) == thread_id: #确保解锁还是上锁人
            self.redis.delete(self.lock_name)
            print("解锁成功")
            return True
        else:
            print("解锁失败")
            return False

    def _get_thread_id(self):
        import socket
        # print(socket.gethostname())  # 获取服务器号
        import os
        # print(os.getpid()) #获取进程号
        # 维护单独的一个线程     “服务器号”+"进程号"
        thread_id = socket.gethostname()+str(os.getpid())+threading.current_thread().name

        return thread_id

if __name__ =="__main__":
    redis_lock = RedisLock("redis_lock2")

    # print(thread_id)
    if redis_lock.acquire_lock(expires=10):
       print("执行对应的操作")
       redis_lock.release_lock()