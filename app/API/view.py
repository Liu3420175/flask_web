from flask_restful import Resource,reqparse,request,fields,marshal_with
from flask_httpauth import HTTPBasicAuth
from flask import Response,jsonify,render_template
from sqlalchemy import desc,or_

from datetime import datetime
from pypinyin import lazy_pinyin
import requests
import random
from hashlib import md5
import json
from decimal import Decimal,getcontext

from time import time
from datetime import timedelta
from app import db
from .decorator import http_basic_auth
from app.exceptions import *

from app.models.serialization import *
from app.models import *
from app.tool import save,create

try:
    from lxml import etree
except ImportError:
    from xml.etree import cElementTree as etree
except ImportError:
    from xml.etree import ElementTree as etree

#解析参数get请求
get_parse = reqparse.RequestParser()
get_parse.add_argument("user_id",
                   type=int,#必须是int类型
                   action='append',#可以介绍多个值或者列表
                   help="user_id是必须参数",
                   default=0
                   )#必须参数,而且必须是int类型


get_parse.add_argument("user_name")#用户名，虽然用的很少

get_parse.add_argument("open_id")#微信open_id，用的也很少
get_parse.add_argument("order_id",
                        type=int,
                        default=0
                       )
get_parse.add_argument("code",
                       type=str)
get_parse.add_argument("location_id",
                       type=int,
                       default=0)

get_parse.add_argument("route_id",
                       type=int,
                       default=0)
get_parse.add_argument("page",
                       type=int,
                       default=1)

get_parse.add_argument("outbound_date",
                       type=str)

#post请求
post_parse = reqparse.RequestParser()
post_parse.add_argument("user_id",
                        type=int,#必须是int类型
                        help="user_id是必须参数"
                   )#必须参数,而且必须是int类型)
post_parse.add_argument("user_name",
                        type=str,
                        location='form'
                        )
post_parse.add_argument("open_id",
                        type=str,
                        location='form'
                        )
post_parse.add_argument("wx_nickname",
                        type=str,
                        location='form'
                        )
post_parse.add_argument("wx_img",
                        type=str,
                        location='form'
                        )
post_parse.add_argument("user_password",
                        type=str,
                        location='form'
                        )
post_parse.add_argument("user_gender",
                        type=str,
                        location='form'
                        )

post_parse.add_argument("contact_email",
                        type=str,
                        location='form'
                        )

post_parse.add_argument("contact_name",
                        type=str,
                        location='form'
                        )
post_parse.add_argument("contact_phone",
                        type=str,
                        location='form'
                        )

post_parse.add_argument("contact_phone",
                        type=str,
                        location='form'
                        )

post_parse.add_argument("contact_id",
                        type=str,
                        location='form'
                        )

post_parse.add_argument("contact_id",
                        type=str,
                        location='form'
                        )

post_parse.add_argument("is_superuser",
                        type=str,
                        location='form'
                        )

post_parse.add_argument("passenger_name",
                        type=str,
                        location="form"
                        )

post_parse.add_argument("passenger_id",
                        type=int,
                        location="form"
                        )
post_parse.add_argument("passenger_phone",
                        type=str,
                        location="form"
                        )

post_parse.add_argument("passenger_name_en",
                        type=str,
                        location="form"
                        )

post_parse.add_argument("passenger_gender",
                        type=str,
                        location="form"
                        )

post_parse.add_argument("due_date",
                        type=str,
                        location="form"
                        )

post_parse.add_argument("code",
                        type=str,
                        location="form")

post_parse.add_argument("out_trade_no",
                        type=str,
                        default="",
                        location="form"
                        )

post_parse.add_argument("total_fee",
                        type=int,
                        location="form")

post_parse.add_argument("pay_state",
                        type=str,
                        default="1",
                        location="form")

post_parse.add_argument("departure",
                        type=str,
                        default="曼谷",
                        location="form"
                        )

post_parse.add_argument("destination",
                        type=str,
                        default="普吉岛",
                        location="form")

post_parse.add_argument("passenger_ids",
                        type=str,
                        location="form")

post_parse.add_argument("ticket_left_id",
                        type=int,
                        location="form")

