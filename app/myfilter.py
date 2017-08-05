"""
自定义模板过滤器
"""

import app

@app.template_filter('dateformat')
def dateformat(date,format="%Y-%m-%d"):
    """
    时间过滤器
    :param date: datetime对象
    :param format: 
    :return: 
    """

    return date.striftime(format)