"""
统计工具,图形化
"""

from sqlalchemy import func
from datetime import datetime,timedelta
import matplotlib.dates as mdates

from app import db
import matplotlib.pyplot as plt
import numpy as np
import mpld3
from mpld3 import plugins
import pandas as pd
import random
from .color import colors

session = db.session


def month_model_situation(Model,start_month,end_month):
    """
    按月统计某个模型新增情况
    时间粒度：月
    返回结果:[(日期,数量),]
    Model：某个模型,把需要类似统计功能的模型抽象出来，简化代码
    
    :return: 
    """

    result = session.query(func.date_format(Model.create_time,"%Y-%m"),func.count("*")
                           ).filter(Model.create_time.between(start_month,end_month)
                                    ).group_by(func.date_format(Model.create_time,"%Y-%m")
                                               ).all()

    return result


def month_days_model_situation(Model,start_time,end_time):
    """
    查看某个时间段某个模型新增趋势,默认是最近30天
    时间粒度:天
    :param Model
    :param start_time: 
    :param end_time: 
    :return: 
    """

    result = session.query(func.date_format(Model.create_time, "%Y-%m-%d"), func.count("*")
                           ).filter(Model.create_time.between(start_time, end_time)
                            ).group_by(func.date_format(Model.create_time, "%Y-%m-%d")
                                               ).all()
    result = dict(result)#对于有些日期没有的，要补充为0
    delta = (end_time - start_time).days
    between = map(lambda x,y:(x+timedelta(days=y)).strftime("%Y-%m-%d"),
                  [start_time]*delta,range(delta))
    res = [(one,result[one] if one in result else 0) for one in between ]

    return res


def month_active_model_situation(Model, start_month, end_month):
    """
    按月统计某个模型活跃情况
    时间粒度：月
    返回结果:[(日期,数量),]
    Model：某个模型,把需要类似统计功能的模型抽象出来，简化代码

    :return: 
    """

    result = session.query(func.date_format(Model.login_time, "%Y-%m"), func.count("*")
                           ).filter(Model.login_time.between(start_month, end_month)
                                    ).group_by(func.date_format(Model.login_time, "%Y-%m")
                                               ).all()

    return result


def month_days_active_model_situation(Model, start_time, end_time):
    """
    查看某个时间段某个模型活跃趋势,默认是最近30天
    时间粒度:天
    :param Model
    :param start_time: 
    :param end_time: 
    :return: 
    """

    result = session.query(func.date_format(Model.login_time, "%Y-%m-%d"), func.count("*")
                           ).filter(Model.login_time.between(start_time, end_time)
                                    ).group_by(func.date_format(Model.login_time, "%Y-%m-%d")
                                               ).all()
    result = dict(result)  # 对于有些日期没有的，要补充为0
    delta = (end_time - start_time).days
    between = map(lambda x, y: (x + timedelta(days=y)).strftime("%Y-%m-%d"),
                  [start_time] * delta, range(delta))
    res = [(one, result[one] if one in result else 0) for one in between]

    return res



