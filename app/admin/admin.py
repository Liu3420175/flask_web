"""
后台管理
"""

from flask_admin import BaseView, expose, babel
from flask_admin.contrib.sqla import ModelView
from flask_login import login_required
from flask import  redirect, url_for,request
import app
from jinja2 import Markup
from flask_login import current_user
from wtforms.fields import SelectField, BooleanField
from datetime import datetime
from datetime import timedelta

today = datetime.today()
in_30_days_later = today + timedelta(days=30)
TODAY = today.strftime("%Y-%m-%d")
IN_30_DAYS_LATER = in_30_days_later.strftime("%Y-%m-%d")

ORDER_STATUS_LIST = [
    ('0', 'A'),
    ('1', 'B'),
    ('2', 'C'),
    ('3', 'D'),
    ('4', 'E'),
    ('5', 'F'),
    ('6', 'G'),
    ('7', 'H'),
    ('8', 'I'),
]

ORDER_STATUS = dict(ORDER_STATUS_LIST)
ORDER_STATUS.update(dict([('', ''),
                          (None, '')]))

PAY_STATE_LIST = [
    ('1', 'A'),
    ('2', 'B'),
    ('3', 'C'),
]

PAY_STATE = dict(PAY_STATE_LIST)
PAY_STATE.update(dict([
    ('', ''),
    (None, ''),
]
))

GENDER_LIST = [
    ('1', "男"),
    ("0", "女"),
]

GENDER = dict(GENDER_LIST)
GENDER.update(dict([
    ("", ""),
    (None, "")
]
))

IS_SUPER_LIST = [
    (0, "否"),
    (1, "是"),
]

IS_SUPER = dict(IS_SUPER_LIST)
IS_SUPER.update(dict([
    ('', "否"),
    (None, "否"), ]))

# 将每个视图的过滤器定义在此处,字段顺序决定了链接形式
PassengerView_column_filters = ["id"]
OrderView_column_filters = ["id", "own_id","other_id"]
UserView_column_filters = ["id","user_name", "contact_name", "contact_phone", "contact_id"]
TicketSoldView_column_filters = ["order_id"]


class MyIndexView(BaseView):
    """
    自定义/admin首页模板
    """

    def __init__(self, name=None, category=None,
                 endpoint=None, url=None,
                 template='auth/admin_index.html',#自定义首页,如果了解Jinja
                                                  # 框架的原理，这一步其实很好理解
                 menu_class_name=None,
                 menu_icon_type=None,
                 menu_icon_value=None):
        super(MyIndexView, self).__init__(name or babel.lazy_gettext('Home'),
                                           category,
                                           endpoint or 'admin',
                                           '/admin' if url is None else url,
                                           'static',
                                           menu_class_name=menu_class_name,
                                           menu_icon_type=menu_icon_type,
                                           menu_icon_value=menu_icon_value)
        self._template = template

    @login_required
    @expose()
    def index(self):
        return self.render(self._template)

class ModelMixin(object):

    #TODO 混入设计模式,简化代码

    def is_accessible(self):
        """
        判断用户是否有权限
        :return: 
        """
        if current_user.is_authenticated and current_user.is_superuser == True:
            return True
        return False


    def inaccessible_callback(self, name, **kwargs):
        """
        无权限返回登陆页
        """
        return redirect(url_for('auth.login_index', ))

    list_template = "auth/list.html"
    edit_template = "auth/edit.html"
    details_template = "auth/details.html"
    create_template = "auth/create.html"


