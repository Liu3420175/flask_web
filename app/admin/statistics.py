"""
统计工具,图形化
"""

from sqlalchemy import func
from datetime import datetime,timedelta
import matplotlib.dates as mdates
from app.models import Order,TicketSold
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

def month_ticket_situation(start_month,end_month):
    """
    按月统计出票状况
    时间粒度:月
    返回结果:[(日期,数量),]
    :param start_month: 
    :param end_month: 
    :return: 
    """
    result = session.query(func.date_format(TicketSold.create_time,"%Y-%m"),
                           func.count("*")
                           ).filter(TicketSold.create_time.between(start_month,
                                                                   end_month)
                        ).group_by(func.date_format(TicketSold.create_time,"%Y-%m")
                                   ).all()
    return result

def month_days_ticket_situation(start_time,end_time):
    """
    查看某个时间段的出票趋势,默认是最近30天
    时间粒度:天
    :param start_time: 
    :param end_time: 
    :return: 
    """

    result = session.query(func.date_format(TicketSold.create_time,"%Y-%m-%d"),
                           func.count("*")
                           ).filter(TicketSold.create_time.between(start_time,
                                                              end_time)
                        ).group_by(func.date_format(TicketSold.create_time, "%Y-%m-%d")
                                               ).all()
    result = dict(result)  # 对于有些日期没有的，要补充为0
    delta = (end_time - start_time).days
    between = map(lambda x, y: (x + timedelta(days=y)).strftime("%Y-%m-%d"),
                  [start_time] * delta, range(delta))
    res = [(one, result[one] if one in result else 0) for one in between]

    return res




def create_order_fig(result,result1,title,temporal=0):
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
    print("res=",result,"res1=",result1)
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
    points = ax.plot(x,y, '-or',label="订单趋势")#TODO　画折线图，实线，红色，标记标点
    points1 = ax.plot(x1,y1,'-ob',label="出票趋势")
    plt.gcf().autofmt_xdate()
    plt.legend(loc='upper right')#制定图例标注

    interactive_legend = plugins.PointHTMLTooltip(points[0],labels,css=css)
    interactive_legend1 = plugins.PointHTMLTooltip(points1[0],labels1,css=css)
    ax.set_xlabel('日期')
    ax.set_ylabel('订单数量')
    title = "{0}订单趋势".format(title)
    ax.set_title(title, size=20)

    plugins.connect(fig, interactive_legend,interactive_legend1)
    #plugins.connect(fig,interactive_legend1)

    html_data = mpld3.fig_to_html(fig)
    return html_data