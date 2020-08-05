
import hashlib
import six
import redis

class MultipleHash(object):
    '''根据提供的原始数据，和预定义的多个salt,生成多个hash函数值'''
    def __init__(self,salts,hash_func_name="md5"):
        self.hash_func = getattr(hashlib,hash_func_name)
        self.salts = salts
        if len(self.salts)<3:
            raise Exception("请输入3个以上的salts值")

    def get_hash_values(self,data):
        '''根据提供的原始数据，返回多个hash函数值'''
        hash_values = []
        for i in self.salts:
            hash_obj = self.hash_func()
            hash_obj.update(self._safe_data(data))
            hash_obj.update(self._safe_data(i))
            ret = hash_obj.hexdigest()
            hash_values.append(int(ret,16))
        return hash_values


    def _safe_data(self,data):
        ''''''
        if six.PY3:
            if isinstance(data,bytes):
                return data
            elif isinstance(data,str):
                return data.encode()
            else:
                raise Exception("请提供一个字符串1")
        else:
            if isinstance(data,str):
                return data
            elif isinstance(data,unicode):
                return data.encode()
            else:
                raise Exception("请提供一个字符串2")

class BloomFilter(object):

    def __init__(self,salts,redis_host="localhost",redis_port=6379,redis_db = 0,redis_key = "bloomfilter"):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.redis_key = redis_key
        self.client = self._get_redis_client()
        self.multiple_hash = MultipleHash(salts)

    def _get_redis_client(self):
        pool = redis.ConnectionPool(host=self.redis_host, port=self.redis_port, db=self.redis_db)
        client = redis.StrictRedis(connection_pool=pool)
        return client


    def save(self,data):
        '''将原始数据在hash表中一一映射
        返回对应的偏移量'''

        hash_values = self.multiple_hash.get_hash_values(data)
        offsets = []
        for hash_value in hash_values:
            offset  =self._get_offset(hash_value)
            offsets.append(offset)
            self.client.setbit(self.redis_key,offset,1)
        return offsets



    def is_exists(self,data):
        ''''''
        hash_values = self.multiple_hash.get_hash_values(data)
        bit_values = []
        for hash_value in hash_values:
            offset = self._get_offset(hash_value)
            v = self.client.getbit(self.redis_key,offset)
            if v == 0 :
                return False

        return True


    def _get_offset(self, hash_value):
        #哈希表的长度  如果在同一项目中不能更改
        return hash_value % (2 ** 8 * 2 ** 20 * 2 * 3)


if __name__ == "__main__":
    # mh  = MultipleHash(['1','2','3'])
    # print(mh.get_hash_values("dsadhaskdhak"))
    data = ["asd","123","123","456","asd"]
    bm  = BloomFilter(salts=['1','2','3','4'])
    for d in data:
        if not bm.is_exists(d):
            bm.save(d)
            print("映射数据成功",d)
        else:
            print("发现重复数据",d)