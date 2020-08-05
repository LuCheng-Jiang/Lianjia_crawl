


def get_filter_class(cls_name):

    if cls_name == "bloom":
        from .bloomfilter import BloomFilter
        return BloomFilter
    elif cls_name == "memory":
        from .information_summary_filter.memory_filter import MemoryFilter
        return MemoryFilter
    elif cls_name == "mysql":
        pass
    elif cls_name == "redis":
        from .information_summary_filter.redis_filter import RedisFilter
        return RedisFilter