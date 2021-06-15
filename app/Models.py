from sqlalchemy import Column, Integer, String, Date, Time, Boolean, ForeignKey, Enum,Float,DateTime
from datetime import datetime
from app import db
from sqlalchemy.orm import relationship
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, UserMixin
from enum import Enum as UserEnum


class Base(db.Model):
    __abstract__ = True
    def __str__(self):
        return self.name


class UserRole(UserEnum):
    ADMIN = 1
    STAFF = 2


class Staff(db.Model, UserMixin):
    __tablename__ = 'staff'
    id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(String(50), nullable=False)
    lastname = Column(String(20), nullable=False)
    email = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=False)
    avatar = Column(String(100))
    active = Column(Boolean, default=True)
    joined_date = Column(Date, default=datetime.now())
    user_role = Column(Enum(UserRole), default=UserRole.STAFF)
    account = relationship('Account', backref='staff', lazy=True)
    def __str__(self):
        return str(self.id)


class Account(db.Model, UserMixin):
    __tablename__ = 'account'
    id = Column(Integer, ForeignKey(Staff.id), primary_key=True)
    username = Column(String(20))
    password = Column(String(50))
    ticket = relationship('Ticket', backref='account', lazy=True)
    def __str__(self):
        return str(self.username)


class Customer(Base, UserMixin):
    __tablename__ = 'customer'
    id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(String(50), nullable=False)
    lastname = Column(String(20), nullable=False)
    identity_card = Column(String(20), nullable=False)
    email = Column(String(50))
    phone = Column(String(20), nullable=False)
    ticket = relationship('Ticket', backref = 'customer', lazy = True)
    def __str__(self):
        return str(self.id)


class Plane(Base):
    __tablename__ = 'plane'
    idPlane = Column(Integer, primary_key=True, autoincrement=True)
    schedule = relationship('Schedule', backref='plane', lazy=True)
    seat = relationship('Seat', backref='plane', lazy=True)

    def __str__(self):
        return str(self.idPlane)


class Airport(Base):
    __tablename__ = 'Airport'
    idAirport = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    locate = Column(String (50), nullable=False)


class Schedule(Base):
    __tablename__ = 'Flight Schedule'
    idFlight = Column(Integer, primary_key=True, autoincrement=True)
    departure = Column(Integer, ForeignKey(Airport.idAirport), nullable=False)
    arrival = Column(Integer, ForeignKey(Airport.idAirport), nullable=False)
    intermediate = Column(Integer, ForeignKey(Airport.idAirport))
    departureDate = Column(Date, nullable=False)
    departureTime = Column(Time, nullable=False)
    timeFlight =  Column(Float, nullable=False)
    idPlane = Column(Integer, ForeignKey(Plane.idPlane), nullable=False)
    ticket = relationship('Ticket', backref='schedule', lazy=True)
    departure_fk = relationship('Airport', foreign_keys=[departure])
    arrival_fk = relationship('Airport',  foreign_keys=[arrival])
    intermediate_fk = relationship('Airport',  foreign_keys=[intermediate])

    def __str__(self):
        return str(self.idFlight)


class TypeSeat(Base):
    id = Column(Integer,primary_key=True, autoincrement=True)
    name = Column(String(100),nullable=False)
    price = Column(Float,nullable=False)
    seat = relationship('SeatLocation', backref='typeseat', lazy=True)


class SeatLocation(Base):
    __tablename__ = "seat location"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    seat = relationship('Seat', backref='seatlocation', lazy=True)
    typeSeat = Column(Integer, ForeignKey(TypeSeat.id), nullable=False)


class Seat(db.Model):
    __tablename__ = "seat"
    idSeat = Column(Integer, primary_key=True, autoincrement=True)
    idPlane = Column(Integer, ForeignKey(Plane.idPlane), nullable=False)
    ticket = relationship('Ticket', backref='seat', lazy=True)
    seatLocation = Column(Integer,ForeignKey(SeatLocation.id),nullable=False)

    def __str__(self):
        return str(self.idSeat)


class Ticket(db.Model):
    __tablename__ ="ticket"
    idTicket = Column(Integer,  primary_key=True, autoincrement=True)
    idSeat = Column(Integer,ForeignKey(Seat.idSeat),nullable=False)
    idFlight = Column(Integer, ForeignKey(Schedule.idFlight), nullable= False)
    idCustomer = Column(Integer, ForeignKey(Customer.id))
    idAccount = Column(Integer,ForeignKey(Account.id))
    exportTime = Column(DateTime)
    exportPlace = Column(String(50))
    is_empty = Column(Boolean, default=True)

    def __str__(self):
        return str(self.idTicket)

class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated


if __name__ == "__main__":
    db.create_all()


#Thêm bộ lọc
# class StaffView(ModelView_Base):
#     column_filters = ("firstname", "lastname", "username", "email", "phone", "active", "joined_date")
# class ScheduleView(ModelView_Base):
#     column_filters = ("departure", "arrival", "date", "time")