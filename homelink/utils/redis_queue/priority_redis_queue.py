
import pickle
from .base import BaseRedisQueue

class PriorityRedisQueue(BaseRedisQueue):
    """使用zset实现优先级队列"""


    def qsize(self):
        self.last_qsize = self.redis.zcard(self.name)
        return self.last_qsize

    def put_nowait(self, obj):
        """
        @param obj: (score,value)
        @return:
        """
        if self.lazy_limit and self.last_qsize < self.maxsize:
            pass
        elif self.full():
            raise self.Full
        mapping = {pickle.dumps(obj[1]):obj[0]}
        self.last_qsize = self.redis.zadd(self.name,mapping )
        return True

    def get_nowait(self):
        """
        -1,-1取权重最大的
        0，0 取权重最小的
        @return:
        """

        if self.use_lock is True:
            from 去重.old.new.request_manager.utils.redis_queue.redis_lock import RedisLock

            lock = RedisLock(**self.redis_lock_config)
            if self.lock is None:
                self.lock = RedisLock(**self.redis_lock_config)   #只用一把锁
            if lock.acquire_lock():
                ret = self.redis.zrange(self.name,-1,-1)
                print(pickle.loads(ret[0]))  #通过打印我们返回的是一个列表
                if not ret :
                    raise self.Empty
                self.redis.zrem(self.name,ret[0])
                lock.release_lock()
                return pickle.loads(ret[0])
        else:
            ret = self.redis.zrange(self.name, -1, -1)
            print(pickle.loads(ret[0]))  # 通过打印我们返回的是一个列表
            if not ret:
                raise self.Empty
            self.redis.zrem(self.name, ret[0])

            return pickle.loads(ret[0])