class OrderView(ModelMixin,ModelView):

    column_labels = {  # 需要显示的列的别名
        "id": "ID",
        "user": "客户",
        "travel_agent": "销售渠道",
        "number": "数量",
        "create_time": "购买时间",
        "order_id_supplier": "供应商订单号",
        "pay_state": "支付状态",
        "order_status": "订单状态",
        "ticket_pdf": "PDF",
        "order_id_agent": "销售渠道订单号",
        "detail": "查看详情",
        "arrive_time": "预计到达时间",
        "to_city_chinese": "目的地",
        "from_city_chinese": "出发地",
        "departure_time": "出发时间",
        "total": "总金额",
        "route_id": "路线",
    }

    _extra_labels = {
        "arrive_time": "预计到达时间",
        "to_city_chinese": "目的地",
        "from_city_chinese": "出发地",
        "departure_time": "出发时间"
    }

    can_delete = False
    can_create = False
    named_filter_urls = True

    column_default_sort = ('id', True)#设置默认排序方式，id从大到小的顺序
    form_overrides = dict(order_status=SelectField
                          , pay_state=SelectField)  # 覆盖默认的标签

    form_edit_rules = [key for key in column_labels
                       if key not in ["id","detail", "arrive_time",
                                    "to_city_chinese",
                                    "from_city_chinese",
                                    "departure_time", "total", "user"]]
    # edit页面可以修改的字段

    column_details_list = [key for key in column_labels]
    _form_args = {
        key: {
            "render_kw": {"disabled": True}  # TODO 不准许edit页面user字段修改
        } for key in column_labels if key not in ["pay_state", "order_status",
                                                  "detail", "arrive_time",
                                                  "to_city_chinese",
                                                  "from_city_chinese",
                                                  "departure_time", "total", "route_id"]

        # 'order_status': {"choices": ORDER_STATUS_LIST}
    }  # 字典推到式
    # form_create_rules = [key for key in column_labels if key not in ("order_id",)]
    _form_args.update({'order_status': {"choices": ORDER_STATUS_LIST},
                       "pay_state": {"choices": PAY_STATE_LIST}})
    form_args = _form_args  # 也可以用form_widget_args
    column_extra_row_actions = [

    ]  # TODO 添加自定义操作，默认的是增加，修改，详情
    form_widget_args = {  # 只改变edit页面某些字段的前端样式
        "order_status": {
            "style": "color:red",
        },

        # "pay_state":{
        # "onclick":"window.location.href='www.baidu.com'" #TODO 用这种方法可将某个字段的值的显示变成链接形式
        # }
    }
    # {
    # "user":{
    #      "render_kw":{"disabled":True}#TODO 不准许edit,create等页面user字段修改
    # },

    # }
    column_list = ("id", "create_time", "user", "travel_agent",
                   "number", "order_id_supplier", "order_status",
                   "pay_state","detail"  # TODO 可以自定义列
                   )

    column_formatters = {
        "user": lambda v, c, m, p: Markup(
            "<a href='/admin/user/details/?id={0}'>{1}</a>".format(
                m.user.user_id, m.user.contact_name)) if m.user else Markup(
            "<span>未知</span>"),
        # TODO 定制，可以成为链接,如果是这样的话，可以将其颜色也可以定制
        "travel_agent": lambda v, c, m, p: m.travel_agent.name if m.travel_agent else "",
        "detail": lambda v, c, m, p: Markup(
            "<a href='/admin/ticketsold/?flt1_{0}={1}'>订单详情</a>".format(
                7 * TicketSoldView_column_filters.index("order_id"),
                m.id
            )
        ),
        "arrive_time": lambda v, c, m, p: m.get_ticket_info_by_order["arrive_time"],
        "to_city_chinese": lambda v, c, m, p: m.get_ticket_info_by_order["to_city_chinese"],
        "from_city_chinese": lambda v, c, m, p: m.get_ticket_info_by_order["from_city_chinese"],
        "departure_time": lambda v, c, m, p: m.get_ticket_info_by_order["departure_time"],
        "total": lambda v, c, m, p: m.total,
    }
    # column_display_all_relations = True
    # column_editable_list = ["order_status","pay_state"]

    column_filters = OrderView_column_filters  # 开启筛选器

    column_choices = {  # 将选项映射到列表视图中
        'pay_state': PAY_STATE_LIST,
        "order_status": ORDER_STATUS_LIST
    }
    can_view_details = True
    can_export = True  # 开启导出功能

    def __init__(self, session, **kwargs):
        from app.models import Order

        super(OrderView, self).__init__(Order, session, **kwargs)


