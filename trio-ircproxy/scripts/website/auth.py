from __future__ import annotations
from flask import Blueprint, make_response, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask_sqlalchemy import BaseQuery
from time import time

import json
from os import path
from website import APP_DIR, running_os, Debug
from twisted.internet import reactor

from user_db import User
from user_db import db
from json_data import json_data
from json_data import encrypt_home

auth = Blueprint('auth', __name__)


def no_cache(resp):
    resp.headers['Cache-Control'] = 'max-age=1, No-Store'


@auth.route('/admin-create/', methods=['GET', 'POST', 'HEAD'])
def admin_create():
    if hasattr(current_user, 'user_name'):
        if current_user.type != 'admin-not-ready':
           return redirect(url_for('views.bounce'))
    else:
        return redirect(url_for('auth.not_admin'))
    if request.method == 'POST':
        email: str = request.form.get('email').lower()
        password1: str = request.form.get('password1')
        password2: str = request.form.get('password2')
        # tricky `if / else`+ ahead
        if len(email) < 4:
            flash('Email is too short, must be longer than 3 characters.')
        if password1 != password2 or not password1 or not password2:
            flash('Passwords do not match.', category='error')
        elif not email:
            flash('Email is too short, must be longer than 3 characters.')
        if ('@' not in email):
            flash('That is not an email address.', category='error')
        else:
            ip = request.environ['REMOTE_ADDR']
            admin = User.query.filter_by(user_name='admin').first()
            admin.type = 'admin'
            admin.email = email
            admin.ip = ip
            admin.password = generate_password_hash(password1, method='sha256')

            db.session.commit()
            login_user(admin, remember=True)
            flash('administrator account is created! pls remember your password.', category='success')
            return redirect(url_for('auth.admin_settings'))
    resp = make_response(render_template("admin.html", user=current_user), 200)
    no_cache(resp)
    return resp


@auth.route('/settings/', methods=['GET', 'HEAD', 'POST'])
@auth.route('/settings.py', methods=['GET', 'HEAD', 'POST'])
@auth.route('/settings.html', methods=['GET', 'HEAD', 'POST'])
@auth.route('/settings.htm', methods=['GET', 'HEAD', 'POST'])
@auth.route('/bnc/settings.py', methods=['GET', 'HEAD', 'POST'])
@auth.route('/bnc/settings.html', methods=['GET', 'HEAD', 'POST'])
@auth.route('/bnc/settings.htm', methods=['GET', 'HEAD', 'POST'])
@auth.route('/admin/bnc-settings.htm', methods=['GET', 'HEAD', 'POST'])
@auth.route('/admin/bnc-settings.py', methods=['GET', 'HEAD', 'POST'])
@auth.route('/admin/bnc-settings.html', methods=['GET', 'HEAD', 'POST'])
@auth.route('/admin/bnc-settings/', methods=['GET', 'HEAD', 'POST'])
@auth.route('/admin/bncsettings/', methods=['GET', 'HEAD', 'POST'])
@auth.route('/bnc/settings', methods=['GET', 'HEAD', 'POST'])
def settings():
    if current_user.is_authenticated:
        resp = make_response(render_template('settings.html', user=current_user), 200)
        no_cache(resp)
        return resp
    else:
        return redirect(url_for('auth.login'))


