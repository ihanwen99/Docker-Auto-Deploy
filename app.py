#!/usr/bin/python
# -*- coding: UTF-8 -*-

from __future__ import unicode_literals

import datetime
import os
import re

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
    docker_name = db.Column(db.String(1024), nullable=False)
    extra_code = db.Column(db.String(1024), nullable=True)
    value = db.Column(db.String(1024), nullable=True)
    # nullable，如果设为 True ,这列允许使用空值;如果设为True ,这列允许使用空值
    create_time = db.Column(db.Date, default=datetime.date.today(), nullable=True)

    def __init__(self, env_id, env_version,docker_name, extra_code,value):
        self.env_id = env_id
        self.env_version = env_version
        self.docker_name=docker_name
        self.extra_code=extra_code
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
            flash("Add Env Successfully.")
        else:
            flash(form.errors)
        return redirect(url_for('show_environments_list'))

@app.route('/docker', methods=['GET', 'POST'])
def show_docker_ps_a():
    if request.method == 'GET':
        # docker_ps获取全部container
        # 传入信息，渲染docekr.html
        docker_command="docker ps -a"
        print(docker_command)
        #print(os.popen(docker_command)) #<open file 'docker ps -a', mode 'r' at 0x7f456d2e6150> 
        #print(type(os.popen(docker_command))) #<type 'file'> 
        result=os.popen(docker_command)
        # res=result.read()
        # for line in res.splitlines():
        #     print(line)
        #     print(type(line))
        docker_count=0
        docker_container_list=[]    
        for line in result:
            line_split_ago=line.strip().split('ago')
            if docker_count==0:
                docker_count+=1
                continue
            docker_container_single={}

            line1=line_split_ago[0].split()
            docker_container_single['CONTAINER_ID']=line1[0]
            docker_container_single['IMAGE']=line1[1]
            docker_container_single['COMMAND']=line1[2]
            docker_container_single['CREATED']=' '.join(line1[3:])+' ago'
            #print(docker_container_single['CREATED'])

            line2=line_split_ago[1]
            spanList=['second','seconds','minute','minutes','hour','hours']
            for word in spanList:
                searchResult=re.search(word, line2)
                if searchResult:
                    start,end=searchResult.span()
            docker_container_single['STATUS']=line2[:end]

            line3=line2[end:].split()

            docker_container_single['PORTS']=' '.join(line3[:-1]) if line3[:-1]!=[] else ' '
            docker_container_single['NAMES']=line3[-1]

            
            # print(docker_container_single['STATUS'])
            # print(docker_container_single['PORTS'])
            # print(docker_container_single['NAMES'])
            docker_container_list.append(docker_container_single)

        return render_template('docker.html',containerList=docker_container_list)


@app.route('/delete/<int:id>')
def delete_environments_list(id):
    # first_or_404() 返回查询的第一个结果，如果没有结果，则终止请求，返回 404 错误响应
    envlist = Environments.query.filter_by(id=id).first_or_404()
    verlist = Version.query.filter_by(env_id=id).all()
    print(envlist)
    print(verlist)
    # delete()删除数据
    for version in verlist:      
        delete_version_list(version.env_id,version.id)
        db.session.delete(version)
    db.session.delete(envlist)

    db.session.commit()
    flash('Delete Env Successfully.')
    return redirect(url_for('show_environments_list'))


@app.route('/view/<int:env_id>', methods=['GET', 'POST'])
def show_version_list(env_id):
    form = VersionListForm()
    if request.method == 'GET':
        # filter_by() 把等值过滤器添加到原查询上，返回一个新查询
        versionlists = Version.query.filter_by(env_id=env_id).join(Environments, Version.env_id == Environments.id)
        env_out_name = Environments.query.filter_by(id=env_id).first_or_404()
        return render_template('view.html', env_out_name=env_out_name.name, versionlists=versionlists, form=form)
    else:
        if form.validate_on_submit():
            versionlist = Version(env_id, form.env_version.data, form.docker_name.data,form.extra_code.data,form.value.data)
            # add()插入数据
            db.session.add(versionlist)
            # commit()提交事务
            db.session.commit()
            flash('Add New Version Successfully')
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
        form.docker_name.data=versionlists.docker_name
        form.extra_code.data=versionlists.extra_code
        form.value.data = versionlists.value
        return render_template('modify.html', form=form)
    else:
        form = VersionListForm()
        if form.validate_on_submit():
            versionlists = Version.query.filter_by(env_id=env_id, id=id).join(Environments,
                                                                              Version.env_id == Environments.id).first_or_404()

            versionlists.env_version = form.env_version.data
            versionlists.docker_name=form.docker_name.data
            versionlists.extra_code=form.extra_code.data
            versionlists.value = form.value.data
            db.session.add(versionlists)
            db.session.commit()
            flash('Modify Successfully')
        else:
            flash(form.errors)
        return redirect(url_for('show_version_list', _external=True, env_id=env_id))


@app.route('/delete/<int:env_id>/<int:id>')
def delete_version_list(env_id, id):
    # first_or_404() 返回查询的第一个结果，如果没有结果，则终止请求，返回 404 错误响应
    versionlists = Version.query.filter_by(env_id=env_id, id=id).join(Environments,
                                                                      Version.env_id == Environments.id).first_or_404()
    env_out_name = (Environments.query.filter_by(id=env_id).first_or_404()).name
    env_name=str(env_out_name).lower()
    print(env_name) #ubuntu
    print(env_name.split('/')[-1])
    #print(versionlists.env_version) #14.04
    #print(versionlists.docker_name) # hw

    docker_env_name=env_name.split('/')[-1]+'_'+versionlists.env_version+'_'+versionlists.docker_name # ubuntu_14.04_hw

    command1="docker stop {}".format(docker_env_name)
    command2="docker rm {}".format(docker_env_name)

    print(command1)
    print(command2)
    os.system(command1)
    os.system(command2)

    # delete()删除数据
    db.session.delete(versionlists)
    db.session.commit()
    flash('Delete Version Successfully')
    return redirect(url_for('show_version_list', _external=True, env_id=env_id))

@app.route('/delete/<string:docker_string_name>')
def delete_docker_container(docker_string_name):
    
    command1="docker stop {}".format(docker_string_name)
    command2="docker rm {}".format(docker_string_name)

    print(command1)
    os.system(command1)
    
    print(command2)
    os.system(command2)

    flash('Delete Version Successfully')
    return redirect(url_for('show_docker_ps_a'))



@app.route('/deploy/<int:env_id>/<int:id>')
def deploy(env_id, id):
    versionlists = Version.query.filter_by(env_id=env_id, id=id).join(Environments,
                                                                      Version.env_id == Environments.id).first_or_404()
    env_out_name = (Environments.query.filter_by(id=env_id).first_or_404()).name
    env_name=str(env_out_name).lower()
    print(env_name) #ubuntu
    print(env_name.split('/')[-1])
    #print(versionlists.env_version) #14.04
    #print(versionlists.docker_name) # hw
    print(versionlists.extra_code)
    docker_env_name=env_name.split('/')[-1]+'_'+versionlists.env_version+'_'+versionlists.docker_name # ubuntu_14.04_hw
    

    command="docker run -itd --name {} {} {}:{} ".format(docker_env_name, versionlists.extra_code, env_name,versionlists.env_version)
    print(command)
    os.system(command)


    flash('Deploy Successfully')
    return redirect(url_for('show_docker_ps_a', _external=True, env_id=env_id))





@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


if __name__ == '__main__':
    #app.run(host='127.0.0.1', port=5001, debug=True)
    app.run(host='0.0.0.0', port=5001, debug=True)
