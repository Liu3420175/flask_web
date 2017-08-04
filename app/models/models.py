from .base import MyBaseModel,TicketLeftBase,MyQuery
from app import db
from flask_login import UserMixin
from .. import login_manager
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import os
from time import time

from datetime import datetime
from pypinyin import lazy_pinyin

class TravelAgent(MyBaseModel):

    __tablename__ = 'travel_agent'

    name = db.Column(db.String(80))
    country_id = db.Column(db.Integer, db.ForeignKey("country.id"))
    commission_rate = db.Column(db.Float)
    other_user = db.relationship("OtherUser",backref="travel_agent",lazy='dynamic')
    order = db.relationship('Order', backref='travel_agent', lazy='dynamic')

    def __init__(self, name="",
                 commission_rate=0.0,
                 country_id=None
                 ):
        self.name = name
        self.commission_rate = commission_rate
        self.country_id = country_id
        self.create_time = datetime.now()


    def __repr__(self):
        return '<TravelAgent Name: %r' % self.name


class Country(MyBaseModel):
    """
    国家
    """
    __tablename__ = "country"
    name_zh = db.Column(db.String(20))
    name_en = db.Column(db.String(50))#"国家(英文)",
    short_name = db.Column(db.String(20))#"英文简称",
    area = db.Column(db.String(20))#"所属地区",
    supplier = db.relationship("Supplier",backref="country",lazy='dynamic')
    travel_agent = db.relationship("TravelAgent",backref="country",lazy='dynamic')
    city = db.relationship("City",backref="country",lazy='dynamic')

    def __init__(self,name_zh=None,
                 name_en=None,
                 short_name=None,
                 area=None
                 ):
        self.name_zh = name_zh
        self.name_en = name_en
        self.short_name = short_name
        self.area = area
        self.create_time = datetime.now()

    def __repr__(self):
        return "Country:%r"%self.name_zh



class Supplier(MyBaseModel):

    __tablename__ = 'supplier'
    name = db.Column(db.String(80), unique=True)
    country_id = db.Column(db.Integer, db.ForeignKey("country.id"))
    route = db.relationship("Route",backref="supplier",lazy='dynamic')

    def __init__(self,
                 name="",
                 country_id=None
                 ):
        self.name = name
        self.country_id = country_id
        self.create_time = datetime.now()


    def __repr__(self):
        return '<Supplier Name: %r>' % self.name


class OwnUser(UserMixin, MyBaseModel):

    __tablename__ = 'own_user'

    user_name = db.Column(db.String(80))
    open_id = db.Column(db.String(80))
    wx_nickname = db.Column(db.String(30))
    wx_img = db.Column(db.String(150))
    user_password = db.Column(db.String(128))
    user_gender = db.Column(db.String(20))
    contact_email = db.Column(db.String(120))
    contact_name = db.Column(db.String(80))
    contact_phone = db.Column(db.String(20))
    contact_id = db.Column(db.String(30))
    is_superuser = db.Column(db.Boolean, default=False)
    login_time = db.Column(db.DateTime)

    def __init__(self, user_name="ABC{0}".format(str(time())),
                 user_password="123456",
                 user_gender="",
                 contact_email="",
                 contact_name="",
                 contact_phone="",
                 contact_id="",
                 is_superuser=False,
                 open_id="",
                 wx_nickname="",
                 wx_img=""
                 ):
        now = datetime.now()
        self.create_time = now
        self.login_time = now

        self.user_name = user_name
        self.user_password = generate_password_hash(
        user_password) if user_password else None
        self.user_gender = user_gender
        self.contact_email = contact_email
        self.contact_name = contact_name
        self.contact_phone = contact_phone
        self.contact_id = contact_id

        self.open_id = open_id
        self.is_superuser = is_superuser
        self.wx_nickname = wx_nickname
        self.wx_img = wx_img

    def __repr__(self):
        return '<OwnUser Id: %r>' % self.id

    def get_id(self):
        """
        返回一个能唯一识别用户的，并能用于从 user_loader 回调中 加载用户的 unicode 。
        注意着 必须 是一个 unicode ——如果 ID 原本是 一个 int 或其它类型，你需要把它转换为
         unicode 。
        :return: 
        """
        return str(self.id)

    def verify_password(self, password):
        """
        验证密码
        :param password: 
        :return: 
        """
        return check_password_hash(self.user_password, password)

    @property
    def user_comment(self):
        all_comments = RouteComment.query.filter_by(id=self.user_id)
        return [one.get_order_info for one in all_comments]