@auth.route('/admin/post/home-data.py', methods=['GET', 'POST'])
def home_data():
    if request.method != 'POST':
        flash('Redirected to the home page.', category='error')
        return redirect(url_for('views.home'))
    if hasattr(current_user, 'user_name') and current_user.user_name != 'admin':
        flash('you MUST log-in as the Admin to post to this URL.', category='error')
        return redirect(url_for('auth.login'))

    if not request.form.get('server_name'):
        flash('invalid Server Name.', category='error')
        return redirect(url_for('auth.admin_settings'))
    for c in request.form.get('server_name'):
        c = c.lower()
        if ord(c) in range(48, 58) and ord(c) not in range(97, 123) and ord(c) != 95 and ord(c) != 46:
            flash('Server Name contains invalid symbols.', category='error')
            return redirect(url_for('auth.admin_settings'))
    json_data.home['home']['server_name'] = request.form.get('server_name')

    if not request.form.get('admin_name'):
        flash('missing Admin NickName.', category='error')
        return redirect(url_for('auth.admin_settings'))
    for c in request.form.get('admin_name'):
        c = c.lower()
        if ord(c) in range(48, 58) and ord(c) not in range(97, 123) and ord(c) != 95 and ord(c) != 46 and ord(c) != 45:
            flash('Admin Name contains invalid symbols.', category='error')
            return redirect(url_for('auth.admin_settings'))

    json_data.home['home']['admin'] = request.form.get('admin_name')
    encrypt_home()
    from fnmatch import fnmatch
    if not request.form.get('email'):
        flash("missing Admin Email Address.", category='error')
        return redirect(url_for('auth.admin_settings'))
    elif '@' not in request.form.get('email'):
        flash('invalid Admin Email Address.', category='error')
        return redirect(url_for('auth.admin_settings'))
    elif not fnmatch(request.form.get('email'), '?*@?*'):
        flash('invalid Admin Email Address.', category='error')
        return redirect(url_for('auth.admin_settings'))
    else:
        json_data.home['home']['email'] = request.form.get('email').lower()
    encrypt_home()

    if not request.form.get('smtp_server'):
        json_data.home['home']['smtp_server'] = 'smtp.' + request.form.get('email').split('@')[2]
        return redirect(url_for('auth.admin_settings'))
    else:
        json_data.home['home']['smtp_server'] = request.form.get('smtp_server')
    encrypt_home()

    if not request.form.get('smtp_password1'):
        flash("you must enter an Password and Confim Password.", category='error')
        return redirect(url_for('auth.admin_settings'))
    elif not request.form.get('smtp_password2'):
            flash("you must enter an Confim Password.", category='error')
            return redirect(url_for('auth.admin_settings'))
    else:
        if request.form.get('smtp_password2') != request.form.get('smtp_password1'):
            flash("the Passwords you entered do not match.", category='error')
            return redirect(url_for('auth.admin_settings'))
        else:
            json_data.home['home']['smtp_password'] = request.form.get('smtp_password2')
    encrypt_home()
    flash("basic server information is saved.", category="success")
    return redirect(url_for('auth.admin_settings'))


@auth.route('/admin/shutdown.htm', methods=['GET', 'POST', 'HEAD'])
@auth.route('/admin/shutdown.html', methods=['GET', 'POST', 'HEAD'])
@auth.route('/admin/shutdown.py', methods=['GET', 'POST', 'HEAD'])
@auth.route('/admin/shutdown/', methods=['GET', 'POST', 'HEAD'])
def admin_shutdown():
    if hasattr(current_user, 'user_name') and current_user.user_name == 'admin':
        if Debug == 'false':
            try:
                reactor.stop()
            except:
                return ('ERROR: unable to shut-down the web-server.',200)
        else:
            func = request.environ.get('werkzeug.server.shutdown')
            if func is None:
                raise RuntimeError('Not running with the Werkzeug Server')
            func()
        return ('Server has been shutdown gracefully.', 200)
    else:
        flash("you are not logged-in as administrator.", category='error')
        return redirect(url_for("auth.not_admin"))


@auth.route('/admin/admin-settings/', methods=['GET', 'POST', 'HEAD'])
@auth.route('/admin-settings/', methods=['GET', 'POST', 'HEAD'])
@auth.route('/admin/admin-settings.htm', methods=['GET', 'POST', 'HEAD'])
@auth.route('/admin/admin-settings.html', methods=['GET', 'POST', 'HEAD'])
def admin_settings():
    if hasattr(current_user, 'user_name') and current_user.user_name == 'admin':
        from json_data import json_data
        resp = make_response(render_template("admin_settings.html", user=current_user, json_data=json_data), 200)
        no_cache(resp)
        return resp
    else:
        flash("you are not logged-in as administrator.", category='error')
        return redirect(url_for('auth.not_admin'))


from random import randrange

forgot_valid: dict[str, dict[str, bool]] = {}


@auth.route('/forgot/', methods=['GET', 'POST', 'HEAD'])
@auth.route('/forgot.py', methods=['GET', 'POST', 'HEAD'])
@auth.route('/forgot.html', methods=['GET', 'POST', 'HEAD'])
@auth.route('/forgot.htm', methods=['GET', 'POST', 'HEAD'])
@auth.route('/admin/forgot.py', methods=['GET', 'POST', 'HEAD'])
@auth.route('/admin/forgot.html', methods=['GET', 'POST', 'HEAD'])
@auth.route('/admin/forgot.htm', methods=['GET', 'POST', 'HEAD'])
def forgot():
    if request.method == 'POST':
        get_user_name = request.form.get('user_name').lower()
        get_email = request.form.get('email').lower()
        if not get_user_name and not get_email:
            flash("you need to enter your UserName and/or E-Mail address.")
        else:
            try:
                user: User | None = None
                email: BaseQuery | None = None
                if get_user_name:
                    user = User.query.filter_by(user_name=get_user_name).first()
                if get_email:
                    email = User.query.filter_by(email=get_email)
                if not user and get_email and email.count() == 0:
                    flash('unknown UserName and E-Mail address.', category='error')
                else:
                    ran: str = str(randrange(10000000, 999999999999999))
                    forgot_valid[ran] = {}
                    valid: bool = forgot_password_request(user, email, forgot_valid[ran])
                    return redirect(url_for("auth.forgot_accepted", valid_pass=ran))
            except:
                raise
                pass
    resp = make_response(render_template("forgot.html", user=current_user), 200)
    no_cache(resp)
    return resp


