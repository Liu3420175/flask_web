"""
自定义模板过滤器
"""

import app

@app.template_filter('dateformat')
def dateformat(date_obj,format="%Y-%m-%d"):
    """
    时间过滤器
    :param date: datetime对象
    :param format: 
    :return: 
    """
    from datetime import datetime,date
    if isinstance(date_obj,date) or isinstance(date_obj,datetime):
        return date_obj.striftime(format)
    else:
        return date_obj