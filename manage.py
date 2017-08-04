#!/usr/bin/env python
# coding=utf-8

import os
import sys
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell
from app import create_app, db
from app.models import *

# app = create_app(config_name='development', load_bp=True)  # 开发环境
app = create_app(config_name='testing', load_bp=True)   # 测试环境
# app = create_app(config_name='production', load_bp=True)  # 生产环境


manager = Manager(app)



def make_shell_context():
    """
    shell脚本,便于用shell进行测试
    """
    from app import models
    models_name_list = models.__all__  # 获取models.py里所有数据模型的名字
    models_dict = dict(app=app, db=db)
    all_models = models.__dict__
    for name in models_name_list:
        models_dict[name] = all_models[name]
    return models_dict

manager.add_command("shell", Shell(make_context=make_shell_context))

# TODO 数据库迁移命令
# TODO 使用方法:由于之前没有用过这个命令,初次使用时使用命令 python manage.py db init 初始化,
# TODO 然后再修改models.py里的模型
# TODO 再执行命令  python manage.py db migrate -m "inition migrate"
# TODO 再执行 python manage.py db upgrade ,然后就可以发现数据库字段的增减
migrate=Migrate(app,db)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