def forgot_password_request(user: User | bool, email: BaseQuery, ran: dict[str, bool]) -> bool:
    """

    """
    email_set: set[str] = set()
    if user and hasattr(user, 'email'):
        email_set.add(user.email)
        # send email
    if email:
        for e in email:
            email_set.add(e.email)
    for em in email_set:
        ran[em] = False
    if not email_set:
        return False
    else:
        if 'smtp_server' in json_data.home:
            smtp_server = json_data.home['smtp_server'][0]
        if not email:
            return True
        for user in email:
            pass
    return True


@auth.route('/admin/forgot-accepted/', methods=['GET', 'HEAD'])
@auth.route('/admin/forgot-accepted.html', methods=['GET', 'HEAD'])
@auth.route('/admin/forgot-accepted.py', methods=['GET', 'HEAD'])
@auth.route('/admin/forgot-accepted.htm', methods=['GET', 'HEAD'])
def forgot_accepted():
    q: str = request.environ['QUERY_STRING']
    q_split: list[str] = q.split('=')
    q_found: bool = False
    valid_pass: str = ''
    accounts: bool | dict[str, str] = False
    for q in q_split:
        if q_found:
            valid_pass = q
            break
        if q == 'valid_pass':
            q_found = True
            continue
    if valid_pass:
        accounts = forgot_valid.get(valid_pass, False)
        if accounts:
            del forgot_valid[valid_pass]
            resp = make_response(render_template("forgot-accepted.html",
                                                 user=current_user, accounts=accounts), 200)
            no_cache(resp)
            return resp
        else:
            return redirect(url_for('auth.link_expired'))
    else:
        return redirect(url_for('views.home'))


@auth.route("/forgot-expired/", methods=['GET', 'HEAD'])
@auth.route("/forgot-expired.py", methods=['GET', 'HEAD'])
@auth.route("/forgot-expired.html", methods=['GET', 'HEAD'])
@auth.route("/forgot-expired.htm", methods=['GET', 'HEAD'])
def link_expired():
    return make_response(render_template('forgot-expired.html', user=current_user), 200)


@auth.route('/admin/not-admin/', methods=['GET', 'POST', 'HEAD'])
@auth.route('/admin/not-admin.html', methods=['GET', 'POST', 'HEAD'])
@auth.route('/admin/not-admin.py', methods=['GET', 'POST', 'HEAD'])
@auth.route('/admin/not-admin.htm', methods=['GET', 'POST', 'HEAD'])
def not_admin():
    if not hasattr(current_user, 'user_name') or current_user.user_name != 'admin':
        resp = make_response(render_template("not_admin.html", user=current_user), 200)
        no_cache(resp)
        return resp
    if hasattr(current_user, 'user_name') and current_user.user_name == 'admin':
        return redirect(url_for('auth.admin'))


@auth.route('/admin/', methods=['GET', 'POST', "HEAD"])
@auth.route('/admin/index.html', methods=['GET', 'POST', "HEAD"])
@auth.route('/admin/index.htm', methods=['GET', 'POST', "HEAD"])
@auth.route('/admin/index.py', methods=['GET', 'POST', "HEAD"])
@auth.route('/admin/admin.py', methods=['GET', 'POST', "HEAD"])
@auth.route('/admin/admin.htm', methods=['GET', 'POST', "HEAD"])
@auth.route('/admin/admin.html', methods=['GET', 'POST', "HEAD"])
def admin():
    if hasattr(current_user, 'user_name'):
        if current_user.type == 'admin-not-ready':
            return redirect(url_for('auth.admin_create'))
        if current_user.user_name == 'admin':
            return redirect(url_for('auth.admin_settings'))

    try:
        admin_exists = User.query.filter_by(user_name='admin').first()
        if admin_exists:
            return redirect(url_for('auth.not_admin'))
        else:
            return login_new_admin(request.environ['REMOTE_ADDR'])
    except:
        return login_new_admin(request.environ['REMOTE_ADDR'])

