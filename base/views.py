from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login, logout
from django.contrib.auth.forms import UserCreationForm
# Create your views here.
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains = q) |
        Q(name__icontains = q) |
        Q(description__icontains=q) |
        Q(host__username__icontains=q)
    )
    topics = Topic.objects.all()[0:5]
    rooms_count = rooms.count()
    room_message = Message.objects.filter(Q(room__topic__name__icontains = q))[0:5]
    context = {'rooms':rooms, 'topics':topics, 'rooms_count':rooms_count, 'room_message':room_message}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id = pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()
    if request.method == 'POST':
        comment = Message.objects.create(user=request.user,
                                         room=room,
                                         body = request.POST.get('body'))
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages':room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)

@login_required(login_url='login')
def createRoom(request):
    status = 'create'
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, create = request.POST.get_or_create(name=topic_name)
        room = Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
        )
        return redirect('home')
    context = {'form': form, 'status': status, 'topics': topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    status = 'update'
    room = Room.objects.get(id = pk)
    topics = Topic.objects.all()
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse('Only host can update.')
    
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, create = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('room', room.id)
    context = {'form':form, 'status': status, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    status = 'delete'
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('Only host can delete.')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    context = {'obj': room.name}
    return render(request, 'base/delete.html', context)

def loginPage(request):
    status = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'user does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'user or password does not exist.')
    context = {'status':status}
    return render(request, 'base/login_register.html', context)

def logoutPage(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    status = 'register'
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration.')
    context = {'status':status, 'form':form}
    return render(request, 'base/login_register.html', context)

@login_required(login_url='login')
def deleteComment(request, pk):
    status = 'delete'
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('This is not your comment.')
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    context = {'obj': message}
    return render(request, 'base/delete.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_message = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user, 'rooms':rooms, 'room_message': room_message, 'topics':topics}
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk = user.id)
    context = {'form': form}
    return render(request, 'base/update-user.html', context)

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(Q(name__icontains = q))
    context = {'topics':topics}
    return render(request, 'base/topics.html', context)

def activityPage(request):
    room_message = Message.objects.all()
    context = {'room_message': room_message}
    return render(request, 'base/activity.html', context)