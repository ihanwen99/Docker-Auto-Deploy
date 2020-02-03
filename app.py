#!/usr/bin/python
# -*- coding: UTF-8 -*-

from __future__ import unicode_literals

import datetime

from flask import (Flask, render_template, redirect, url_for, request, flash)
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

from Forms import VersionListForm, EnvironmentsListForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hw.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.secret_key = "hw"
db = SQLAlchemy(app)

bootstrap = Bootstrap(app)


class Environments(db.Model):
    __tablename__ = 'environments'
    # primary_key，设置为true，这列就是表对主键
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1024), nullable=False)
    description = db.Column(db.String(1024), nullable=False)
    create_time = db.Column(db.Date, default=datetime.date.today())

    def __init__(self, name, description):
        self.name = name
        self.description = description


class Version(db.Model):
    __tablename__ = 'version'
    # primary_key 版本表的主键
    id = db.Column(db.Integer, primary_key=True)
    # env_id 来自环境的外键，用于搜索
    env_id = db.Column(db.Integer, db.ForeignKey('environments.id'), nullable=False)
    env_version = db.Column(db.String(1024), nullable=False)
    value = db.Column(db.String(1024), nullable=False)
    # nullable，如果设为 True ,这列允许使用空值;如果设为True ,这列允许使用空值
    create_time = db.Column(db.Date, default=datetime.date.today(), nullable=True)

    def __init__(self, env_id, env_version, value):
        self.env_id = env_id
        self.env_version = env_version
        self.value = value


@app.route('/', methods=['GET', 'POST'])
def show_environments_list():
    form = EnvironmentsListForm()
    db.create_all()
    if request.method == 'GET':
        # query.all()返回查询到的所有对象
        envlists = Environments.query.all()
        return render_template('index.html', envlists=envlists, form=form)
    else:
        if form.validate_on_submit():
            envlist = Environments(form.name.data, form.description.data)
            # add()插入数据
            db.session.add(envlist)
            # commit()提交事务
            db.session.commit()
            flash('新环境添加成功')
        else:
            flash(form.errors)
        return redirect(url_for('show_environments_list'))


@app.route('/delete/<int:id>')
def delete_environments_list(id):
    # first_or_404() 返回查询的第一个结果，如果没有结果，则终止请求，返回 404 错误响应
    envlist = Environments.query.filter_by(id=id).first_or_404()
    # delete()删除数据
    db.session.delete(envlist)
    db.session.commit()
    flash('删除环境成功')
    return redirect(url_for('show_environments_list'))


@app.route('/view/<int:env_id>', methods=['GET', 'POST'])
def show_version_list(env_id):
    form = VersionListForm()
    if request.method == 'GET':
        # filter_by() 把等值过滤器添加到原查询上，返回一个新查询
        versionlists = Version.query.filter_by(env_id=env_id).join(Environments, Version.env_id == Environments.id)
        env_out_name = Environments.query.filter_by(id=env_id).first_or_404()
        print(env_out_name.name)
        return render_template('view.html', env_out_name=env_out_name.name, versionlists=versionlists, form=form)
    else:
        if form.validate_on_submit():
            versionlist = Version(env_id, form.env_version.data, form.value.data)
            # add()插入数据
            db.session.add(versionlist)
            # commit()提交事务
            db.session.commit()
            flash('新的版本信息添加成功')
        else:
            flash(form.errors)
        return redirect(url_for('show_version_list', _external=True, env_id=env_id))


@app.route('/change/<int:env_id>/<int:id>', methods=['GET', 'POST'])
def change_version_list(env_id, id):
    if request.method == 'GET':
        versionlists = Version.query.filter_by(env_id=env_id, id=id).join(Environments,
                                                                          Version.env_id == Environments.id).first_or_404()
        form = VersionListForm()
        form.env_version.data = versionlists.env_version
        form.value.data = versionlists.value
        return render_template('modify.html', form=form)
    else:
        form = VersionListForm()
        if form.validate_on_submit():
            versionlists = Version.query.filter_by(env_id=env_id, id=id).join(Environments,
                                                                              Version.env_id == Environments.id).first_or_404()

            versionlists.env_version = form.env_version.data
            versionlists.value = form.value.data
            db.session.add(versionlists)
            db.session.commit()
            flash('修改成功')
        else:
            flash(form.errors)
        return redirect(url_for('show_version_list', _external=True, env_id=env_id))


@app.route('/delete/<int:env_id>/<int:id>')
def delete_version_list(env_id, id):
    # first_or_404() 返回查询的第一个结果，如果没有结果，则终止请求，返回 404 错误响应
    versionlists = Version.query.filter_by(env_id=env_id, id=id).join(Environments,
                                                                      Version.env_id == Environments.id).first_or_404()
    # delete()删除数据
    db.session.delete(versionlists)
    db.session.commit()
    flash('删除成功')
    return redirect(url_for('show_version_list', _external=True, env_id=env_id))


@app.route('/deploy/<int:env_id>/<int:id>')
def deploy(env_id, id):
    versionlists = Version.query.filter_by(env_id=env_id, id=id).join(Environments,
                                                                      Version.env_id == Environments.id).first_or_404()
    print(versionlists.env_version)
    print(env_id)
    print(id)
    
    flash('部署成功')
    return redirect(url_for('show_version_list', _external=True, env_id=env_id))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)