def login_new_admin(ip):
    new_user = User(email='noadmin@yoursite.com', type="admin-not-ready", user_name='admin', ip=ip,
                    password=generate_password_hash('no-password', method='sha256'))
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user, remember=True)
    flash('admin account created. change the password right now!', category='success')
    return redirect(url_for('auth.admin_create'))


@auth.route('/login.html', methods=['GET', 'POST', 'HEAD'])
@auth.route('/login/login.htm', methods=['GET', 'POST', 'HEAD'])
@auth.route('/login/login.html', methods=['GET', 'POST', 'HEAD'])
@auth.route('/login/index.htm', methods=['GET', 'POST', 'HEAD'])
@auth.route('/login/index.html', methods=['GET', 'POST', 'HEAD'])
@auth.route('/login/', methods=['GET', 'POST', 'HEAD'])
@auth.route('/login.htm', methods=['GET', 'POST', 'HEAD'])
@auth.route('/admin/login/', methods=['GET', 'POST', 'HEAD'])
@auth.route('/admin/login.html', methods=['GET', 'POST', 'HEAD'])
@auth.route('/admin/login.py', methods=['GET', 'POST', 'HEAD'])
@auth.route('/admin/login.htm', methods=['GET', 'POST', 'HEAD'])
def login():
    if request.method == 'POST':
        user_name = request.form.get('user_name').lower()
        password = request.form.get('password')
        if not user_name and not password:
            flash('you must enter your UserName and Password to log-in.')
        elif not user_name:
            flash('you did not enter your UserName.')
        elif not password:
            flash('you did not enter your Password.')
        else:
            user: User = User.query.filter_by(user_name=user_name).first()
            if user:
                if check_password_hash(user.password, password):
                    flash('logged-in successfully!', category='success')
                    login_user(user, remember=True)
                    return redirect(url_for('views.bounce'))
                else:
                    flash('incorrect Password, try again.', category='error')
            else:
                flash('UserName does not exist!', category='error')
    resp = make_response(render_template("login.html", user=current_user), 200)
    no_cache(resp)
    return resp

@auth.route('/logout/', methods=['GET', 'HEAD'])
@auth.route('/logout/logout.html', methods=['GET', 'HEAD'])
@auth.route('/logout/logout.htm', methods=['GET', 'HEAD'])
@auth.route('/logout/index.html', methods=['GET', 'HEAD'])
@auth.route('/logout/index.htm', methods=['GET', 'HEAD'])
@auth.route('/logout.htm', methods=['GET', 'HEAD'])
@auth.route('/logout.py', methods=['GET', 'HEAD'])
@auth.route('/logout.html', methods=['GET', 'HEAD'])
@auth.route('/admin/logout/', methods=['GET', 'HEAD'])
@auth.route('/admin/logout.py', methods=['GET', 'HEAD'])
@auth.route('/admin/logout.htm', methods=['GET', 'HEAD'])
@auth.route('/admin/logout.html', methods=['GET', 'HEAD'])
def logout():
    if current_user.is_authenticated:
        flash("you have logged-out.")
        logout_user()
        return redirect(url_for('views.home'))
    else:
        flash("you are not logged-in.")
        resp = make_response(render_template("logout.html", user=current_user), 200)
        no_cache(resp)
        return resp