class OwnUserView(ModelMixin,ModelView):

    column_labels = {
        "id": "ID",
        "user_name": "用户名",
        "user_gender": "性别",
        "contact_email": "E-mail",
        "contact_name": "姓名",
        "contact_phone": "联系电话",
        "contact_id": "护照",
        "is_superuser": "是否是超级用户",
        "open_id": "微信openid",
        "detail": "查看"
    }
    column_extra_row_actions = [

    ]
    can_delete = False
    form_overrides = dict(is_superuser=BooleanField,
                          user_gender=SelectField)
    form_edit_rules = [key for key in column_labels if key not in ("id", "detail")]  # edit页面可以修改的字段
    form_create_rules = [key for key in column_labels if key not in ("id", "detail")]
    column_details_list = [key for key in column_labels]
    _form_args = {
        key: {
            "render_kw": {"disabled": True}
        } for key in column_labels if key in ["user_name"]

    }  # 字典推到式

    form_args = {  # 'is_superuser': {"choices": IS_SUPER_LIST},
        "user_gender": {"choices": GENDER_LIST}
    }

    column_list = ("id", "user_name", "user_gender", "contact_email",
                   "contact_name", "contact_phone", "contact_id", "is_superuser",
                 "detail"
                   )
    column_choices = {
        "user_gender": GENDER_LIST,
        "is_superuser": IS_SUPER_LIST

    }
    column_filters = UserView_column_filters
    column_formatters = {
        # "user_gender": lambda v, c, m, p: GENDER[m.user_gender],
        # "is_superuser": lambda v, c, m, p: IS_SUPER[m.is_superuser],
        "detail": lambda v, c, m, p: Markup(
            "<a href='/admin/passenger/?flt1_0={0}'>乘客信息</a>"
            " <span>/</span> "
            "<a href='/admin/order/?flt1_user_id_equals={0}'>所有订单</a>".format(m.id)
        )

    }

    can_view_details = True

    def __init__(self, session, **kwargs):
        from app.models import OwnUser
        super(OwnUserView, self).__init__(OwnUser,session, **kwargs)


class OtherUserView(ModelMixin,ModelView):
    column_labels = {
        "id": "ID",
        "travel_agent":"客户来源",
        "contact_email": "E-mail",
        "contact_name": "姓名",
        "contact_phone": "联系电话",
        "contact_id": "护照",
        "detail": "查看"
    }
    column_extra_row_actions = [

    ]
    can_delete = False

    form_edit_rules = [key for key in column_labels if key not in ("id", "detail")]  # edit页面可以修改的字段
    form_create_rules = [key for key in column_labels if key not in ("id", "detail")]
    column_details_list = [key for key in column_labels]



    column_list = ("id", "travel_agent",  "contact_email",
                   "contact_name", "contact_phone", "contact_id",
                 "detail"
                   )

    column_filters = ["id","travel_agent"]
    column_formatters = {
        "detail": lambda v, c, m, p: Markup(
            "<a href='/admin/passenger/?flt1_0={0}'>乘客信息</a>"
            " <span>/</span> "
            "<a href='/admin/order/?flt1_user_id_equals={0}'>所有订单</a>".format(m.id)

        ),
        "travel_agent": lambda v, c, m, p: m.travel_agent.name if m.travel_agent else "",

    }

    can_view_details = True

    def __init__(self, session, **kwargs):
        from app.models import OtherUser
        super(OtherUserView, self).__init__(OtherUser,session, **kwargs)


class CityView(ModelMixin,ModelView):

    column_labels = {
        "city_id": "ID",
        "city_zh": "城市(中文名)",
        "city_en": "城市(英文名)",
        "city_pinyin": "中文拼音",
        "country":"国家",
        "search_heat": "热度",
        "detail": "操作"
    }
    can_view_details = True
    column_filters = ["city_zh", "city_en", "city_pinyin", "search_heat"]
    column_details_list = [key for key in column_labels]
    column_list = ["city_id",
                   "city_zh",
                   "city_en",
                   "city_pinyin",
                   "country",
                   "search_heat",
                   "detail"]

    column_formatters = {
        "country":lambda v,c,m,p:m.country.name_zh if m.country else "未知",
        "detail": lambda v, c, m, p: Markup(
            "<a href='/admin/routenode/?flt0_12={0}'>相关路线</a>"
            "<span>/</span>"
            "<a href='/admin/routeschedule/?flt0_5={1}&flt3_11={2}+to+{3}'>近期排班</a>".format(
                ",".join(m.locations), ",".join(m.route_ids), TODAY, IN_30_DAYS_LATER),
        )
    }

    def __init__(self, session, **kwargs):
        from app.models import City
        super(CityView, self).__init__(City, session, **kwargs)


