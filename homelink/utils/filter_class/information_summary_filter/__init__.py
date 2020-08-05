#基于信息摘要算法进行数据的去重判断和存储

import hashlib
import six

class  BaseFilter(object):
    '''基于信息摘要算法进行数据的去重判断和存储'''


    def __init__(self,hash_func_name="md5",redis_host='localhost',redis_port=6379,redis_db=0,redis_key="redis_filter"):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.redis_key = redis_key
        self.hash_func = getattr(hashlib,hash_func_name)
        self.storage = self._get_storage()



    def _get_storage(self):
        '''
        返回对应的一个存储对象
        @return:
        '''
        pass
    '''
    python2  str == python3  bytes
    python2 unicode = python3 str
    '''

    def _safe_data(self,data):
        ''''''
        if six.PY3:
            if isinstance(data,bytes):
                return data
            elif isinstance(data,str):
                return data.encode()
            else:
                raise Exception("请提供一个字符串")
        else:
            if isinstance(data,str):
                return data
            elif isinstance(data,unicode):
                return data.encode()
            else:
                raise Exception("请提供一个字符串")


    def _get_hash_value(self,data):
        '''根据给定的数据，返回信息摘要哈希值'''
        hash_obj = self.hash_func()
        hash_obj.update(self._safe_data(data))    #python3  bytes
        hash_value  = hash_obj.hexdigest()
        return hash_value


    def save(self,data):
        '''根据data计算出对应的指纹进行存储'''

        hash_value =  self._get_hash_value(data)
        return self._save(hash_value)


    def _save(self,hash_value):
        '''存储对应的hash值
        交给对应的子类去继承
        :return 存储的结果
        '''
        pass


    def is_exists(self,data):
        '''判断给定的数据的指纹是否存在'''
        hash_value  =self._get_hash_value(data)
        return self._is_exists(hash_value)


    def _is_exists(self,hash_value):
        '''
        判断对应的哈希值是否存在（交给对应的子类去继承）

        @param hash_value:
        @return:
        '''
        pass