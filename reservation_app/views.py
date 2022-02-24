from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from reservation_app.models import Room, Reservation
from datetime import date, datetime
from django.db import IntegrityError


def parse_date(s):
    # return datetime.strptime(s, "%d.%m.%Y").date()
    return datetime.strptime(s, "%Y-%m-%d").date()


# making validations
def check_exceptions(request):
    if len(request.POST.get('room-name')) < 1:
        return render(request, "add-room.html",
                      {'error': "Nazwa sali musi być dłuższa nić 1 znak"})
    elif Room.objects.filter(name=request.POST.get('room-name')):
        return render(request, "add-room.html",
                      {'error': "Sala o tej nazwie już istnieje"})
    elif int(request.POST.get('capacity')) < 0:
        return render(request, "add-room.html",
                      {'error': "Pojemność sali nie może być ujemna"})
    elif int(request.POST.get('capacity')) == 0:
        return render(request, 'edit-room.html',
                      {'error': 'Pojemność musi być większa od 0'})
    elif not request.POST.get('room-name'):
        return render(request, 'edit-room.html',
                      {'error': 'Proszę podać nazwę sali'})
    elif Room.objects.filter(name=request.POST.get('room-name')):
        return render(request, 'edit-room.html',
                      {'error': 'Sala o tej nazwie już istnieje'})


# adding room
class AddRoom(View):

    def get(self, request):
        return render(request, "add-room.html")

    def post(self, request):
        if check_exceptions(request):
            return check_exceptions(request)
        else:
            Room.objects.create(name=request.POST.get('room-name'),
                                capacity=request.POST.get('capacity'),
                                projector=request.POST.get('projector') == 'on')

        return redirect("room-list")


# showing rooms
class RoomList(View):

    def get(self, request):
        rooms = list(Room.objects.all())
        for room in rooms:
            reservation_dates = [reservation.date for reservation in room.reservation_set.all()]
            room.reserved = date.today() in reservation_dates
        return render(request, "room-list.html", {'rooms': rooms})


# deleting room
class DeleteRoom(View):

    def get(self, request, room_id):
        Room.objects.filter(pk=room_id).delete()
        return redirect('room-list')


# editing room
class EditRoom(View):
    def get(self, request, room_id):
        room = get_object_or_404(Room, pk=room_id)
        return render(request, 'edit-room.html', {'room': room})

    def post(self, request, room_id):
        if check_exceptions(request):
            return check_exceptions(request)
        else:
            room = get_object_or_404(Room, pk=room_id)
            room.name = request.POST.get('room-name')
            room.capacity = request.POST.get('capacity')
            room.projector = request.POST.get('projector') == 'on'
            room.save()
            # Room.objects.create(name=request.POST.get('room-name'),
            #                     capacity=request.POST.get('capacity'),
            #                     projector=request.POST.get('projector') == 'on')
        return redirect("room-list")


# creating view for reservation and making validation for reservation possibility
class ReservationView(View):

    def get(self, request, room_id):
        room = get_object_or_404(Room, pk=room_id)
        reservations = room.reservation_set.filter(date__gte=date.today()).order_by('date')
        return render(request, 'reservation.html', {'room': room,
                                                    'reservations': reservations})

    def post(self, request, room_id):
        room = get_object_or_404(Room, pk=room_id)
        try:
            reservation_date = parse_date(request.POST.get('reservation-date'))
            print('==================')
            print(reservation_date)
        except (ValueError, KeyError):
            return render(request, "reservation.html", {'error': "Wymagana data rezerwacji"})
        if Reservation.objects.filter(room_id=room_id, date=request.POST.get('reservation-date')):
            return render(request, 'reservation.html',
                          {'error': 'Rezerwacja dla tego terminu oraz pokoju już istnieje'})
        elif reservation_date < date.today():
            return render(request, 'reservation.html', {'error': 'Nie prawidłowa data'})
        else:
            try:
                Reservation.objects.create(date=reservation_date,
                                           comment=request.POST.get('comment'),
                                           room=room)
            except IntegrityError:
                return render(request, 'reservation.html',
                              {'error': 'Ktoś cię ubiegł termin zarezerwowany'})

            return redirect('room-list')


# showing information about room
class RoomDetails(View):
    def get(self, request, room_id):
        room = get_object_or_404(Room, pk=room_id)
        reservations = Reservation.objects.filter(room_id=room_id).order_by('date')
        return render(request, 'room-details.html', {'room': room,
                                                     'reservations': reservations})
