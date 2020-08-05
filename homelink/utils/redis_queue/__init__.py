

def get_redis_queue_cls(queue_type):

    if queue_type == "fifo":
        from 去重.old.new.request_manager.utils.redis_queue.fifo_redis_queue import  FifoRedisQueue
        return FifoRedisQueue
    elif queue_type == "lifo":
        from 去重.old.new.request_manager.utils.redis_queue.lifo_redis_queue import  LifoRedisQueue
        return LifoRedisQueue
    elif queue_type == "priority":
        from 去重.old.new.request_manager.utils.redis_queue.priority_redis_queue import  PriorityRedisQueue
        return PriorityRedisQueue
    else:
        raise Exception("只支持fifo,Lifo,priority三种类型的队列类型")

def get_redis_lock_cls():

    from 去重.old.new.request_manager.utils.redis_queue.redis_lock import  RedisLock
    return RedisLock