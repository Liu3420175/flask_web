from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis
from flask_login import LoginManager
from flask_babelex import Babel
import warnings
from flask_restful import Api
from flask_admin import Admin

from config import config
#from flask import app
from app.admin import *

redis_store = FlaskRedis()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login_index'#TODO 这一步也决定了login_required装饰器跳转到哪个页面
babel = Babel()
admin = Admin(name="",index_view=MyIndexView())


with warnings.catch_warnings():
    #TODO 解决"UserWarning: Fields missing from ruleset"警告
    warnings.filterwarnings('ignore', 'Fields missing from ruleset', UserWarning)
    admin.add_view(OrderView(db.session, name="A", category="AA"))
    admin.add_view(OwnUserView(db.session, name="A", category="BB"))
    admin.add_view(OtherUserView(db.session, name="B", category="BB"))
    admin.add_view(CityView(db.session, name="A", category="CC"), )
    admin.add_view(PassengerView(db.session, name="C", category="BB"))
    admin.add_view(TicketSoldView(db.session, name="B", category="AA"))
    admin.add_view(LocationView(db.session, name="C", category="CC"))
    admin.add_view(RouteNodeView(db.session, name="B", category="CC"))
    admin.add_view(CurrencyRateView(db.session, name="A", category="DD"))
    admin.add_view(SupplierView(db.session, name="B", category="DD"))
    admin.add_view(TravelagentView(db.session, name="C", category="DD"))
    admin.add_view(CountryView(db.session, name="D", category="DD"))

    admin.add_view(OrderStatics(name="Order",category="统计"))
    admin.add_view(UserStatics(name="User",category="统计"))



def create_app(config_name='default', load_bp=False):

 app = Flask(__name__)
 app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
 app.config['BABEL_DEFAULT_LOCALE'] = 'zh_Hans_CN'  # 后台汉化
 app.config.from_object(config[config_name])
 config[config_name].init_app(app)
 app.config.update(SECRET_KEY="BodagqBUBsNH")
 redis_store.init_app(app)
 db.init_app(app)
 login_manager.init_app(app)
 babel.init_app(app)
 api = Api(app)
 admin.init_app(app)
 if load_bp:
     from app.API import UserApi, PayUnifiedorderApi, CityApi, SearchSchedulesApi, \
         WXLoginApi, WXPayApi, LocationApi, OrderDetailApi, RouteApi, UserOrderApi, \
         PassengerApi,RouteCommentApi
     from .auth import auth as auth_url

     api.add_resource(UserApi,"/api/v1/user/")
     api.add_resource(PassengerApi,"/api/v1/passenger/")
     api.add_resource(UserOrderApi,"/api/v1/order/")
     api.add_resource(RouteApi,"/api/v1/route/<string:route_type>/")
     api.add_resource(OrderDetailApi,"/api/v1/order/detail/")
     api.add_resource(LocationApi,"/api/v1/location/")
     api.add_resource(WXPayApi,"/api/v1/wechat/pay/")
     api.add_resource(WXLoginApi,"/api/v1/wechat/login/")
     api.add_resource(PayUnifiedorderApi,"/api/v1/pay/unified/")
     api.add_resource(SearchSchedulesApi,"/api/v1/search/bus/")
     api.add_resource(CityApi,"/api/v1/city/")
     api.add_resource(RouteCommentApi,"/api/v1/routecomment/")

     app.register_blueprint(auth_url,url_prefix="/auth")


 return app