@auth.route('/sign-up/', methods=['GET', 'POST', 'HEAD'])
@auth.route('/signup/', methods=['GET', 'POST', 'HEAD'])
@auth.route('/sign-up.htm', methods=['GET', 'POST', 'HEAD'])
@auth.route('/signup.html', methods=['GET', 'POST', 'HEAD'])
@auth.route('/sign-up.html', methods=['GET', 'POST', 'HEAD'])
@auth.route('/sign-up/index.htm', methods=['GET', 'POST', 'HEAD'])
@auth.route('/signup/index.htm', methods=['GET', 'POST', 'HEAD'])
@auth.route('/signup/index.html', methods=['GET', 'POST', 'HEAD'])
@auth.route('/sign-up/index.html', methods=['GET', 'POST', 'HEAD'])
@auth.route('/sign-up/sign-up.htm', methods=['GET', 'POST', 'HEAD'])
@auth.route('/sign-up/signup.html', methods=['GET', 'POST', 'HEAD'])
@auth.route('/signup/sign-up.htm', methods=['GET', 'POST', 'HEAD'])
@auth.route('/signup/signup.html', methods=['GET', 'POST', 'HEAD'])
@auth.route('/sign-up/sign-up.html', methods=['GET', 'POST', 'HEAD'])
@auth.route('/signup/sign-up.html', methods=['GET', 'POST', 'HEAD'])
@auth.route('/signup.htm', methods=['GET', 'POST', 'HEAD'])
@auth.route('/admin/sign-up/', methods=['GET', 'POST', 'HEAD'])
@auth.route('/admin/signup/', methods=['GET', 'POST', 'HEAD'])
@auth.route('/admin/sign-up.htm', methods=['GET', 'POST', 'HEAD'])
@auth.route('/admin/signup.html', methods=['GET', 'POST', 'HEAD'])
@auth.route('/admin/sign-up.html', methods=['GET', 'POST', 'HEAD'])
@auth.route('/admin/signup.htm', methods=['GET', 'POST', 'HEAD'])
def sign_up():
    if request.method == 'POST':
        ip = request.environ['REMOTE_ADDR']
        now: float = time()
        with open(path.join(APP_DIR[0],"flood.json"), 'r') as sfopen:
            flood: dict = json.load(sfopen)
        remove: list = []
        count: int = 1
        visits: int = -1

        if 'posts_time' not in flood:
            flood['posts_time'] = []
        flood['posts_time'].append(time())
        for visit in flood['posts_time']:
            visits += 1
            if now - visit > 120:
                remove.append(visits)
                continue
            count += 1
        if remove:
            sortlist = []
            remove = sorted(remove)
            for d in reversed(remove):
                sortlist.append(d)
            remove = sortlist
        for item in remove:
            del flood['posts_time'][item]
        if not 'ip_count' in flood:
            flood['ip_count'] = {}
        if ip in flood['ip_count']:
            flood['ip_count'][ip] = int(flood['ip_count'][ip])
            flood['ip_count'][ip] += 1
        else:
            flood['ip_count'][ip] = 1
        ip_count: int = int(flood['ip_count'][ip])
        ip_time: float = 0.0
        if 'ip_time' not in flood:
            flood['ip_time'] = {}
        if ip in flood['ip_time']:
            ip_time = float(flood['ip_time'][ip])
        else:
            flood['ip_time'][ip] = now
            ip_time = now
        if now - ip_time > 60:
            flood['ip_count'][ip] = 1
            flood['ip_time'][ip] = now
            ip_count = 1
        with open(path.join(APP_DIR[0], "flood.json"), 'w') as sfopen:
            sfopen.write(json.dumps(flood))
        if count > 30 or ip_count > 20:
            return redirect(url_for('views.flood'))
        del remove
        del ip_count
        del flood
        del count
        del now
        email: str = request.form.get('email').lower()
        user_name: str = request.form.get('userName').lower()
        password1: str = request.form.get('password1')
        password2: str = request.form.get('password2')

        user_email: User = User.query.filter_by(email=email)
        used_username: User = User.query.filter_by(user_name=user_name).first()
        user_ip: User = User.query.filter_by(ip=ip)

        if user_email.count() > 5:
            flash('email already has the maximum of accounts allowed.', category='error')
        elif user_ip.count() > 4:
            flash('this host address already made 5 accounts.', category='error')
        elif 'admin' in user_name.lower():
            flash('UserName must not contain the word "admin".', category='error')
        elif used_username:
            flash('UserName already exists.', category='error')
        elif len(email) < 4:
            flash('email must be greater than 3 characters long.', category='error')
        elif len(email) > 139:
            flash('email must be shorter than 140 characters long.', category='error')
        elif len(user_name) < 2:
            flash('UserName must be greater than 1 character long.', category='error')
        elif len(user_name) > 39:
            flash('UserName must be less than 40 characters long.', category='error')
        elif password1 != password2:
            flash('Passwords do not match.', category='error')
        elif len(password1) < 6:
            flash('Password must be at least 6 characters long.', category='error')
        elif len(password1) >= 40:
            flash('Password must be less than 40 characters long.', category='error')

        else:
            new_user = User(email=email.lower(), type="normal", user_name=user_name.lower(), ip=ip, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user, remember=True)
            flash('account created! pls remember your Password.', category='success')
            return redirect(url_for('views.bounce'))
    resp = make_response(render_template("sign_up.html", user=current_user))
    no_cache(resp)
    return resp
