from app.models import OwnUser
from . import auth

from .forms import RegistrationForm,LoginForm
from app import db
from flask import render_template, redirect, request, url_for, flash,Response
from flask_login import login_user,logout_user


@auth.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = OwnUser(contact_email=form.email.data,
                    user_name=form.username.data,
                    user_password=form.password.data,
                    contact_id="",
                    contact_name="",
                    contact_phone="",user_gender=1,)
        db.session.add(user)
        db.session.commit()
        flash('You can now login.')
        return redirect(url_for('auth.register'))
    return render_template('auth/register.html', form=form)


@auth.route("/login/index/",methods=['GET', 'POST'])
def login_index():

    return render_template('auth/login.html')


@auth.route('/login/', methods=['GET', 'POST'])
def login():
    data = request.values
    username = data.get('username', '')  # 获取用户名
    password = data.get('password', '')  # 获取密码
    err_message = ''
    if  username:
        user = OwnUser.query.filter(OwnUser.user_name==username,).first()
        if user is not None and user.verify_password(password):
            login_user(user,True)#它的工作原理是通过装饰器user_loader回调其装饰的函数，
                                 # 返回一个user对象，并在会话中存储该对象，用户通过验证后，
                                # 用 login_user 函数来登入他们
            return redirect(url_for("admin.index"))
        else:
            #flash("用户名或者密码错误!")
            err_message = "用户名或者密码错误!"
            #return redirect(url_for("auth.login_index"))
            return render_template('auth/login.html',err_message=err_message)
    else:
        #flash('用户名不能为空!')
        err_message = "用户名不能为空!"
        #return redirect(url_for("auth.login_index"))
        return render_template('auth/login.html', err_message=err_message)



@auth.route("/logout/",methods=["POST","GET"])
def logout():
    logout_user()
    return redirect(url_for("auth.login_index"))