@login_manager.user_loader
def load_user(userid):
    return OwnUser.query.get(int(userid))

class OtherUser(MyBaseModel):

    __tablename__ = "other_user"

    user_gender = db.Column( db.String(20))
    contact_email = db.Column( db.String(120))
    contact_name = db.Column( db.String(80))
    contact_phone = db.Column( db.String(20))
    contact_id = db.Column( db.String(30))
    agent_id = db.Column(db.Integer, db.ForeignKey("travel_agent.id"))

    def __init__(self,
                 user_gender="1",
                 contact_email="",
                 contact_name="",
                 contact_phone="",
                 contact_id="",
                 agent_id="",
                 ):
        self.user_gender = user_gender
        self.contact_email = contact_email
        self.contact_name = contact_name
        self.contact_phone = contact_phone
        self.contact_id = contact_id
        self.agent_id = agent_id
        self.create_time = datetime.now()

    def __repr__(self):
        return "<OtherUser ID:%r>"%self.id



class Order(MyBaseModel):

    __tablename__ = 'order'


    own_id = db.Column(db.Integer,nullable=False)
    other_id = db.Column(db.Integer, nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('travel_agent.id'))
    order_status = db.Column(db.String(20))
    number = db.Column(db.Integer),
    ticket_pdf = db.Column(db.String(120))
    order_id_agent = db.Column(db.String(50), unique=True)
    order_id_supplier = db.Column(db.String(50))
    pay_state = db.Column(db.String(10))
    route_id = db.Column(db.Integer)
    is_reviewed = db.Column(db.Boolean, default=False)
    total_price = db.Column(db.Numeric(4))
    departure_date = db.Column(db.String(30))
    ticket_sold = db.relationship('TicketSold', backref='order', lazy='dynamic')


    def __init__(self,
                 agent_id=None,
                 order_status="",
                 number=0,
                 pay_state="",
                 own_id=0,
                 other_id=0,
                 order_id_agent="",
                 ticket_pdf="",
                 order_id_supplier="",
                 route_id="",
                 is_reviewed="",
                 total_price="",
                 departure_date=""
                 ):
        if not own_id and not other_id:
            #两者至少有一个不能为0
            raise TypeError("`order`.own_id and `order`.other_id can not be null at the same time")
        elif own_id and not other_id:
            self.own_id = own_id
            self.other_id = 0
        elif not own_id and other_id:
            self.own_id = 0
            self.other_id = other_id
        else:
            raise TypeError("`order`.own_id and `order`.other_id can not be  non-null  at the same time")


        self.agent_id = agent_id
        self.order_status = order_status
        self.number = number
        self.create_time = datetime.now()
        self.ticket_pdf = ticket_pdf
        self.order_id_agent = order_id_agent
        self.order_id_supplier = order_id_supplier
        self.pay_state = pay_state
        self.total_price = total_price
        self.route_id = route_id
        self.is_reviewed = is_reviewed
        self.departure_date = departure_date

    def __repr__(self):
        return '<Order Id: %r>' % self.id

    @property
    def user(self):
        """
        获取订单的用户
        :return: 
        """
        if self.own_id:
            user = OwnUser.query.get(self.own_id)
        else:
            user = OtherUser.query.get(self.other_id)
        return user

    @property
    def get_ticket_info_by_order(self):

        tmp = {}
        ticketsold = TicketSold.query.filter_by(order_id=self.id).first()
        if ticketsold:

            ride_date = self.departure_date

            ticket_line_info = ticketsold.ticket_line_info
            if ticket_line_info["detail"]:
                from_city_info = ticket_line_info["detail"][0]
                to_city_info = ticket_line_info["detail"][-1]
                tmp["from_city_chinese"] = from_city_info["city_chinese"]
                tmp["from_city_en"] = from_city_info["city_en"]
                tmp["from_loc_name_chinese"] = from_city_info["loc_name_chinese"]
                tmp["from_loc_name_en"] = from_city_info["loc_name_en"]
                tmp["to_city_chinese"] = to_city_info["city_chinese"]
                tmp["to_city_en"] = to_city_info["city_en"]
                tmp["to_loc_name_chinese"] = to_city_info["loc_name_chinese"]
                tmp["to_loc_name_en"] = to_city_info["loc_name_en"]

                tmp["departure_time"] = ride_date

                tmp["create_time"] = self.create_time.strftime("%Y-%m-%d %H:%M:%S")
                arrive_time = (to_city_info['time'] - from_city_info['time']) / 3600
                tmp["arrive_time"] = round(arrive_time,1)
                tmp["number"] = self.number
                tmp["order_status"] = self.order_status
                tmp["pay_state"] = self.pay_state
                tmp["order_id_agent"] = self.order_id_agent
                tmp["route_id"] = self.route_id
                tmp["is_reviewed"] = self.is_reviewed

        return tmp

