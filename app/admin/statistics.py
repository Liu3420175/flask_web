"""
统计工具,图形化
"""

from sqlalchemy import func
from datetime import datetime,timedelta
import matplotlib.dates as mdates
from app.models import Order
from app import db
import matplotlib.pyplot as plt
import numpy as np
import mpld3
from mpld3 import plugins
import pandas as pd

session = db.session


def month_order_situation(start_month,end_month):
    """
    按月统计订单情况
    时间粒度：月
    返回结果:[(日期,数量),]
    
    :return: 
    """

    result = session.query(func.date_format(Order.create_time,"%Y-%m"),func.count("*")
                           ).filter(Order.create_time.between(start_month,end_month)
                                    ).group_by(func.date_format(Order.create_time,"%Y-%m")
                                               ).all()

    return result


def month_days_order_situation(start_time,end_time):
    """
    查看某个时间段１的订单趋势,默认是最近30天
    时间粒度:天
    
    :param start_time: 
    :param end_time: 
    :return: 
    """

    result = session.query(func.date_format(Order.create_time, "%Y-%m-%d"), func.count("*")
                           ).filter(Order.create_time.between(start_time, end_time)
                            ).group_by(func.date_format(Order.create_time, "%Y-%m-%d")
                                               ).all()
    result = dict(result)#对于有些日期没有的，要补充为0
    delta = (end_time - start_time).days
    between = map(lambda x,y:(x+timedelta(days=y)).strftime("%Y-%m-%d"),
                  [start_time]*delta,range(delta))
    res = [(one,result[one] if one in result else 0) for one in between ]

    return res



def create_order_fig(result,title,temporal=0):
    """
    绘图
    :param result: 
    :return: 
    """

    N = len(result)
    df = pd.DataFrame(index=range(N))

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
        x = [datetime.strptime(one[0],"%Y-%m-%d") for one in result]
    else:
        x = [datetime.strptime(one[0], "%Y-%m") for one in result]
    y = [one[1] for one in result]
    df['数量'] = y

    labels = []# TODO 设置标点样式
    for i in range(N):
        label = df.ix[[i], :].T
        label.columns = ['{0}'.format(x[i])]
        labels.append(str(label.to_html()))
    # 配置时间坐标
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())

    fig, ax = plt.subplots()
    points = ax.plot(x,y, '-or')#TODO　画折线图，实线，红色，标记标点

    plt.gcf().autofmt_xdate()

    interactive_legend = plugins.PointHTMLTooltip(points[0],labels,css=css)

    ax.set_xlabel('日期')
    ax.set_ylabel('订单数量')
    title = "{0}订单趋势".format(title)
    ax.set_title(title, size=20)
    plugins.connect(fig, interactive_legend)

    html_data = mpld3.fig_to_html(fig)
    return html_data


