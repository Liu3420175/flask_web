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



def sendEmail(_to=(),subject="ABC",file_path=("/home/abc/efd.pdf",)):
    """
    发送邮件
    :return: 
    """
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.application import MIMEApplication
    from collections import Iterable
    import os

    username = 'XXXXX@qq.com'
    password = 'XXXXXXXX'
    sender = username
    if isinstance(_to,Iterable) and not isinstance(_to,str) and _to:
        #判断其是不是可迭代对象,但不是字符串
        receivers = ','.join(_to)
    else:
        raise TypeError()

    # 如名字所示： Multipart就是多个部分
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receivers

    # 下面是文字部分
    puretext = MIMEText('Hello World')
    msg.attach(puretext)

    #发送附件
    if isinstance(file_path,(list,tuple)):
        for filename in file_path:
            if os.path.exists(filename):
                suffix_name = filename.split(".")[-1]#后缀名
                attachment = MIMEApplication(open(filename,"rb").read(),
                                             _subtype=suffix_name)
                attachment.add_header("Content-Disposition",
                                      "attachment",
                                      filename="abc.{0}".format(suffix_name))
                msg.attach(attachment)

    ##  下面开始真正的发送邮件了
    try:
        client = smtplib.SMTP()
        client.connect('https://mail.qq.com')
        client.login(username, password)
        client.sendmail(sender, receivers, msg.as_string())
        client.quit()
        print('邮件发送成功！')
    except Exception as e:
        print("发送失败,{0}".format(str(e)))