class Passenger(MyBaseModel):

    __tablename__ = 'passenger'

    own_id = db.Column(db.Integer, nullable=False)
    other_id = db.Column(db.Integer, nullable=False)
    passenger_name = db.Column(db.String(80))
    passport_id = db.Column(db.String(20))
    passenger_phone = db.Column(db.String(20))
    passenger_name_en = db.Column(db.String(80))
    passenger_gender = db.Column(db.String(20))
    due_date = db.Column(db.Date)
    ticket_sold = db.relationship('TicketSold', backref='passenger', lazy='dynamic')

    def __init__(self,
                 passenger_name="",
                 passport_id="",
                 own_id=0,
                 other_id=0,
                 passenger_phone="",
                 passenger_name_en=""
                 ):

        if not own_id and not other_id:
            # 两者至少有一个不能为0
            raise TypeError("`order`.own_id and `order`.other_id can not be null at the same time")
        elif own_id and not other_id:
            self.own_id = own_id
            self.other_id = 0
        elif not own_id and other_id:
            self.own_id = 0
            self.other_id = other_id
        else:
            raise TypeError("`order`.own_id and `order`.other_id can not be  non-null  at the same time")

        self.passenger_name = passenger_name
        self.passport_id = passport_id
        self.passenger_phone = passenger_phone

        self.create_time = datetime.now()
        if passenger_name:
            name_pinyin_list = lazy_pinyin(passenger_name)
            name_pinyin = "%s " % name_pinyin_list[0] + "".join(name_pinyin_list[1:])
            passenger_name_en = name_pinyin
        self.passenger_name_en = passenger_name_en

    def __repr__(self):
        return '<Passenger Name: %r>' % self.passenger_name

    @property
    def user(self):

        if self.own_id:
            user = OwnUser.query.get(self.own_id)
            types = "ABC"
            user_name = user.user_name if user else "未知"
        else:
            user = OtherUser.query.get(self.other_id)
            types = user.travel_agent.name if user and user.travel_agent else ""
            user_name = user.contact_name if user else ""
        return "{0}:{1}".format(types,user_name)


class Location(MyBaseModel):

    __tablename__ = 'location'

    loc_name_en = db.Column(db.String(200))
    loc_name_chinese = db.Column(db.String(80))
    city_en = db.Column(db.String(40))
    city_chinese = db.Column(db.String(40))
    city_code = db.Column(db.String(20))
    city_tel_code = db.Column(db.String(20))
    latitude = db.Column(db.String(20))
    longitude = db.Column(db.String(20))
    location_id_supplier = db.Column(db.String(20))
    route_node = db.relationship('RouteNode', backref='location', lazy='dynamic')

    def __init__(self,
                 loc_name_en='',
                 loc_name_chinese='',
                 city_en='',
                 city_chinese='',
                 city_code='',
                 city_tel_code='',
                 latitude='',
                 longitude='',
                 location_id_supplier=''
                 ):
        self.loc_name_en = loc_name_en
        self.loc_name_chinese = loc_name_chinese
        self.city_en = city_en
        self.city_chinese = city_chinese
        self.city_code = city_code
        self.city_tel_code = city_tel_code
        self.latitude = latitude
        self.longitude = longitude
        self.location_id_supplier = location_id_supplier
        self.create_time = datetime.now()

    def __repr__(self):
        return '<Location Name: %r>' % self.loc_name_en