class PassengerView(ModelMixin,ModelView):

    column_labels = {
        "passport_id": "护照",
        "user": "所属用户",
        "passenger_name_en": "英文名",
        "passenger_email": "电子邮件",
        "passenger_gender": "性别",
        "passenger_name": "姓名",
        "passenger_phone": "联系电话",
        "id": "ID",
        "due_date":"护照截止日期"
    }
    column_list = ["id", "passenger_name", "passport_id", "passenger_phone",
                   "passenger_email",
                   "passenger_name_en", "user","due_date"
                   ]
    can_view_details = True
    column_filters = PassengerView_column_filters
    form_edit_rules = [key for key in column_labels if key not in ("passenger_id", "user")]
    form_create_rules = [key for key in column_labels if key not in ("passenger_id",)]

    form_args = {
        "passenger_gender": {"choices": GENDER_LIST}
    }

    column_formatters = {
        "user":lambda v,c,m,p:m.user
    }
    def __init__(self, session, **kwargs):
        from app.models import Passenger
        super(PassengerView, self).__init__(Passenger, session, **kwargs)


class TicketSoldView(ModelMixin,ModelView):
    """
    票务详情，其实也是订单详情
    """

    column_labels = {
        "id": "ID",
        "arrive_time": "预计到达时间",
        "to_city_chinese": "目的地",
        "from_city_chinese": "出发地",
        "departure_time": "出发时间",
        "price_RMB": "票价(RMB)",  # 票价
        "passenger": "乘客",  # 乘坐人
        #"supplier": "供应商",
        "ticket_sold_status": "出票状态",
        "order": "订单号"
    }
    can_create = False
    can_view_details = False
    can_delete = False
    can_edit = True
    # form_overrides = dict(routeschedules=StringField)
    form_edit_rules = [
     "ticket_sold_status", 'ticket_sold_seat',
        'price_RMB', 'ticket_code']

    column_list = ["id", "passenger", "from_city_chinese", "to_city_chinese",
                   "departure_time", "price_RMB",  "ticket_sold_status",
                   "arrive_time"
                   ]

    #column_filters = TicketSoldView_column_filters

    column_formatters = {
        "arrive_time": lambda v, c, m, p: m.ticket_info["arrive_time"] if m.ticket_info else "",
        "to_city_chinese": lambda v, c, m, p: m.ticket_info["to_city_chinese"] if m.ticket_info else "",
        "from_city_chinese": lambda v, c, m, p: m.ticket_info["from_city_chinese"] if m.ticket_info else "",
        "departure_time": lambda v, c, m, p: m.ticket_info["departure_time"] if m.ticket_info else "",


        "passenger": lambda v, c, m, p: Markup(
            "<a href='/admin/passenger/?flt1_{0}={1}'>{2}</a>".format(
                7 * PassengerView_column_filters.index("id"), m.id,
                m.passenger.passenger_name
            )
        )
    }

    def __init__(self, session, **kwargs):
        from app.models import TicketSold
        super(TicketSoldView, self).__init__(TicketSold, session, **kwargs)


class LocationView(ModelMixin,ModelView):

    column_labels = {
        'city_chinese': "城市中文名",
        'city_code': "城市代码",
        'city_en': "城市英文名",
        'city_tel_code': "电话区号",
        'latitude': "维度",
        'loc_name_chinese': "地点中文名",
        'loc_name_en': "地点英文名",
        'id': "ID",
        'longitude': "经度",
        "location_id_supplier": "供应商地点ID"
    }
    can_view_details = True
    column_filters = ["city_chinese"]

    column_list = ['id', 'city_chinese', 'city_en', 'loc_name_chinese',
                   'city_code', 'city_tel_code', 'latitude', 'longitude'
                   ]
    column_details_list = ['id', 'city_chinese', 'city_en', 'loc_name_chinese',
                           'city_code', 'city_tel_code', 'latitude', 'longitude']
    form_edit_rules = ['city_chinese', 'city_en', 'loc_name_chinese',
                       'city_code', 'city_tel_code', 'latitude', 'longitude']

    form_create_rules = ['city_chinese', 'city_en', 'loc_name_chinese',
                         'city_code', 'city_tel_code', 'latitude', 'longitude',
                         "location_id_supplier"]

    def __init__(self, session, **kwargs):
        from app.models import Location
        super(LocationView, self).__init__(Location, session, **kwargs)


