"""
定制Query,这样可以增加一些默认Query没有的操作数据库的API
"""
from flask_sqlalchemy import BaseQuery



def _column_2_tuple(_tuple, obj):
    """

    :param _tuple: 字段
    :param obj: 模型对象
    :return: 
    """
    return tuple([getattr(obj, field) for field in _tuple])

def _column_2_dict(_tuple,obj):
    """
    
    :param _tuple: 
    :param obj: 
    :return: 
    """
    return dict([(field,getattr(obj,field)) for field in _tuple])




class MyQuery(BaseQuery):
    def values_list(self, *column,to_dict=False):
        """
        讲集合某个字段的返回值以列表的形式展现
        :param column: 
        :return: 
        """
        _tuple = column
        if to_dict:
            return [_column_2_dict(_tuple,obj) for obj in self]
        if len(_tuple) == 1:
            field = _tuple[0]
            return [getattr(obj, field) for obj in self]
        elif len(_tuple) == 0:
            raise TypeError
        else:

            return [_column_2_tuple(_tuple, obj) for obj in self]





    def save(self,**column):
        """
        保存对象某些字段的值
        :param column: 
        :return: 
        """
        _dict = column
        #对于某些空的字段，过滤掉，只保存非空字段的指
        _dict = filter(lambda key: key not in [None,''],_dict)


