import redis
from . import BaseFilter

class RedisFilter(BaseFilter):
    '''基于python中的集合数据类型进行去重判断依据'''



    def _get_storage(self):

        pool = redis.ConnectionPool(host=self.redis_host,port=self.redis_port,db=self.redis_db)
        client = redis.StrictRedis(connection_pool=pool)
        return client

    def _save(self, hash_value):
        '''
        利用Redis的无序集合进行存储
        @param hash_value:
        @return:
        '''
        return self.storage.sadd(self.redis_key,hash_value)


    def _is_exists(self, hash_value):
        return self.storage.sismember(self.redis_key,hash_value)