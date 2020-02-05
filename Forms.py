# -*- coding: utf-8 -*-
# @Time    : 2019/12/20
# @Author  : Liu Hanwen
# @File    : Forms.py

from __future__ import unicode_literals
from flask_wtf import FlaskForm

from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired, Length


class VersionListForm(FlaskForm):
    env_version = StringField('环境版本', validators=[DataRequired(), Length(1, 64)])
    docker_name=StringField('Docker名', validators=[DataRequired(), Length(1, 64)])
    value = StringField('环境备注', validators=[DataRequired(), Length(1, 64)])
    submit = SubmitField('提交')


class EnvironmentsListForm(FlaskForm):
    name = StringField('环境', validators=[DataRequired(), Length(1, 64)])
    description = StringField('描述', validators=[DataRequired(), Length(1, 64)])
    submit = SubmitField('提交')