class RouteNodeView(ModelMixin,ModelView):

    column_labels = {
        "route": "所属路线",
        "city": "城市",
        "nature": "始发/目的",
        "operator": "汽车公司",
        "supplier": "供应商",
        "recent": "详情",
        "locations": "汽车站名",
        "time": "时间戳",

    }
    can_view_details = True
    column_list = ["route", "city", "nature", "operator", "supplier", "location", "recent"]
    form_create_rules = ["route", "location", "time"]
    column_filters = ["route_id", "location_id", "route.operator", "location.loc_name_chinese"]
    create_template = "auth/create.html"

    column_formatters = {
        "route": lambda v, c, m, p: m.route_id,
        "location": lambda v, c, m, p: m.location.loc_name_chinese,
        "city": lambda v, c, m, p: m.locations.city_chinese,
        "operator": lambda v, c, m, p: m.route.operator.operator_name,
        "supplier": lambda v, c, m, p: m.route.operator.supplier.supplier_name,
        "recent": lambda v, c, m, p: Markup(
            "<a href='/admin/route/?flt0_0={0}'>查看</a>".format(m.route_id)
        ),
        "nature": lambda v, c, m, p: Markup(
            """
              <span style='color:red;'>{0}</span> 
            """.format(m.location_nature)
        ) if m.location_nature == '出发地' else m.location_nature
    }

    def __init__(self, session, **kwargs):
        from app.models import RouteNode
        super(RouteNodeView, self).__init__(RouteNode, session, **kwargs)


class RouteView(ModelMixin,ModelView):
    """
    路线详情
    """
    column_labels = {
        "id": "ID",
        "operator": "汽车公司",
        "supplier": "供应商",
        "arrive_time": "预计到达时间",
        "to_loc_chinese": "目的地",
        "from_loc_chinese": "出发地",
        "departure_time": "出发时间",
        "vehicle_type": "车型",
        "total_seat": "座位数",
        "price_RMB": "票价(RMB)",
        "stop_sale": "最迟买票时间(h)",
        "mileage": "距离(KM)"
    }

    can_view_details = True
    can_edit = False
    can_create = False
    can_delete = False

    column_list = ["id", "supplier", "operator", "from_loc_chinese",
                   "to_loc_chinese", "departure_time", 'arrive_time',
                   'vehicle_type', 'total_seat', 'price_RMB',
                   'mileage', 'stop_sale']

    column_details_list = column_list

    column_filters = ["route_id", "operator.operator_name", "operator.supplier"]

    column_formatters = {
        'supplier': lambda v, c, m, p: m.operator_name[1],
        "operator": lambda v, c, m, p: m.operator_name[0],
        "from_loc_chinese": lambda v, c, m, p: m.route_node_detail[0]["detail"][0]['loc_name_chinese'],
        "to_loc_chinese": lambda v, c, m, p: m.route_node_detail[0]["detail"][1]['loc_name_chinese'],
        "departure_time": lambda v, c, m, p: m.route_node_detail[0]['detail'][0]['hour_minute_str'],
        "arrive_time": lambda v, c, m, p: m.route_node_detail[0]['detail'][1]['hour_minute_str'],
        "vehicle_type": lambda v, c, m, p: m.route_data_detail['vehicle_type'],
        "total_seat": lambda v, c, m, p: m.route_data_detail['total_seat'],
        # 'price_RMB':
        "mileage": lambda v, c, m, p: m.route_data_detail['mileage'],
        "stop_sale": lambda v, c, m, p: round(m.route_data_detail["stop_sale"] / 60, 2),
        "price_RMB": lambda v, c, m, p: m.route_price
    }

    def __init__(self, session, **kwargs):
        from app.models import Route
        super(RouteView, self).__init__(Route, session, **kwargs)



