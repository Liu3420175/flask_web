"""
工具
"""
def save(obj,session,**column):
    """
    保存/修改某个对象（是单个对象）某些字段的值
    :param obj: 
    :param session:
    :param column: 
    :return: 
    """

    if not obj:
       raise ValueError("对象不存在，无法保存")

    _dict = column
    # 对于某些空的字段，过滤掉，只保存非空字段的指
    _dict = dict(filter(lambda one: one[1] not in [None, ''], _dict.items()))

    for key,value in _dict.items():
        setattr(obj,key,value)
    session.add(obj)
    session.commit()

def create(model,session,**column):
    """
    创建一条记录
    :param model
    :param session: 
    :param column: 
    :return: 
    """

    obj = model(**column)
    session.add(obj)
    session.commit()
    print(obj)
    return obj


def insert(model,session,iterable=(),**column):
    """
    批量插入数据
    :param model: 
    :param session: 
    :param iterable
    :param column: 
    :return: 
    """
    _dict= column

    session.execute(model.__table__.insert(),
                    [{
                       key:_dict[key] for key in _dict
                    } for obj in iterable])
    session.commit()




def seconds_2_time(seconds):
    """
    将秒转换成"HH:MM"形式
    :param seconds: 
    :return: 
    """
    hour = seconds // 3600
    minute = int((seconds / 3600.0 - hour) * 60)
    minute_str = "{0}{1}".format(minute // 10,minute % 10)
    hour_str = "{0}".format(hour % 24 if hour % 24 else "00")

    return ":".join([hour_str,minute_str])


