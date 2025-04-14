from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from .models import SupportTicket, SupportMessage, Transport, Cargo, TransportStatus
from decimal import Decimal
import json
from django.urls import reverse
from django.utils import timezone

def index(request):
    if not request.session.session_key:
        request.session.create()
    
    transports = Transport.objects.all()
    
    context = {
        'transports': transports,
    }
    return render(request, 'transport/index.html', context)

def transport_detail(request, transport_id):
    transport = get_object_or_404(Transport, id=transport_id)
    cargoes = Cargo.objects.filter(transport=transport)
    status_history = TransportStatus.objects.filter(transport=transport).order_by('-timestamp')[:10]
    
    context = {
        'transport': transport,
        'cargoes': cargoes,
        'status_history': status_history,
    }
    return render(request, 'transport/transport_detail.html', context)

@require_http_methods(["POST"])
def update_transport_status(request, transport_id):
    try:
        transport = get_object_or_404(Transport, id=transport_id)
        new_status = request.POST.get('status')
        new_location = request.POST.get('location')
        comment = request.POST.get('comment', '')

        if new_status not in dict(Transport.STATUS_CHOICES):
            return JsonResponse({'success': False, 'error': 'Неверный статус'}, status=400)

        transport.status = new_status
        transport.current_location = new_location
        transport.save()

        TransportStatus.objects.create(
            transport=transport,
            status=new_status,
            location=new_location,
            comment=comment
        )

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@ensure_csrf_cookie
def support_chat(request):
    current_ticket_id = request.GET.get('ticket_id') or request.session.get('current_ticket_id')
    current_ticket = None
    messages = []
    
    if current_ticket_id:
        try:
            current_ticket = SupportTicket.objects.get(id=current_ticket_id)
            messages = SupportMessage.objects.filter(ticket=current_ticket).order_by('created_at')
        except SupportTicket.DoesNotExist:
            current_ticket_id = None
    
    tickets = SupportTicket.objects.filter(session_id=request.session.session_key).order_by('-created_at')
    
    context = {
        'current_ticket': current_ticket,
        'tickets': tickets,
        'messages': messages
    }
    
    return render(request, 'transport/support_chat.html', context)

@ensure_csrf_cookie
@require_http_methods(["POST"])
def create_ticket(request):
    try:
        data = json.loads(request.body)
        
        if not request.session.session_key:
            request.session.create()
        
        session_id = request.session.session_key
        email = data.get('email')
        subject = data.get('subject')
        message = data.get('message')
        
        if not all([email, subject, message]):
            return JsonResponse({
                'success': False,
                'error': 'Необходимо заполнить email, тему и сообщение'
            }, status=400)
        
        recent_ticket = SupportTicket.objects.filter(
            session_id=session_id,
            email=email,
            subject=subject,
            created_at__gte=timezone.now() - timezone.timedelta(minutes=5)
        ).first()
        
        if recent_ticket:
            return JsonResponse({
                'success': True,
                'ticket_id': recent_ticket.id,
                'redirect_url': reverse('support_chat') + f'?ticket_id={recent_ticket.id}'
            })
        
        ticket = SupportTicket.objects.create(
            session_id=session_id,
            email=email,
            subject=subject,
            status='new'
        )
        
        SupportMessage.objects.create(
            ticket=ticket,
            message=message,
            is_staff=False
        )
        
        request.session['current_ticket_id'] = ticket.id
        
        return JsonResponse({
            'success': True,
            'ticket_id': ticket.id,
            'redirect_url': reverse('support_chat') + f'?ticket_id={ticket.id}'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Неверный формат данных'
        }, status=400)

@ensure_csrf_cookie
@require_POST
def send_message(request, ticket_id):
    try:
        ticket = get_object_or_404(SupportTicket, id=ticket_id)
        data = json.loads(request.body)
        message_text = data.get('message')
        
        if not message_text:
            return JsonResponse({
                'success': False,
                'error': 'Сообщение не может быть пустым'
            }, status=400)
        
        message = SupportMessage.objects.create(
            ticket=ticket,
            message=message_text,
            is_staff=request.user.is_staff if request.user.is_authenticated else False
        )
        
        return JsonResponse({
            'success': True,
            'message': {
                'message': message.message,
                'created_at': message.created_at.strftime('%d.%m.%Y %H:%M'),
                'is_staff': message.is_staff
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Неверный формат данных'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@ensure_csrf_cookie
def support_admin(request):
    current_ticket_id = request.GET.get('ticket_id')
    current_ticket = None
    messages = []
    
    if current_ticket_id:
        try:
            current_ticket = SupportTicket.objects.get(id=current_ticket_id)
            messages = SupportMessage.objects.filter(ticket=current_ticket).order_by('created_at')
        except SupportTicket.DoesNotExist:
            current_ticket_id = None
    
    tickets = SupportTicket.objects.all().order_by('-created_at')
    
    context = {
        'current_ticket': current_ticket,
        'tickets': tickets,
        'messages': messages
    }
    return render(request, 'transport/support_admin.html', context)

@require_http_methods(["POST"])
def admin_send_message(request, ticket_id):
    try:
        ticket = get_object_or_404(SupportTicket, id=ticket_id)
        data = json.loads(request.body)
        message_text = data.get('message')
        new_status = data.get('status')
        
        if not message_text:
            return JsonResponse({
                'success': False,
                'error': 'Сообщение не может быть пустым'
            }, status=400)
        
        message = SupportMessage.objects.create(
            ticket=ticket,
            message=message_text,
            is_staff=True
        )
        
        if new_status and new_status in dict(SupportTicket.STATUS_CHOICES):
            ticket.status = new_status
            ticket.save()
        
        response_data = {
            'success': True,
            'message': {
                'id': message.id,
                'message': message.message,
                'created_at': message.created_at.isoformat(),
                'is_staff': message.is_staff
            }
        }
        
        if new_status:
            response_data['ticket_status'] = ticket.get_status_display()
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@csrf_exempt
def get_ticket_messages(request, ticket_id):
    try:
        ticket = get_object_or_404(SupportTicket, id=ticket_id)
        messages = SupportMessage.objects.filter(ticket=ticket).order_by('created_at')
        
        return JsonResponse({
            'success': True,
            'ticket': {
                'id': ticket.id,
                'subject': ticket.subject,
                'status': ticket.status
            },
            'messages': [{
                'id': msg.id,
                'message': msg.message,
                'is_staff': msg.is_staff,
                'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M:%S')
            } for msg in messages]
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@require_http_methods(["POST"])
def update_ticket_status(request, ticket_id):
    try:
        ticket = get_object_or_404(SupportTicket, id=ticket_id)
        data = json.loads(request.body)
        new_status = data.get('status')
        
        if not new_status or new_status not in dict(SupportTicket.STATUS_CHOICES):
            return JsonResponse({
                'success': False,
                'error': 'Некорректный статус'
            }, status=400)
        
        ticket.status = new_status
        ticket.save()
        
        return JsonResponse({
            'success': True,
            'status': ticket.get_status_display()
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