post_parse.add_argument("price_RMB",
                        type=float,
                        location="form")

post_parse.add_argument("order_id_agent",
                        type=str,
                        location="form"
                      )

post_parse.add_argument("route_id",
                        type=int,
                        location="form"
                        )

post_parse.add_argument("total_price",
                        type=float,
                        location="form"
                        )

post_parse.add_argument("comment",
                        type=str,
                        location='form')

post_parse.add_argument("score",
                        type=float,
                        default=5.0,
                        location='form')
post_parse.add_argument("is_anonymous",
                        type=bool,
                        default=0,
                        location="form")
post_parse.add_argument("outbound_date",
                        type=str,
                        location="form")

user_fields = {
    'user_name' : fields.String,#"用户名",
    'open_id' :fields.String,#"微信openId",
    'wx_nickname': fields.String,#"微信名",
    'wx_img':fields.String,#"微信头像地址",
    'user_password': fields.String,#"密码",
    'user_gender' : fields.String,#"性别",
    'contact_email':fields.String,#"联系人E-mail",
    'contact_name': fields.String,#"联系人姓名",
    'contact_phone': fields.String,#"联系人电话",
    'contact_id': fields.String,#"联系人的护照ID",
    'is_superuser' : fields.Boolean(default=False),#"是不是超级用户",

}


class SearchSchedulesApi(Resource):

    decorators = [http_basic_auth]

    def get(self):
        """
        
        :return: 
        """
        tomorrow = datetime.today() + timedelta(days=1)
        tomorrow_str = tomorrow.strftime("%Y-%m-%d")
        departure = request.args.get("departure", "").strip()  # 起始地点
        destination = request.args.get("destination", "").strip()  # 目的地
        outbound_date_str = request.args.get("outbound_date", tomorrow_str)  # 出发日期,默认为明天

        currency_rate_obj = CurrencyRate.query.all()
        rate_dict = {currencyrate.id: currencyrate.rate for currencyrate in currency_rate_obj}
        result = self._search_bus_schedules(departure,
                                            destination,
                                            outbound_date_str,
                                            rate_dict)

        return jsonify(result)

    def _search_bus_schedules(self,departure, destination, outbound_date_str, rate_dict):


        outbound_date = datetime.strptime(outbound_date_str, "%Y-%m-%d")
        result = {"error": 0,
                  "info": [],
                  "outbound_date": outbound_date_str,
                  "pre_outbound_date": (outbound_date - timedelta(days=1)
                                        ).strftime("%Y-%m-%d"),
                  "next_outbound_date": (outbound_date + timedelta(days=1)
                                         ).strftime("%Y-%m-%d"),
                  "departure": departure,
                  "destination": destination,
                  }
        info = []

        engin = db.engine
        route_sql = """select `ticket_left_1`.`route_id` from `ticket_left_1` join `routes` on `ticket_left_1`.`route_id`=`route`.`id` join `line` on `route`.`line_id`=`line`.`line_id`  where `ticket_left_1`.`date`='%s' and `line`.`line_id` in (select `line`.`line_id` from `line` where `line`.`origin_city_id` in (select  `city`.`city_id` from `city` where`city`.`city_zh`='%s') and `line`.`destination_city_id` in (select  `city`.`city_id` from `city` where`city`.`city_zh`='%s'))"""%(outbound_date_str,departure,destination)
        exe_route = engin.execute(route_sql)
        route_ids = [one["route_id"] for one in exe_route]

        routes = Route.query.filter(Route.id.in_(route_ids)
                                            ).filter_by(is_selectable=1).all()
        for route in routes:
            node_detail, start_time = route.route_node_detail_new

            ticket_info = route.route_ticket_info(outbound_date, rate_dict)
            tmp = {}
            tmp["route_id"] = route.route_id
            tmp["start_time"] = start_time
            tmp["node_detail"] = node_detail
            tmp["ticket_info"] = ticket_info
            info.append(tmp)
                    # 按时间进行排序
            info = sorted(info, key=lambda one: one["start_time"])  # 按出发时间进行排序
            result['info'] = info

        return result


