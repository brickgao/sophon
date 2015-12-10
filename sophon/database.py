#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sophon.config import SQLALCHEMY_DATABASE_URI

engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
db_session = sessionmaker(bind=engine)
session = db_session()
BaseModel = declarative_base()

def init_db():
    BaseModel.metadata.create_all(bind=engine)

def drop_db():
    BaseModel.metadata.drop_all(bind=engine)

from sophon.models import UserMeta  # pylint: disable=unused-import