class Operator(MyBaseModel):


    __tablename__ = 'operator'

    operator_name = db.Column(db.String(80))
    operator_phone = db.Column(db.String(50))
    operator_email = db.Column(db.String(120))
    operator_website = db.Column(db.String(100))
    operator_address = db.Column(db.String(120))
    terms_conditions = db.Column(db.Text)
    operator_logo = db.Column(db.String(100))
    route = db.relationship("Route",backref="operator",lazy='dynamic')

    def __init__(self,
                 operator_name='',
                 operator_phone='',
                 operator_email='',
                 operator_website='',
                 operator_address='',
                 terms_conditions='',
                 operator_logo=''
                 ):

        self.operator_name = operator_name
        self.operator_phone = operator_phone
        self.operator_email = operator_email
        self.operator_website = operator_website
        self.operator_address = operator_address
        self.terms_conditions = terms_conditions
        self.operator_logo = operator_logo
        self.create_time = datetime.now()

    def __repr__(self):
        return '<Operator Name: %r>' % self.operator_name


class Route(MyBaseModel):

    __tablename__ = 'route'

    route_id_supplier = db.Column(db.String(50))
    operator_id = db.Column(db.Integer, db.ForeignKey('operator.id'))
    is_selectable = db.Column(db.Boolean)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    line_id = db.Column(db.Integer, db.ForeignKey('line.id'))
    route_node = db.relationship('RouteNode', backref='route', lazy='dynamic')
    ticket_left_1 = db.relationship('TicketLeft1', backref='route', lazy='dynamic')
    route_data = db.relationship('RouteData', backref='route', lazy='dynamic')
    route_picture = db.relationship("RoutePicture", backref="route", lazy="dynamic")
    route_comment = db.relationship("RouteComment", backref="route", lazy="dynamic")

    def __init__(self,
                 route_id_supplier='',
                 operator_id='',
                 is_selectable='',
                 supplier_id='',
                 line_id=None
                 ):
        self.route_id_supplier = route_id_supplier
        self.operator_id = operator_id
        self.is_selectable = is_selectable
        self.supplier_id = supplier_id
        self.line_id = line_id
        self.create_time = datetime.now()

    def __repr__(self):
        return '<Route_Id: %r>' % self.id

    @property
    def route_pictures(self):

        pictures = Picture.query.join(RoutePicture,
                                      Picture.picture_id==RoutePicture.picture_id
                                      ).filter(
            RoutePicture.route_id==self.id).values("path")

        return [one[0].split("/")[-1] for one in pictures if one[0]]


    @property
    def route_score_avg(self):

        from sqlalchemy import func
        session = db.session
        avg_ = session.query(func.avg(RouteComment.score
                                      )).filter(
            RouteComment.route_id == self.route_id).scalar()
        try:
            avg = float(avg_)
        except:
            avg = 0.0
        return avg

    @property
    def route_node_detail(self):

        from app.tool import seconds_2_time
        data = { "detail": []}
        start_time = 0
        order = 0
        routenodes = RouteNode.query.filter_by(route_id=self.route_id
                                               ).order_by("node_id")

        for routenode in routenodes:

            order += 1
            time_int = routenode.time
            if order == 1:
                start_time = time_int
            tmp = {}
            loc_name_en, loc_name_chinese, city_en, city_chinese = routenode.route_node_name

            tmp["loc_name_en"] = loc_name_en
            tmp["loc_name_chinese"] = loc_name_chinese
            tmp["city_en"] = city_en
            tmp["city_chinese"] = city_chinese
            tmp["order"] = order
            tmp["node_id"] = routenode.id
            tmp["location_id"] = routenode.location_id

            tmp["time"] = time_int
            tmp["hour_minute_str"] = seconds_2_time(time_int)
            data["detail"].append(tmp)
        return data, start_time

    def route_ticket_info(self, date, rate_dict):
        """
        获取一条路线的票务信息
        """
        info = {}
        ticketleft = TicketLeft1.query.filter_by(route_id=self.route_id,
                                                date=date).first()
        if ticketleft:
            info = ticketleft.ticket_info(rate_dict)
        return info