class UserApi(Resource):
    decorators = [http_basic_auth,]#身份验证

    def get(self):

        args = get_parse.parse_args()
        user_id = args.get('user_id')
        user_name = args.get("user_name")
        open_id = args.get("open_id")
        schema = UserSchema()
        print("user_id",user_id,type(user_id))
        if isinstance(user_id,int) and user_id > 0:
            user = None
            if user_id:
                user = OwnUser.query.get(user_id)
            if user_name:
                user = OwnUser.query.filter(OwnUser.user_name==user_name).first()
            if open_id:
                user = OwnUser.query.filter(OwnUser.open_id==open_id).first()

            result = schema.dumps(user).data#序列化成json形式

        elif isinstance(user_id,list):
            users = OwnUser.query.filter(OwnUser.id.in_(user_id))
            result = schema.dumps(users,many=True).data

        else:
            page = args.get("page")
            users = OwnUser.query.order_by(OwnUser.id.asc()
                                           ).paginate(page, 10, False).items
            result = schema.dumps(users,many=True).data

        return Response(result)

    def __args(self,args):
        """
        辅助函数，解析form参数
        :return: 
        """

        user_name = args.get("user_name")
        open_id = args.get("open_id")
        wx_nickname = args.get("wx_nickname")
        wx_img = args.get("wx_img")
        user_password = args.get("user_password", "123456")
        user_gender = args.get("user_gender")  # "性别",
        contact_email = args.get("contact_email")  # "联系人E-mail",
        contact_name = args.get("contact_name")  # "联系人姓名",
        contact_phone = args.get("contact_phone")
        contact_id = args.get("contact_id")
        is_superuser = args.get("is_superuser", False)

        args_dict = dict(user_name=user_name,
                         open_id=open_id,
                         wx_nickname=wx_nickname,
                         wx_img=wx_img,
                         user_password=user_password,
                         user_gender=user_gender,
                         contact_name=contact_name,
                         contact_email=contact_email,
                         contact_phone=contact_phone,
                         contact_id=contact_id,
                         is_superuser=is_superuser, )
        return args_dict

    #@marshal_with(user_fields)
    def post(self):

        session = db.session
        status = msg= "OK"
        args = post_parse.parse_args()
        args_dict = self.__args(args)
        obj = create(OwnUser,session,**args_dict)
        desc = "创建成功"
        result = dict(status=status,msg=msg,desc=desc)
        return jsonify(result)


    #@marshal_with(user_fields)
    def put(self):

        from werkzeug.security import generate_password_hash
        session = db.session
        status = msg = "OK"
        args = post_parse.parse_args()
        user_id = args.get("user_id")

        args_dict = self.__args(args)
        user_password = args_dict.get("user_password")
        if user_password:
            user_password = generate_password_hash(user_password)
            args_dict.update({ "user_password":user_password})

        user_name = args_dict.pop("user_name")
        open_id = args_dict.pop("open_id")
        user = None
        if user_id:
            user = OwnUser.query.get(user_id)
        if user_name and not user:
            user = OwnUser.query.filter(OwnUser.user_name == user_name).first()
        if open_id and not user:
            user = OwnUser.query.filter(OwnUser.open_id == open_id).first()

        if user:
            save(user,
                session,
                **args_dict
                    )
            desc = "修改成功"
        else:
            status = "ERROR"
            msg = desc = "用户不存在"
        result = dict(status=status, msg=msg, desc=desc)
        return jsonify(result)


