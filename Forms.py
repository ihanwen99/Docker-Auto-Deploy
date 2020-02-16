# -*- coding: utf-8 -*-
# @Time    : 2019/12/20
# @Author  : Liu Hanwen
# @File    : Forms.py

from __future__ import unicode_literals
from flask_wtf import FlaskForm

from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired, Length


class VersionListForm(FlaskForm):
    env_version = StringField('Image Name', validators=[DataRequired(), Length(1, 64)])
    docker_name=StringField('Docker Name', validators=[DataRequired(), Length(1, 64)])
    extra_code=StringField('Extra Config', validators=[Length(0, 64)])
    value = StringField('Description', validators=[Length(0, 64)])
    submit = SubmitField('Submit')


class EnvironmentsListForm(FlaskForm):
    name = StringField('Image Name', validators=[DataRequired(), Length(1, 64)])
    description = StringField('Description', validators=[DataRequired(), Length(1, 64)])
    submit = SubmitField('Submit')