class RouteData(MyBaseModel):


    __tablename__ = 'routedata'


    route_id = db.Column(db.Integer, db.ForeignKey('route.id'))
    vehicle_type = db.Column(db.String(50))
    total_seat = db.Column(db.Integer)
    pre_sale = db.Column(db.Integer)
    stop_sale = db.Column(db.Integer)
    mileage = db.Column(db.Integer)
    wifi = db.Column(db.Boolean)
    air_condition = db.Column(db.Boolean)
    water = db.Column(db.Boolean)
    power_plug = db.Column(db.Boolean)
    toilet = db.Column(db.Boolean)
    food_stop = db.Column(db.Boolean)


    def __init__(self,
                 route_id=None,
                 vehicle_type='',
                 total_seat=15,
                 pre_sale=30,
                 stop_sale=240,
                 mileage=100,
                 wifi=False,
                 air_condition=False,
                 water=False,
                 power_plug=False,
                 toilet=False,
                 food_stop=False
                 ):
        self.route_id = route_id
        self.vehicle_type = vehicle_type
        self.total_seat = total_seat
        self.pre_sale = pre_sale
        self.stop_sale = stop_sale
        self.mileage = mileage
        self.wifi = wifi
        self.air_condition = air_condition
        self.water = water
        self.power_plug = power_plug
        self.toilet = toilet
        self.food_stop = food_stop
        self.create_time = datetime.now()

    def __repr__(self):
        return '<Route_Data_Id: %r>' % self.id