class PassengerApi(Resource):

    decorators = [http_basic_auth]

    def get(self):

        args = get_parse.parse_args()
        user_id = args.get("user_id")
        user_name = args.get("user_name")
        if not user_id:
            user = OwnUser.query.filter(OwnUser.user_name == user_name).first()
            user_id = user.id
        else:
            user_id = 0
        passengers = Passenger.query.filter(Passenger.own_id==user_id,
                                            Passenger.other_id==0)
        schema = PassengerSchema()
        result = schema.dumps(passengers,many=True).data
        return Response(result)


    def __args(self,args):

        user_id = args.get("user_id", 0)
        user_name = args.get("user_name")
        passenger_id = args.get("passenger_id", 0)
        passenger_name = args.get("passenger_name")
        passport_id = args.get("passport_id")
        passenger_phone = args.get("passenger_phone")
        passenger_name_en = args.get("passenger_name_en")
        passenger_gender = args.get("passenger_gender")
        due_date = args.get("due_date")

        if due_date:
            due_date = datetime.strptime("due_date","%Y-%m-%d HH:MM:SS")

        user_dict = dict(user_id=user_id,
                    user_name=user_name,
                    passenger_id=passenger_id)

        args_dict = dict(passenger_name=passenger_name,
                         passport_id=passport_id,
                         passenger_name_en=passenger_name_en,
                         passenger_phone=passenger_phone,
                         passenger_gender=passenger_gender,
                         due_date=due_date
                         )
        return user_dict,args_dict

    def post(self):
        #TODO 其实这里可以做一些改进，按照严格的restful设计标准，post请求是新建资源，
        # TODO 而put和patch请求才是更新资源的，之前都是一直将它们在了一起，新建和更新都是用post请求
        # TODO 但是有问题，有些框架是解析不了PUT请求的参数，好在Flask框架可以，它把PUT请求的参数
        # TODO 都放在了form里
        session = db.session
        status = msg = "OK"

        args = post_parse.parse_args()
        user_dict,args_dict = self.__args(args)

        user_id,user_name = user_dict["user_id"],user_dict['user_name']

        if not user_id:
            user = OwnUser.query.filter(OwnUser.user_name == user_name).first()
            user_id = user.id

        if not user_id:
            raise ObjectDoesNotExist()
        args_dict.update({'own_id':user_id})
        create(Passenger,session,**args_dict)
        desc = "创建成功"

        result = dict(status=status, msg=msg,desc=desc)
        return jsonify(result)

    def put(self):

        session = db.session
        status = msg = "OK"
        desc = ""
        args = post_parse.parse_args()
        user_dict, args_dict = self.__args(args)

        passenger_id = user_dict["passenger_id"]
        passenger_name = args_dict['passenger_name']
        if passenger_id > 0:

            passenger = Passenger.query.get(passenger_id)
            if passenger:
                if passenger_name:
                    name_pinyin_list = lazy_pinyin(passenger_name)
                    name_pinyin = "%s " % name_pinyin_list[0] + "".join(
                        name_pinyin_list[1:])
                    args_dict["passenger_name_en"] = name_pinyin

                save(passenger, session, **args_dict)
                desc = "修改成功"
            else:
                status = "ERROR"
                msg = desc = "该乘客不存在"
        result = dict(status=status, msg=msg, desc=desc)
        return jsonify(result)


class UserOrderApi(Resource):

    decorators = [http_basic_auth,]

    def get(self):

        args = get_parse.parse_args()
        user_id = args.get("user_id")
        user_name = args.get("user_name")
        page = args.get("page")
        schema = OrderSchema()
        if not user_id:
            user = OwnUser.query.filter(OwnUser.user_name == user_name).first()
            user_id = user.id
        else:
            raise ObjectDoesNotExist()

        paginates = Order.query.filter(Order.own_id==user_id
                                    ).paginate(page, 10, False)
        orders = paginates.items
        page_number = paginates.pages# 表示一共有多少页
        all_number =  paginates.total# 一个有多少订单

        result = schema.dumps(orders,many=True).data
        return jsonify(status=1,
                       detail=result,
                       page_number=page_number,
                       all_number=all_number)



class OrderDetailApi(Resource):

    decorators = [http_basic_auth,]

    def get(self):
        args = get_parse.parse_args()
        user_id = args.get("user_id")
        order_id = args.get("order_id")
        ticketsolds = TicketSold.query.join(Order,TicketSold.order_id==Order.id
                                            ).filter(
                                            Order.own_id==user_id,
                                            Order.own_id==0,
                                            Order.id==order_id
                                            ).all()
        if ticketsolds:
            schema = TicketSoldSchema()
            result = schema.dumps(ticketsolds,many=True)
            return Response(result)
        else:
            status = "ERROR"
            msg = "你暂无权限访问该用户名下的订单详情"
            return jsonify(status=status,msg=msg)

    def put(self):

        session = db.session
        data = post_parse.parse_args()
        order_id = data.get("order_id")
        pay_state = data.get("pay_state")
        user_id = data.get("user_id")

        if pay_state == "2":
            return Response(json.dumps({"status": 0, "msg": "User has paid"}))


        order = Order.query.filter_by(order_id=order_id,
                                      own_id=user_id,
                                      other_id=0,
                                      pay_state="1"
                                          ).first()
        if order:
            _tmp = dict(order_status="5")
            save(order,session,**_tmp)
            return Response(json.dumps({"status": 1, "msg": "cancel it successfully"}))
        else:
            return Response(json.dumps({"status": 0, "msg": "order does not exist"}))


