"""
模型序列化
"""
from marshmallow import Schema,fields

class UserSchema(Schema):
    """
    序列化User模型
    """
    id = fields.Int()
    user_name = fields.Str()
    open_id = fields.Str()
    wx_nickname = fields.Str()
    wx_img = fields.Str()
    user_gender = fields.Str()
    contact_email = fields.Str()
    contact_name = fields.Str()
    contact_phone = fields.Str()
    contact_id = fields.Str()
    is_superuser = fields.Bool()


class PassengerSchema(Schema):

    id = fields.Int()
    user_id = fields.Int()
    passenger_name = fields.Str()
    passport_id = fields.Str()
    passenger_phone = fields.Str()
    passenger_name_en = fields.Str()


class OrderSchema(Schema):
    """
    Order序列化对象
    """
    id = fields.Int()
    own_id = fields.Int()
    other_id = fields.Int()
    travel_agent_id = fields.Int()
    order_status = fields.Str()
    number_of_tickets = fields.Int()
    create_time = fields.DateTime()
    order_id_agent = fields.Str()
    order_id_supplier = fields.Str()
    pay_state = fields.Str()
    route_id = fields.Int()
    is_reviewed = fields.Bool()
    total_price = fields.Decimal()
    departure_date = fields.Str()


class TicketSoldSchema(Schema):
    """
    序列化TicketSold对象
    """
    id = fields.Int()
    order_id = fields.Int()
    passenger_id = fields.Int()
    price_RMB = fields.Decimal()
    passenger = fields.Nested(PassengerSchema,only=["passenger_name_en",])
    ticket_left_info = fields.Str()



class LocationSchema(Schema):
    """
    Location序列化
    """
    id =fields.Int()
    loc_name_en = fields.Str()
    loc_name_chinese = fields.Str()
    city_en = fields.Str()
    city_chinese = fields.Str()
    city_code = fields.Str()
    city_tel_code = fields.Str()
    latitude = fields.Str()
    longitude = fields.Str()
    location_id_supplier = fields.Str()


class CountrySchema(Schema):
    """
    国家序列化
    """
    id = fields.Int()
    name_zh = fields.Str()
    name_en = fields.Str()
    short_name = fields.Str()
    area = fields.Str()


class CitySchema(Schema):
    """
    City序列化
    """
    city_id = fields.Int()
    city_zh = fields.Str()
    city_en = fields.Str()
    city_pinyin = fields.Str()
    country_id = fields.Int()
    search_heat = fields.Int()
    country = fields.Nested(CountrySchema,only=["name_zh","name_en"])


class SupplierSchema(Schema):
    """
    
    """
    id = fields.Int()
    name = fields.Str()
    country_id = fields.Int()
    country = fields.Nested(CountrySchema, only=["name_zh", "name_en"])


class OperatorSchema(Schema):
    """
    
    """
    id = fields.Int()
    operator_name = fields.Str()
    operator_phone = fields.Str()
    operator_email = fields.Str()
    operator_website = fields.Str()
    operator_address = fields.Str()
    terms_conditions = fields.Str()
    operator_logo = fields.Str()


