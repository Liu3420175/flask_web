from app import db
from .query import MyQuery


class MyBaseModel(db.Model):
    """
    自定义基类
    """
    __abstract__ = True  # 抽象类，不能实例化，其他的类都继承自它
    query_class = MyQuery  # 使用定制的Query

    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.DateTime)




class TicketLeftBase(db.Model):
    """
    自定义基类
    """
    __abstract__ = True  # 抽象类，不能实例化，其他的类都继承自它
    query_class = MyQuery  # 使用定制的Query

    ticket_left_id = db.Column(db.Integer, primary_key=True)
    availability = db.Column(db.Integer)
    price_local = db.Column(db.Float)
    #currency_rate_id = db.Column(db.Integer, db.ForeignKey('currency_rate.id'))
    ticket_left_id_supplier = db.Column(db.String(100))
    #route_id = db.Column(db.Integer, db.ForeignKey('route.id'))
    date = db.Column(db.Date)