class WXPayApi(Resource):


    def __create_order(self,session,
                        user_id,
                        passenger_ids,
                        ticket_pdf,
                        order_id_agent,
                        route_id,
                        ticket_left_id,
                        price_RMB,
                        total_price,
                        travel_agent_id=2,
                        order_status="0",
                        pay_state="1",
                        departure_date=None,

                     ):
        from app.celery_task.tasks import send_email
        getcontext().prec = 4
        order_column = dict(own_id=user_id,
                      agent_id=travel_agent_id,
                      order_status=order_status,
                      number=len(passenger_ids),
                      other_id=0,
                      pay_state=pay_state,
                      order_id_agent=order_id_agent,  # 这个是订单号，调用微信支付时必须要的
                      route_id=route_id,
                      total_price=Decimal(total_price),
                      ticket_pdf=ticket_pdf,
                      departure_date=departure_date#TODO 格式YY-mm-dd HH:MM

                      )

        order = create(Order,session,**order_column)

        order_id = self.__create_ticket_sold(
            order.order_id,
            passenger_ids,
            price_RMB,
            ticket_left_id
        )
        #send_email.apply_async()
        return order_id


    def __create_ticket_sold(self,
                             order_id,
                             passenger_ids,
                             price_RMB,
                             ticket_left_info
                             ):


        try:

            db.session.execute(TicketSold.__table__.insert(),
                               [{"order_id": order_id,
                                 "passenger_id": passenger_id,
                                 "ticket_left_info": ticket_left_info,
                                 "price_RMB": price_RMB} for passenger_id in passenger_ids]
                               )
            db.session.commit()  # 批量插入数据
            return order_id
        except:
            order = Order.query.get(order_id)
            db.session.delete(order)
            db.session.commit()
            return 0

    def post(self):

        data = post_parse.parse_args()
        session = db.session

        user_id = data.get("user_id", "")
        open_id = data.get("open_id", "")
        passenger_ids = data.get("passenger_ids", '')
        ticket_left_id = data.get("ticket_left_id", "0")
        price_RMB = data.get("price_RMB")
        order_id_agent = data.get("order_id_agent", '').strip()
        route_id = data.get("route_id", "0").strip()
        total_price = data.get("total_price")
        departure_date = data.get("outbound_date")

        user = OwnUser.query.get(user_id)
        if open_id:
            user = OwnUser.query.filter_by(open_id=open_id).first()

        if user:
            user_id = user.user_id
            if passenger_ids:
                try:
                    passenger_ids = json.loads(passenger_ids)
                except:
                    return Response(json.dumps({
                        "status": 0,
                        "error_reasson": "The data format is invalid"}))

                order_id = self.__create_order(session==session,
                                               user_id=user_id,
                                                passenger_ids=passenger_ids,
                                                ticket_pdf=None,
                                                order_id_agent=order_id_agent,
                                                price_RMB=price_RMB,
                                                route_id=route_id,
                                                total_price=total_price,
                                                ticket_left_id=ticket_left_id,
                                                departure_date=departure_date
                                        )
                if not order_id:
                    return Response(
                        json.dumps({"status": 0, "error_reasson": "create order failly"}))
                return Response(
                    json.dumps({"status": 1, "order_id": order_id}))

        return Response(
                json.dumps({"status": 0,
                            "error_reason": "user does not exist or the data of pessenger is invalid "}))