class RouteNode(MyBaseModel):

    __tablename__ = 'routenode'


    route_id = db.Column(db.Integer, db.ForeignKey('route.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    time = db.Column(db.Integer)

    def __init__(self,
                 route_id=None,
                 location_id=None,
                 time=0):
        self.route_id = route_id
        self.location_id = location_id
        self.time = time
        self.create_time = datetime.now()

    def __repr__(self):
        return '<Node_Id: %r>' % self.id

    @property
    def route_node_name(self):

        location = Location.query.filter_by(id=self.location_id).first()
        if location:

            return location.loc_name_en, location.loc_name_chinese, location.city_en, location.city_chinese
        return "", "", "", ""




class TicketLeft1(TicketLeftBase):

    __tablename__ = 'ticket_left_1'

    currency_rate_id = db.Column(db.Integer, db.ForeignKey('currency_rate.id'))
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'))


    def __init__(self,
                 availability=15,
                 price_local=0,
                 currency_rate_id=1,
                 ticket_left_id_supplier='',
                 route_id=None,
                 date=None
                 ):
        self.availability = availability
        self.price_local = price_local
        self.currency_rate_id = currency_rate_id
        self.ticket_left_id_supplier = ticket_left_id_supplier
        self.route_id = route_id
        self.date = date

    def __repr__(self):
        return '<TicketLeft1 Id: %r>' % self.ticket_left_id

    def ticket_info(self, rate_dict):

        import math
        info = {}
        global Commission_rate
        if Commission_rate != -1:
            commission_rate = Commission_rate
        else:
            travelagent = TravelAgent.query.filter_by(travel_agent_name="ABC")
            Commission_rate = travelagent[0].commission_rate if travelagent else 0.0
            commission_rate = Commission_rate
        price = math.ceil(
                self.price_local * rate_dict[self.currency_rate_id] / (1 - commission_rate))

        info["price"] = price
        info["availability"] = self.availability
        info["ticket_left_id"] = self.ticket_left_id

        return info



class CurrencyRate(MyBaseModel):
    """
    """

    __tablename__ = "currency_rate"

    rate = db.Column( db.Numeric(4))
    name = db.Column(db.String(15))
    ticket_left_1 = db.relationship('TicketLeft1', backref='currency_rate', lazy='dynamic')

    def __init__(self,
                 rate=0.0,
                 name="",
                 from_currency_id=1,
                 to_currency_id=1
                 ):
        self.from_currency_id = from_currency_id
        self.to_currency_id = to_currency_id
        self.rate = rate
        self.name = name
        self.create_time = datetime.now()


    def __repr__(self):
        return '<Currency Name: %r>' % self.currency_rate_name


class TicketSold(MyBaseModel):
    __tablename__ = 'ticketsold'

    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    passenger_id = db.Column(db.Integer, db.ForeignKey('passenger.id'))
    price_RMB = db.Column(db.Numeric(4))
    ticket_left_id = db.Column(db.Integer)

    def __init__(self,
                 order_id=None,
                 passenger_id=None,
                 price_RMB=0.0,
                 ticket_left_id=0
                 ):
        self.order_id = order_id
        self.passenger_id = passenger_id
        self.price_RMB = price_RMB
        self.ticket_left_id = ticket_left_id
        self.create_time = datetime.now()

    def __repr__(self):
        return '<TicketSold ID: %r>' % self.id

    @property
    def ticket_line_info(self):


        data = {"node_order": None, "detail": []}
        route_id = self.order.route_id#TODO 这里用的是反向查询

        route = Route.query.get(route_id) if route_id else Route.query.filter(
            Route.id==route_id).first()
        if route:
            data = route.route_node_detail[0]
        return data

    @property
    def ticket_info(self):

        order = self.order
        create_time = self.create_time

        tmp = {}
        ticket_line_info = self.ticket_line_info
        if ticket_line_info["detail"]:
            from_city_info = ticket_line_info["detail"][0]
            to_city_info = ticket_line_info["detail"][-1]
            tmp["from_city_chinese"] = from_city_info["city_chinese"]
            tmp["from_city_en"] = from_city_info["city_en"]
            tmp["from_loc_name_chinese"] = from_city_info["loc_name_chinese"]
            tmp["from_loc_name_en"] = from_city_info["loc_name_en"]
            tmp["to_city_chinese"] = to_city_info["city_chinese"]
            tmp["to_city_en"] = to_city_info["city_en"]
            tmp["to_loc_name_chinese"] = to_city_info["loc_name_chinese"]
            tmp["to_loc_name_en"] = to_city_info["loc_name_en"]

            tmp["departure_time"] = order.departure_date

            tmp["create_time"] = create_time.strftime("%Y-%m-%d %H:%M:%S")
            arrive_time = (to_city_info['time'] - from_city_info['time']) / 3600
            tmp["arrive_time"] = round(arrive_time, 1)
            tmp["number"] = order.number
            tmp["order_status"] = order.order_status
            tmp["pay_state"] = order.pay_state
            tmp["order_id_agent"] = order.order_id_agent
        return tmp

class WXAccessToken(db.Model):
    """
    由于微信的有些接口调用需要access_tocken，而且access_token一天只能请求2000次，依次有效时间是两个小时，为了避免浪费请求次数，
    将获取的access_token值保存在数据库里，如果值过期再重新获取同时更新值，所以这张表里目前只有一条记录

    """
    __tablename__ = "wxaccesstoken"
    query_class = MyQuery

    token_id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(200))
    create_time = db.Column(db.DateTime)

    def __init__(self, access_token):
        self.access_token = access_token
        self.create_time = datetime.now()

    def __repr__(self):
        return '<TicketSold ID: %r>' % self.token_id


class City(MyBaseModel):

    __tablename__ = 'city'

    city_zh = db.Column(db.String(50), unique=True)
    city_en = db.Column(db.String(50), unique=True)
    city_pinyin = db.Column(db.String(60))
    country_id = db.Column(db.Integer,db.ForeignKey("country.id"))
    search_heat = db.Column(db.Integer)

    def __repr__(self):
        return "<City ID:%r>" % self.city_id

    def __init__(self,
                 city_zh='',
                 city_pinyin='',
                 city_en='',
                 country_id=None,
                 search_heat=0
                 ):
        self.city_en = city_en
        self.city_pinyin = city_pinyin
        self.city_zh = city_zh
        self.country_id = country_id
        self.search_heat = search_heat
        self.create_time = datetime.now()

    @property
    def locations(self):

        locations = Location.query.filter(Location.city_chinese == self.city_zh)
        location_ids = [str(one.location_id) for one in locations]
        return location_ids

    @property
    def route_ids(self):

        locations = Location.query.filter(Location.city_chinese == self.city_zh)
        location_ids = [one.location_id for one in locations]
        routenodes = RouteNode.query.filter(RouteNode.location_id.in_(location_ids)
                                            ).distinct().all()
        route_id = [str(one.route_id) for one in routenodes]

        return route_id


class RoutePicture(MyBaseModel):

    __tablename__ = "route_picture"

    route_id = db.Column(db.Integer, db.ForeignKey('route.id'))
    picture_id = db.Column(db.Integer)

    def __init__(self,
                 route_id=None,
                 picture_id=None
                 ):
        self.route_id = route_id
        self.picture_id = picture_id
        self.create_time = datetime.now()

    def __repr__(self):
        return "RoutePicture:{0}".format(self.id)


class Picture(MyBaseModel):

    __tablename__ = "picture"

    path = db.Column(db.String(100))
    path_supplier = db.Column(db.String(200))

    def __init__(self,
                 path='',
                 path_supplier=''
                 ):
        self.path = path
        self.path_supplier = path_supplier
        self.create_time = datetime.now()

    def __repr__(self):
        return "RoutePicture:{0}".format(self.id)


class RouteComment(MyBaseModel):

    __tablename__ = "route_comment"

    route_id = db.Column(db.Integer, db.ForeignKey('route.id'))
    user_id = db.Column(db.Integer)
    comment = db.Column(db.String(200))
    order_id = db.Column(db.Integer)
    score = db.Column(db.Float)
    path = db.Column(db.String(200))
    is_anonymous = db.Column(db.Boolean, default=False)

    def __init__(self,
                 route_id=None,
                 user_id=None,
                 order_id=None,
                 comment='',
                 score=1,
                 is_anonymous=False
                 ):
        self.route_id = route_id
        self.comment = comment
        self.score = score
        self.user_id = user_id
        self.is_anonymous = is_anonymous
        self.order_id = order_id
        self.create_time = datetime.now()

    def __repr__(self):
        return "RouteComment:{0}".format(self.id)

    @property
    def get_route_comment(self):

        user = OwnUser.query.get(self.user_id)
        tmp = {"nick_name":"匿名用户","img":""}
        if user:
            tmp["nick_name"] = user.wx_nickname
            tmp["img"] = user.wx_img
        tmp["score_str"] = str(self.score) if self.score else "0.0"
        tmp.update(self.__dict__)

        return tmp

    @property
    def get_order_info(self):

        tmp = {}
        ticketsold = TicketSold.query.filter_by(order_id=self.order_id).first()
        if ticketsold:
            ride_date = ticketsold.order.departure_date
            ticket_line_info = ticketsold.ticket_line_info
            if ticket_line_info["detail"]:
                from_city_info = ticket_line_info["detail"][0]
                to_city_info = ticket_line_info["detail"][-1]
                tmp["from_city_chinese"] = from_city_info["city_chinese"]

                tmp["to_city_chinese"] = to_city_info["city_chinese"]

                tmp["departure_time"] = ride_date
        tmp["score_str"] = str(self.score) if self.score else "0.0"
        tmp.update(self.__dict__)

        return tmp



class Line(MyBaseModel):

    __tablename__ = "line"

    origin_city_id = db.Column(db.Integer)
    destination_city_id = db.Column(db.Integer)
    search_heat = db.Column(db.Integer)

    route = db.relationship('Route', backref='line', lazy='dynamic')

    def __init__(self,
                 origin_city_id=None,
                 destination_city_id=None,
                 search_heat=0
                 ):
        self.origin_city_id = origin_city_id
        self.destination_city_id = destination_city_id
        self.search_heat = search_heat
        self.create_time = datetime.now()

    def __repr__(self):
        return "<Line ID:%r" % self.id


