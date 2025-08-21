from enum import StrEnum
from datetime import datetime
from datetime import time
from typing import Set
from app import db
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Float
from sqlalchemy import Date
from sqlalchemy import Time
from sqlalchemy import Table
from sqlalchemy import Integer
from sqlalchemy import Boolean
from sqlalchemy import LargeBinary
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id: Mapped[str] = mapped_column(db.String, primary_key=True)
    password: Mapped[LargeBinary] = mapped_column(db.LargeBinary)
    events: Mapped[Set['Event']] = relationship("Event")
    tasks: Mapped[Set['Task']] = relationship("Task")


class CalendarObjectType(StrEnum):
    event = 'event'
    task = 'task'


class CalendarObject(db.Model):
    id: Mapped[str] = mapped_column(db.String, primary_key=True)
    type: Mapped[CalendarObjectType] = mapped_column(
        db.Enum(CalendarObjectType)
        )
    title: Mapped[str] = mapped_column(db.String)
    date: Mapped[Date] = mapped_column(db.Date)
    start_time: Mapped[DateTime] = mapped_column(db.DateTime)
    notes: Mapped[str] = mapped_column(db.String, nullable=True)
    user_id: Mapped[str] = mapped_column(db.String, ForeignKey(User.id))
    __mapper_arguments = {
        'polymorphic_identity': 'calendarObject',
        'polymorphic_on': 'type'
    }


class Event(CalendarObject):
    id: Mapped[str] = mapped_column(ForeignKey(CalendarObject.id),
                                    primary_key=True
                                    )
    end_time: Mapped[DateTime] = mapped_column(db.DateTime)
    __mapper_arguments__ = {'polymorphic_identity': 'event'}


class Task(CalendarObject):
    id: Mapped[str] = mapped_column(ForeignKey(CalendarObject.id),
                                    primary_key=True
                                    )
    # completion separates 'events' from 'tasks'
    is_complete: Mapped[bool] = mapped_column(db.Boolean)
    __mapper_arguments__ = {'polymorphic_identity': 'task'}