class WXLoginApi(Resource):
    """
    微信登录小程序api
    """

    decorators = [http_basic_auth]

    def get(self):
        """
        接受传过来的js_code
        :return: 
        """

        args = get_parse.parse_args()
        code = args.get("code")
        openid = self.__wx_login(code)
        return jsonify(openid=openid)

    def post(self):

        args = post_parse.parse_args()
        code = args.get("code")
        openid = self.__wx_login(code)
        return jsonify(openid=openid)

    def put(self):
        """
        保存登录后获取的openid,并将openid传给小程序
        :return: 
        """
        session = db.session
        args = post_parse.parse_args()
        open_id = args.get("open_id")
        user_id = args.get("user_id")
        login_time = datetime.now()#记录用户最新登录时间
        args_dict = dict(login_time=login_time)
        if open_id:
            user = OwnUser.query.filter(OwnUser.open_id == open_id).first()

            if user:  # 如果user存在，则返回user_id
                user_id = user.user_id
                args_dict.update({"open_id":open_id})
                save(user,session,**args_dict)
            else:
                user = OwnUser(open_id=open_id)
                db.session.add(user)
                db.session.commit()
                user_id = user.user_id
            return Response(json.dumps(user_id))
        else:
            if user_id:
                user = OwnUser.query.get(user_id)
                if user:
                    save(user,session,**args_dict)
            return Response(json.dumps(user_id))


    def __wx_login(self,js_code):


        appId = 'xxxxxxxxx'
        appSecret = 'yyyyyyyyyyyy'
        if js_code:
            url = 'https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code'.format(
                appId, appSecret, js_code)

            response = requests.get(url)
            data = response.json()

            if "openid" in data:
                openid = data["openid"]
                return openid
        return 0