class CurrencyRateView(ModelMixin,ModelView):

    column_labels = {
        'id': "ID",
        'from_currency': "原始币种",
        "to_currency":"目标币种",
        'currency_rate': '汇率',
        "date":"日期"
    }

    can_view_details = True

    column_list = ["id", 'from_currency',"from_currency", 'currency_rate',"date"]
    # column_editable_list = column_labels
    form_edit_rules = ['currency_rate']
    form_create_rules = form_edit_rules
    column_formatters = {
        "from_currency":lambda v,c,m,p:"{0}({1})".format(m.from_currency.name_en,
                                                         m.from_currency.name),
        "to_currency": lambda v, c, m, p: "{0}({1})".format(m.from_currency.name_en,
                                                              m.from_currency.name)
    }

    def __init__(self, session, **kwargs):
        from app.models import CurrencyRate
        super(CurrencyRateView, self).__init__(CurrencyRate, session, **kwargs)


class OperatorsView(ModelMixin,ModelView):
    """
    汽车公司
    """
    can_view_details = True

    column_labels = {
        'id': 'ID',
        'supplier': '供应商',
        'operator_name': '汽车公司名字',
        'operator_phone': '电话',
        'operator_email': 'E-mail',
        'operator_website': '官方网址',
        'operator_address': '地址',
        'operator_logo': 'Logo位置'
    }

    column_list = ['id', 'supplier', 'operator_name', 'operator_phone',
                   'operator_email', 'operator_website', 'operator_address', 'operator_logo'
                   ]

    form_create_rules = ['supplier', 'operator_name', 'operator_phone', 'terms_conditions',
                         'operator_email', 'operator_website', 'operator_address', 'operator_logo'
                         ]
    form_edit_rules = form_create_rules

    column_filters = ['operator_id', 'supplier.supplier_name', 'operator_name']

    column_formatters = {
        'supplier': lambda v, c, m, p: m.supplier.supplier_name
    }

    def __init__(self, session, **kwargs):
        from app.models import Operator
        super(OperatorsView, self).__init__(Operator, session, **kwargs)


class SupplierView(ModelMixin,ModelView):

    can_view_details = True

    column_labels = {
        'id': 'ID',
        'name': '供应商名',
        "country":"国家"
    }

    column_list = ['id', 'name',"country"]
    form_create_rules = ['name',"country"]
    form_edit_rules = ['name',"country"]

    column_formatters = {
        "country":lambda v,c,m,p:m.country.name_zh if m.country else "未知"
    }

    def __init__(self, session, **kwargs):
        from app.models import Supplier
        super(SupplierView, self).__init__(Supplier, session, **kwargs)


class TravelagentView(ModelMixin,ModelView):

    can_view_details = True

    column_labels = {
        'id': "ID",
        'name': '渠道',
        'commission_rate': '利润率',
        "country":"国家"
    }

    column_list = ['id', 'name', 'commission_rate',"country"]

    form_create_rules = ['name', 'commission_rate',"country"]
    form_edit_rules = ['name', 'commission_rate',"country"]
    column_formatters = {
        "country": lambda v, c, m, p: m.country.name_zh if m.country else "未知"
    }

    def __init__(self, session, **kwargs):
        from app.models import TravelAgent
        super(TravelagentView, self).__init__(TravelAgent, session, **kwargs)


class CountryView(ModelMixin,ModelView):

    can_view_details = True
    can_create = True
    can_delete = True
    can_edit = True

    column_labels = {
        "id":"ID",
        "name_zh":"国家",
        "name_en":"国家(英文)",
        "short_name":"英文简称",
        "area":"地区"
    }
    column_list = ["id","name_zh","name_en","short_name","area"]
    form_edit_rules = ["name_zh","name_en","short_name","area"]
    form_create_rules = ["name_zh","name_en","short_name","area"]

    def __init__(self,session,**kwargs):
        from app.models import Country
        super(CountryView,self).__init__(Country,session,**kwargs)