def model_increase_fig(result,result1,title,temporal=0,_label=("订单趋势","出票趋势")):
    """
    绘图,将两个折线放在一个图里
    :param result: 
    :return: 
    """

    N = len(result)
    # TODO　这里要注意下，不能用df=df1=pd.DataFrame(index=range(N)),这样写他俩会指向同一对象
    df = pd.DataFrame(index=range(N))
    df1 = pd.DataFrame(index=range(N))

    css = """
    table
    {
      border-collapse: collapse;
    }
    th
    {
      color: #ffffff;
      background-color: #000000;
    }
    td
    {
      background-color: #cccccc;
    }
    table, th, td
    {
      font-family:Arial, Helvetica, sans-serif;
      border: 1px solid black;
      text-align: center;
    }
    """

    if temporal == 0:
        x = [datetime.strptime(one[0],"%Y-%m-%d").date() for one in result]
        x1 = [datetime.strptime(one[0],"%Y-%m-%d").date() for one in result1]

    else:
        x = [datetime.strptime(one[0], "%Y-%m").date() for one in result]
        x1 = [datetime.strptime(one[0], "%Y-%m") for one in result1]
    y = [one[1] for one in result]
    y1 = [one[1] for one in result1]
    df['数量'] = y
    df1['数量'] = y1

    labels = []# TODO 设置标点样式
    for i in range(N):
        label = df.ix[[i], :].T
        label.columns = ['{0}'.format(x[i])]
        labels.append(str(label.to_html()))
    labels1 = []
    for i in range(N):
        label1 = df1.ix[[i], :].T
        label1.columns = ['{0}'.format(x1[i])]
        labels1.append(str(label1.to_html()))

    # 配置时间坐标
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())

    fig, ax = plt.subplots()
    points = ax.plot(x,y, '-or',label=_label[0])#TODO　画折线图，实线，红色，标记标点
    points1 = ax.plot(x1,y1,'-ob',label=_label[1])
    plt.gcf().autofmt_xdate()
    plt.legend(loc='upper right')#制定图例标注

    interactive_legend = plugins.PointHTMLTooltip(points[0],labels,css=css)
    interactive_legend1 = plugins.PointHTMLTooltip(points1[0],labels1,css=css)
    ax.set_xlabel('日期')
    ax.set_ylabel('数量')
    title = "{0}数量趋势".format(title)
    ax.set_title(title, size=20)

    plugins.connect(fig, interactive_legend,interactive_legend1)
    #plugins.connect(fig,interactive_legend1)

    html_data = mpld3.fig_to_html(fig)
    return html_data


def month_user_from_situation(start_month, end_month, distributor, distributor1):
    """
           用户来源情况
           时间粒度：月
           返回结果:[(渠道,数量),]

           :return: 
           """
    from app.models import OwnUser
    result = session.query(OwnUser.distributor_id,
                           func.count("*")
                           ).filter(OwnUser.create_time.between(start_month, end_month)
                                    ).group_by(OwnUser.distributor_id
                                               ).all()

    result = [(distributor1[one[0]], one[1]) for one in result]
    res_dict = dict(result)
    distributor.update(res_dict)
    result = distributor.items()

    total = sum([one[1] for one in result])
    res = [(one[0], one[1] / total * 100) for one in result]
    return res


def create_active_user_fig(result, title, temporal=0):
    """
    新增用户来源分析
    :param result: 
    :param title: 
    :param temporal: 
    :return: 
    """
    # 调节图形大小，宽，高
    fig, ax = plt.subplots()

    plt.figure(figsize=(9, 9))
    # 定义饼状图的标签，标签是列表
    labels = [one[0] for one in result]
    # 每个标签占多大，会自动去算百分比
    sizes = [one[1] for one in result]
    color = random.sample(colors, len(result))
    # 将某部分爆炸出来， 使用括号，将第一块分割出来，数值的大小是分割出来的与其他两块的间隙
    # explode = (0.05, 0, 0)

    patches, l_text, p_text = ax.pie(sizes,
                                     labels=labels, colors=color,
                                     labeldistance=1.1, autopct='%3.1f%%', shadow=False,
                                     startangle=90, pctdistance=0.6)

    # labeldistance，文本的位置离远点有多远，1.1指1.1倍半径的位置
    # autopct，圆里面的文本格式，%3.1f%%表示小数有三位，整数有一位的浮点数
    # shadow，饼是否有阴影
    # startangle，起始角度，0，表示从0开始逆时针转，为第一块。一般选择从90度开始比较好看
    # pctdistance，百分比的text离圆心的距离
    # patches, l_texts, p_texts，为了得到饼图的返回值，p_texts饼图内部文本的，l_texts饼图外label的文本
    # 改变文本的大小
    # 方法是把每一个text遍历。调用set_size方法设置它的属性
    for t in l_text:
        t.set_size = (30)
    for t in p_text:
        t.set_size = (20)
    # 设置x，y轴刻度一致，这样饼图才能是圆的
    plt.axis('equal')
    title = "{0}用户来源分布".format(title)
    ax.set_title(title, size=20)
    html_data = mpld3.fig_to_html(fig)
    return html_data