class PayUnifiedorderApi(Resource):

    decorators = [http_basic_auth]


    def __random_str(self,num):
        """
        生成num个随机字符串
        :param num: 
        :return: 
        """
        Str = "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789"
        l = random.sample(Str, num)
        return "".join(l)

    def __md5_Encrypt(self,strA):
        """
        md5加密
        :param strA: 
        :return: 
        """
        m = md5(strA.encode(encoding='utf-8'))
        return m.hexdigest().upper()


    def __paysignjsapi(self,mch_key, **data):
        """
        统一下单api签名算法

        """
        # 第一步按照参数名规范化参数
        data1 = sorted(data.items(), key=lambda one: one[0])

        stringA = ''.join(["&{0}={1}".format(one[0], one[1]) for one in data1])
        stringA = stringA[1:]
        stringSignTemp = stringA + "&key=%s" % mch_key  #
        sign = self.__md5_Encrypt(stringSignTemp)  # ＡＰＩ秘钥
        return sign

    def __to_xml(self,raw):
        """
        将字典转换为xml形式的字符串
        :param raw: 
        :return: 
        """
        s = ""
        for k, v in raw.items():
            s += "<{0}>{1}</{0}>".format(k, v)
        s = "<xml>{0}</xml>".format(s)
        return s.encode("utf-8")

    def __to_dict(self,xml_):
        """
        将xml形式得字符串转换为字典
        :param xml_: 
        :return: 
        """
        data = {}
        root = etree.fromstring(xml_)
        for one in root:
            data[one.tag] = one.text
        return data

    def __paysignjs(self,mch_key, appid, nonce_str, prepay_id, timeStamp):
        """
        再次签名算法

        """

        _dict = {
            'appId': appid,
            'nonceStr': nonce_str,
            'package': "prepay_id=%s" % prepay_id,
            'signType': "MD5",
            'timeStamp': timeStamp,
        }
        ret1 = sorted(_dict.items(), key=lambda one: one[0])
        stringA = ''.join(["&{0}={1}".format(one[0], one[1]) for one in ret1])
        stringA = stringA[1:]
        stringSignTemp = stringA + "&key=%s" % mch_key  # API密钥

        sign = self.__md5_Encrypt(stringSignTemp)  # ＡＰＩ秘钥


        return sign

    def post(self):
        """
       微信支付服务后台生成预支付交易单 申请付款,
       同时prepay_id的获取和签名paySign
        :return: 
        """
        args = post_parse.parse_args()

        appid = 'xxxxxxxxxxxx'
        mch_id = "yyyyyyyyyy"
        device_info = "WEB"
        nonce_str = self.__random_str(18)
        body = "ABC"

        attach = "ABC"
        out_trade_no = args.get("out_trade_no", "")
        total_fee = args.get("total_fee", 0)
        trade_type = "JSAPI"
        order_id = args.get("order_id", 0)
        user_id = args.get("user_id", 0)
        openid = args.get("openid", '')
        notify_url = "https://open.staging.bodaboda.com.cn/api/v1/pay_result/"
        spbill_create_ip = "192.168.1.1"
        mch_key = "9hj2qp6e8s17noldicf0bt5mzwx4yk3r"

        sign = self.__paysignjsapi(mch_key=mch_key,
                            appid=appid,
                            mch_id=mch_id,
                            device_info=device_info,
                            nonce_str=nonce_str,
                            notify_url=notify_url,
                            body=body,
                            attach=attach,
                            out_trade_no=out_trade_no,
                            total_fee=total_fee,
                            openid=openid,
                            trade_type=trade_type,
                            spbill_create_ip=spbill_create_ip)
        url = "https://api.mch.weixin.qq.com/pay/unifiedorder"

        if not openid:
            try:
                user = OwnUser.query.get(int(user_id))
                openid = user.open_id
                if not openid:

                    return jsonify(status=0,err_code="openid is null")
            except:

                return jsonify(status=0, err_code="openid is null")

        dict_ = {
            'appid': appid,
            'mch_id': mch_id,
            'device_info': device_info,
            'nonce_str': nonce_str,
            "notify_url": notify_url,
            'body': body,
            "openid": openid,
            'attach': attach,
            'out_trade_no': out_trade_no,
            'total_fee': total_fee,
            'trade_type': trade_type,
            'spbill_create_ip': spbill_create_ip,
            "sign": sign,
        }

        formData = self.__to_xml(dict_)
        result = requests.session().post(url, data=formData)  # ,headers=headers)
        result = result.content.decode("utf-8")  # 转化为二进制相应内容

        try:
            xml_dict = self.__to_dict(result)
        except:
            return jsonify(status=0, err_code="net error 1l")

        if xml_dict["return_code"] == "SUCCESS":
            if xml_dict["result_code"] == "SUCCESS":
                # return_code 和result_code都为SUCCESS时有prepay_id
                prepay_id = xml_dict["prepay_id"]

                timeStamp = str(int(time()))
                paySignjs = self.__paysignjs(mch_key,
                                             appid,
                                             nonce_str,
                                             prepay_id,
                                             timeStamp
                                             )
                return Response(json.dumps({"status": 1, "prepay_id": prepay_id,
                                            "paySign": paySignjs,
                                            "appid": xml_dict["appid"],
                                            'nonce_str': nonce_str,
                                            'timeStamp': timeStamp,
                                            'package': "prepay_id=%s" % prepay_id
                                            }))
            else:
                return Response(json.dumps(
                    {"status": 0,
                    "err_code": xml_dict.get("err_code") if xml_dict.get(
                                                "err_code") else "get sigin err"}
                ))
        else:
            return Response(json.dumps({"status": 0, "err_code": "net error 2"}))


class LocationApi(Resource):

    decorators = [http_basic_auth]

    def get(self):
        """
        获取资源信息
        :return: 
        """
        args = get_parse.parse_args()
        location_id = args.get("location_id")
        location = Location.query.get(location_id)
        schema = LocationSchema()
        result = schema.dumps(location).data
        return jsonify(result)


