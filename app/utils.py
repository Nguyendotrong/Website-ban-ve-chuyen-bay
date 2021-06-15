import hashlib
from pprint import pprint
from flask_admin import BaseView, Admin
from sqlalchemy import desc, Date,asc
from sqlalchemy.orm import aliased
from sqlalchemy.sql.functions import count
from app import db
from app.Models import Schedule, Airport, Plane, Seat, Staff, Account, Ticket, SeatLocation, TypeSeat, Customer


class MyView(BaseView):
    def __init__(self, *args, **kwargs):
        self._default_view = True
        super(MyView, self).__init__(*args, **kwargs)
        self.admin = Admin()


# kiểm tra nhân viên đã tồn tại hay chưa
def check_staff(id_staff):
    staff = Staff.query.filter(Staff.id == id_staff).first()
    if staff:
        return True
    return False


# kiểm acount đã tồn tại hay chưa theo id hoặc username
def check_account(key=''):
    if key.isdigit():
        account = Account.query.filter(Account.id == key).first()
    elif key.isalpha():
        account = Account.query.filter(Account.username == key.strip()).first()

    if account:
        return True
    return False


def add_account(id_staff, username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = Account(id=id_staff, username=username, password=password)
    try:
        db.session.add(user)
        db.session.commit()
        return True
    except Exception as ex:
        print(ex)
        return False


def get_account(username, password):
    user = Account.query.join(Staff, Staff.id == Account.id) \
        .filter(Account.username == username, Account.password == password) \
        .add_columns(Account.id, Staff.user_role).first()

    return user


def get_all_schedule():
    airport_1 = aliased (Airport)
    airport_2 = aliased(Airport)
    airport_3 = aliased(Airport)

    schedule = Schedule.query.join(airport_1, Schedule.departure == airport_1.idAirport)\
    .join(airport_2,Schedule.arrival == airport_2.idAirport)\
    .join(Plane, Schedule.idPlane == Plane.idPlane) \
    .join(Ticket, Schedule.idFlight == Ticket.idFlight) \
    .add_columns(Schedule.idFlight,
                     airport_1.name.label("departure_airport"),
                     airport_2.name.label("arrival_airport"),
                     airport_1.locate.label("departure_locate"),
                     airport_2.locate.label("arrival_locate"),
                     Schedule.departureDate.label("departure_date"),
                     Schedule.departureTime.label("departure_time"),
                     Plane.idPlane,
                     Ticket.is_empty,
                     count(Ticket.idTicket).label("empty_seats")) \
    .group_by(Schedule.idFlight)\
    .order_by(desc(Schedule.departureDate)).all()

    return  schedule


def search_schedule (departure_locate, arrival_locate, date = None):
    airport_1 = aliased(Airport)
    airport_2 = aliased(Airport)
    airport_3 = aliased(Airport)
    schedule = []

    if date:
        schedule = Schedule.query.join(airport_1, Schedule.departure == airport_1.idAirport)\
            .join(airport_2,Schedule.arrival == airport_2.idAirport)\
            .join(Plane, Schedule.idPlane == Plane.idPlane)\
            .join(Ticket, Schedule.idFlight == Ticket.idFlight)\
            .filter(airport_1.locate == departure_locate,
                    airport_2.locate == arrival_locate)\
            .add_columns(Schedule.idFlight,
                         airport_1.name.label("departure_airport"),
                         airport_2.name.label("arrival_airport"),
                         airport_1.locate.label("departure_locate"),
                         airport_2.locate.label("arrival_locate"),
                         Schedule.departureDate.label("departure_date"),
                         Schedule.departureTime.label("departure_time"),
                         Ticket.is_empty,
                         Plane.idPlane,
                         count(Ticket.idTicket).label("empty_seats"))\
            .group_by("idFlight")\
            .order_by(desc(Schedule.departureDate)).all()

    return schedule


def get_flight_by_id(idFlight):
    airport_1 = aliased(Airport)
    airport_2 = aliased(Airport)
    airport_3 = aliased(Airport)

    flight = Schedule.query.join(airport_1, Schedule.departure == airport_1.idAirport) \
        .join(airport_2, Schedule.arrival == airport_2.idAirport) \
        .join(Plane, Schedule.idPlane == Plane.idPlane) \
        .join(Ticket, Schedule.idFlight == Ticket.idFlight) \
        .filter(Schedule.idFlight  == idFlight)\
        .add_columns(Schedule.idFlight,
                     airport_1.name.label("departure_airport"),
                     airport_2.name.label("arrival_airport"),
                     airport_1.locate.label("departure_locate"),
                     airport_2.locate.label("arrival_locate"),
                     Schedule.departureDate.label("departure_date"),
                     Schedule.departureTime.label("departure_time"),
                     Plane.idPlane,
                     Ticket.is_empty,
                     count(Ticket.idTicket).label("empty_seats")) \
        .group_by(Schedule.idFlight) \
        .order_by(desc(Schedule.departureDate)).first()

    return flight


def get_all_airport():
    airports = Airport.query.all()
    return airports


def get_seats_by_id_flight(id_flight):
    seats = Ticket.query.join(Seat, Ticket.idSeat == Seat.idSeat)\
                .join(SeatLocation, SeatLocation.id == Seat.seatLocation)\
                .join(Schedule, Schedule.idFlight == Ticket.idFlight)\
                .join(TypeSeat, TypeSeat.id == SeatLocation.typeSeat)\
                .filter(Schedule.idFlight == id_flight)\
                .add_columns(SeatLocation.name.label("seat_location"),
                     TypeSeat.name.label("type_seat"),
                     Ticket.idTicket,
                     Ticket.is_empty

                     )\
                .order_by(asc(SeatLocation.name)).all()

    return seats


def get_id_seat(id_flight, seat_location):
    seat = Seat.query.join(Ticket, Ticket.idSeat == Seat.idSeat) \
        .join(SeatLocation, SeatLocation.id == Seat.seatLocation) \
        .join(Schedule, Schedule.idFlight == Ticket.idFlight) \
        .join(TypeSeat, TypeSeat.id == SeatLocation.typeSeat) \
        .filter(Schedule.idFlight == id_flight, SeatLocation.name == seat_location) \
        .add_columns(SeatLocation.name.label("seat_location"),
                     TypeSeat.name.label("type_seat"),
                     Ticket.idTicket,
                     Ticket.is_empty,
                     Seat.idSeat
                     ) \
        .order_by(asc(SeatLocation.name)).first()

    return seat.idSeat





def update_ticket_for_Staff(id_customer, id_staff, id_seat, id_flight):
    ticket = Ticket.query.filter(Ticket.idSeat == id_seat, Ticket.idFlight == id_flight).first()
    ticket.idCustomer = id_customer
    ticket.idAccount = id_staff
    ticket.is_empty =  False

    try:
        db.session.merge(ticket)
        db.session.flush()
        db.session.commit()
        return True
    except Exception as ex:
        print(ex)
        return False


def update_ticket_for_customer(id_customer, id_seat, id_flight):
    ticket = Ticket.query.filter(Ticket.idSeat == id_seat, Ticket.idFlight == id_flight).first()
    ticket.idCustomer = id_customer

    ticket.is_empty =  False

    try:
        db.session.merge(ticket)
        db.session.flush()
        db.session.commit()
        return True
    except Exception as ex:
        print(ex)
        return False


def add_customer(firstname,lastname,identity_card, phone, email = None):
    if email:
        customer =Customer(firstname=firstname,lastname=lastname,identity_card=identity_card,phone=phone,email=email)
    else:
        customer =Customer(firstname=firstname,lastname=lastname,identity_card=identity_card,phone=phone)

    try:
        db.session.add(customer)
        db.session.commit()
        return True
    except Exception as ex:
        print(ex)
        return False


def get_customer(firstname,lastname,identity_card):
    customer = Customer.query.filter(Customer.firstname == firstname,
                                     Customer.lastname == lastname,
                                     Customer.identity_card == identity_card).first()

    return customer






# def book_ticket(id_flight, seat_location):
#,
# print(count_seat_not_emty(1))
#
#
# print(get_schedule(depature_locate= "Ha Noi", arrival_locate='Binh Thuan', date='2020-12-03'))
# print(get_all_schedule())
# print(get_flight_by_id(1))
# print(get_seats(1))
# update_ticket(id_customer=1, id_staff=2, id_seat=2, id_flight=1)
# print(get_id_seat(1,"A1"))