class OrderStatics(BaseView):
    """
    与订单分析有关的类
    """
    @expose("/")
    def index(self):
        from .statistics import month_model_situation,month_days_model_situation,\
            model_increase_fig
        from app.models import Order,TicketSold
        args = request.values
        start_time = args.get("start_date")
        end_time = args.get("end_date")
        today = datetime.today()
        #temporal = 0#时间粒度，默认表示天
        start_date = datetime.strptime(start_time,
            "%Y-%m-%d") if start_time else (today - timedelta(days=30)
                                            ).replace(hour=0,minute=0,second=0)

        end_date = datetime.strptime(end_time,"%Y-%m-%d") if end_time else today.replace(
        hour=0,minute=0,second=0
        )

        delta = end_date - start_date
        if delta.days <= 60:
            #时间粒度:天
            temporal = 0  # 时间粒度，默认表示天
            result  = month_days_model_situation(Order,start_date,end_date)
            result1 = month_days_model_situation(TicketSold,start_date,end_date)
            if delta.days < 31:
                title = "最近30天"
            else:
                title = "{0}至{1}".format(start_date.strftime("%Y-%m-%d"),
                                         end_date.strftime("%Y-%m-%d"))
        else:
            #时间粒度:月
            temporal = 1
            start_month = start_date.replace(day=1)

            end_month = end_date.replace(day=1) + timedelta(days=31)
            end_month = end_month.replace(day=1)
            result = month_model_situation(Order,start_month,end_month)
            result1 = month_model_situation(Order,start_month,end_month)
            title = "{0}至{1}".format(start_month.strftime("%Y-%m"),
                                     end_month.strftime("%Y-%m"))

        html_data = model_increase_fig(result,result1,title,temporal,
                                          ("订单趋势","出票趋势"))

        return self.render("auth/order_static.html",
                           my_data=html_data,
                           start_date=start_date.date(),
                           end_date=end_date.date())




class UserStatics(BaseView):
    """
    与订单分析有关的类
    """
    @expose("/")
    def index(self):
        from .statistics import month_model_situation,month_days_model_situation,\
        model_increase_fig,month_active_model_situation,month_days_active_model_situation, \
            month_user_from_situation, create_active_user_fig
        from app.models import OwnUser
        from app.models import TravelAgent
        args = request.values
        start_time = args.get("start_date")
        end_time = args.get("end_date")
        today = datetime.today()
        #temporal = 0#时间粒度，默认表示天
        start_date = datetime.strptime(start_time,
            "%Y-%m-%d") if start_time else (today - timedelta(days=30)
                                            ).replace(hour=0,minute=0,second=0)

        end_date = datetime.strptime(end_time,"%Y-%m-%d") if end_time else today.replace(
        hour=0,minute=0,second=0
        )

        delta = end_date - start_date
        if delta.days <= 60:
            #时间粒度:天
            temporal = 0  # 时间粒度，默认表示天
            result  = month_days_model_situation(OwnUser,start_date,end_date)
            result1 = month_days_active_model_situation(OwnUser,start_date,end_date)
            if delta.days < 31:
                title = "最近30天"
            else:
                title = "{0}至{1}".format(start_date.strftime("%Y-%m-%d"),
                                         end_date.strftime("%Y-%m-%d"))
        else:
            #时间粒度:月
            temporal = 1
            start_month = start_date.replace(day=1)

            end_month = end_date.replace(day=1) + timedelta(days=31)
            end_month = end_month.replace(day=1)
            result = month_model_situation(OwnUser,start_month,end_month)
            result1 = month_active_model_situation(OwnUser,start_month,end_month)
            title = "{0}至{1}".format(start_month.strftime("%Y-%m"),
                                     end_month.strftime("%Y-%m"))
        distributors = TravelAgent.query.all()
        tmp = {one.name: 0 for one in distributors}
        tmp1 = {one.id: one.name for one in distributors}
        tmp1.update({None: "未知"})
        result_ = month_user_from_situation(start_date, end_date, tmp, tmp1)
        html_data = model_increase_fig(result,result1,title,temporal,
                                          ("新增用户趋势","活跃用户趋势"))
        html_data1 = create_active_user_fig(result_, title)

        return self.render("auth/user_static.html",
                           my_data=html_data,
                           my_data1=html_data1,
                           start_date=start_date.date(),
                           end_date=end_date.date())