class CityApi(Resource):

    decorators = [http_basic_auth]

    def _get_all_city(self):
        all_citys = City.query.order_by(desc("city_pinyin"))  # filter()
        hot_city = City.query.order_by(desc("search_heat"))[:15]  # 热门城市
        length = all_citys.count()
        schema = CitySchema()
        # 对城市信息进行分组
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
                   'O', 'P','Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        result2 = []
        result1 = schema.dump(all_citys,many=True,).data
        result4 = schema.dump(hot_city,many=True).data
        groupname = []
        result3 = {}.fromkeys(letters,[])

        tmp = filter(lambda city:city["city_pinyin"] ,result1 )

        for city in tmp:
            pinyin = city["city_pinyin"]
            first_pinyin = pinyin[0]
            result3[first_pinyin].append(city)


        for key, value in result3.items():

            tmp = {
                    "groupname": key,
                    "member": value
                }
            result2.append(tmp)
            groupname.append(key)

            result2 = sorted(result2, key=lambda one: one["groupname"])
            groupname = sorted(groupname)
        result = {"length": length,
                  "group": result2,
                  "hot_city": result4,
                  "groupname": groupname
                  }
        return result

    def get(self):
        from app import redis_store

        result_X = redis_store.get("all_city")
        if result_X:
            r = result_X.decode("utf-8")
            try:
                result = eval(r)
            except:
                result = self._get_all_city()
            print(111)
        else:
            result = self._get_all_city()
            redis_store.set("all_city", result)

        return Response(json.dumps(result))

    def put(self):

        args = post_parse.parse_args()

        departure = args.get("departure", "").strip()
        destination =args.get("destination", "").strip()
        citys = City.query.filter(or_(City.city_zh == destination,
                                      City.city_zh == departure))
        for city in citys:
            city.search_heat += 1
            db.session.add(city)
        db.session.commit()
        return Response(json.dumps(1))


class RouteApi(Resource):

    decorators = [http_basic_auth]

    def get(self,route_type):

        args = get_parse.parse_args()
        route_id = args.get("route_id")
        route = Route.query.get(route_id)

        if route_type == "average":

            score = route.route_score_avg if route else 0.0

            return jsonify(score=score)

        elif route_type == "pictures":

            info = route.route_pictures if route else []
            return jsonify(status='1',info=info)

        elif route_type == "comment":

            page = args.get("page")
            paginates = RouteComment.query.filter_by(
                route_id=route_id).paginate(page,10,False)
            all_comments = paginates.items
            info = [one.get_route_comment for one in all_comments]
            page_number = paginates.pages  # 表示一共有多少页
            all_number = paginates.total  # 一个有多少条评论
            return jsonify(status="1",
                           info=info,
                           page_number=page_number,
                           all_number=all_number
            )
        else:
            #如果是其它请求，直接返回404页面，表示该资源请求不存在
            return  render_template('404.html')


class RouteCommentApi(Resource):

    decorators = [http_basic_auth]

    def post(self):
        data = post_parse.parse_args()
        route_id = data.get("route_id")
        user_id = data.get("user_id")
        comment = data.get("comment", "").strip()
        score = data.get("score",)
        is_anonymous = data.get("is_anonymous")
        order_id = data.get("order_id")

        result = {"status": 1, "msg": "OK"}

        routecomment = RouteComment(route_id=route_id,
                                    user_id=user_id,
                                    comment=comment,
                                    score=score,
                                    is_anonymous=is_anonymous,
                                    order_id=order_id,
                                    )
        order = Order.query.get(order_id)
        if order:
            order.is_reviewed = 1
            db.session.add(order)
        db.session.add(routecomment)
        db.session.commit()
        return jsonify(result)


    def get(self):

        data = get_parse.parse_args()
        user_id = data.get("user_id", 0)
        open_id = data.get("open_id", "")
        user_name = data.get("user_name", "")
        page = data.get("page", 1)
        result = {"status": 1,
                  "info": [],
                  "page_number": 0,
                  "all_number": 0,
                  }

        user = None

        if user_id:
            user = OwnUser.query.get(user_id)

        if open_id:
            user = OwnUser.query.filter_by(open_id=open_id).first()

        if user_name:
            user = OwnUser.query.filter_by(user_name=user_name).first()

        if user:
            all_num = RouteComment.query.count()
            page_num = all_num / 10 + 1
            if page > page_num:
                result["status"] = 0
                result["msg"] = "page 超出了范围"
                return Response(json.dumps(result))
            result["page_number"] = page_num
            result["all_number"] = all_num
            start = 10 * (page - 1)
            result["info"] = [one.get_order_info for one in RouteComment.query.offset(
                start).limit(10)]
            return Response(json.dumps(result))

        return Response(json.dumps({"status": 0, "msg": "该用户在数据库中不存在"}))