"""
وحدات العرض لتطبيق العقارات
يحتوي على جميع وحدات العرض المتعلقة بالعقارات وإدارتها
"""

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from functools import wraps
from .models import Property, PropertyRequest, PropertyImage, PropertyLike, PropertyComment, UserFollow, Chat, Message, CommentLike
from .forms import PropertyForm, PropertyRequestForm

def login_required_with_message(view_func):
    """
    دالة لتحقق من تسجيل الدخول مع رسالة
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'يرجى تسجيل الدخول أو إنشاء حساب للمتابعة')
            return redirect(f"{reverse('accounts:login')}?next={request.path}")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def home(request):
    """
    الصفحة الرئيسية
    """
    pass
    # properties = Property.objects.all().order_by('-created_at')
    # return render(request, 'properties/home.html', {'properties': properties})

def property_list(request):
    """
    قائمة العقارات
    يعرض جميع العقارات المتاحة مع إمكانية التصفية والبحث
    """
    properties = Property.objects.all()
    # Order by newest first
    properties = properties.order_by('-created_at')
    
    # تحميل التعليقات مع العقارات
    properties = properties.prefetch_related(
        'comments',
        'comments__user',
        'comments__user__profile'
    )

    context = {
        'properties': properties,
        'title': 'قائمة العقارات'
    }
    
    return render(request, 'properties/property_list.html', context)

def property_detail(request, pk):
    """
    عرض تفاصيل العقار
    يعرض جميع تفاصيل العقار مع الصور والتعليقات
    """
    property = get_object_or_404(Property, pk=pk)
    comments = property.comments.all().order_by('-created_at')
    return render(request, 'properties/property_detail.html', {
        'property': property,
        'comments': comments,
    })

@login_required_with_message
def create_property(request):
    """
    إنشاء عقار جديد
    يتيح للمستخدم إضافة عقار جديد مع الصور والتفاصيل
    """
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property = form.save(commit=False)
            property.owner = request.user
            property.save()
            
            # Handle image upload
            if request.FILES.get('images'):
                image = request.FILES['images']
                PropertyImage.objects.create(
                    property=property,
                    image=image,
                    is_primary=True
                )
            
            messages.success(request, 'تم إضافة العقار بنجاح!')
            return redirect('properties:property_detail', pk=property.pk)
    else:
        form = PropertyForm()
    
    return render(request, 'properties/property_form.html', {
        'form': form,
        'title': 'إضافة عقار جديد'
    })

@login_required_with_message
def edit_property(request, pk):
    """
    تحديث بيانات العقار
    يتيح لمالك العقار تعديل بياناته وصوره
    """
    property = get_object_or_404(Property, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=property)
        images = request.FILES.getlist('images')
        
        if form.is_valid():
            property = form.save()
            
            for image in images:
                PropertyImage.objects.create(
                    property=property,
                    image=image,
                    is_primary=not PropertyImage.objects.filter(property=property).exists()
                )
            
            messages.success(request, 'تم تحديث العقار بنجاح.')
            return redirect('properties:property_detail', pk=property.pk)
    else:
        form = PropertyForm(instance=property)
    
    return render(request, 'properties/property_form.html', {
        'form': form,
        'property': property
    })

@login_required_with_message
def delete_property(request, pk):
    """
    حذف العقار
    يتيح لمالك العقار حذفه نهائياً
    """
    property = get_object_or_404(Property, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        property.delete()
        messages.success(request, 'تم حذف العقار بنجاح.')
    return redirect('properties:property_list')
    
    # return render(request, 'properties/property_confirm_delete.html', {'property': property})


@login_required_with_message
def create_request(request, property_id):
    """
    إنشاء طلب جديد
    يتيح للمستخدم إرسال طلب للاطلاع على العقار
    """
    property = get_object_or_404(Property, id=property_id)
    
    if request.method == 'POST':
        form = PropertyRequestForm(request.POST)
        if form.is_valid():
            property_request = form.save(commit=False)
            property_request.user = request.user
            property_request.property = property
            property_request.save()
            messages.success(request, 'تم إرسال طلبك بنجاح.')
            return redirect('properties:request_detail', pk=property_request.pk)
    else:
        initial_data = {
            'property': property,
            'property_type': property.property_type,
            'listing_type': property.listing_type,
        }
        form = PropertyRequestForm(initial=initial_data)
    
    return render(request, 'properties/request_form.html', {
        'form': form,
        'property': property
    })

@login_required_with_message
def edit_request(request, pk):
    """
    تحديث الطلب
    يتيح للمستخدم تعديل طلبه
    """
    property_request = get_object_or_404(PropertyRequest, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = PropertyRequestForm(request.POST, instance=property_request)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الطلب بنجاح.')
            return redirect('properties:request_detail', pk=property_request.pk)
    else:
        form = PropertyRequestForm(instance=property_request)
    
    return render(request, 'properties/request_form.html', {'form': form})

@login_required_with_message
def delete_request(request, pk):
    """
    حذف الطلب
    يتيح للمستخدم حذف طلبه
    """
    property_request = get_object_or_404(PropertyRequest, pk=pk, user=request.user)
    
    if request.method == 'POST':
        property_request.delete()
        messages.success(request, 'تم حذف الطلب بنجاح.')
        return redirect('properties:my_requests')
    
    return render(request, 'properties/request_confirm_delete.html', {'property_request': property_request})

@login_required_with_message
def request_detail(request, pk):
    """
    عرض تفاصيل الطلب
    يعرض جميع تفاصيل الطلب
    """
    property_request = get_object_or_404(PropertyRequest, pk=pk)
    return render(request, 'properties/request_detail.html', {'property_request': property_request})

@login_required_with_message
def my_properties(request):
    """
    عقاراتي
    يعرض جميع العقارات التي يملكها المستخدم
    """
    properties = Property.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'properties/my_properties.html', {'properties': properties})

@login_required_with_message
def my_requests(request):
    """
    طلباتي
    يعرض جميع الطلبات التي أرسلها المستخدم
    """
    requests = PropertyRequest.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'properties/my_requests.html', {'requests': requests})

@login_required_with_message
def matching_properties(request, pk):
    """
    العقارات المطابقة
    يعرض جميع العقارات التي تتوافق مع الطلب
    """
    property_request = get_object_or_404(PropertyRequest, pk=pk, user=request.user)
    
    # البحث عن العقارات المطابقة
    matching_properties = Property.objects.filter(
        property_type=property_request.property_type,
        listing_type=property_request.listing_type,
        price__lte=property_request.max_price,
        area__gte=property_request.min_area,
        is_available=True
    )

    if property_request.bedrooms:
        matching_properties = matching_properties.filter(bedrooms=property_request.bedrooms)

    return render(request, 'properties/matching_properties.html', {
        'property_request': property_request,
        'matching_properties': matching_properties
    })

def search_properties(request):
    """
    البحث عن العقارات
    يتيح للمستخدمين البحث عن العقارات حسب معايير مختلفة
    """
    query = request.GET.get('q')
    property_type = request.GET.get('property_type')
    listing_type = request.GET.get('listing_type')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    min_area = request.GET.get('min_area')
    max_area = request.GET.get('max_area')
    bedrooms = request.GET.get('bedrooms')
    bathrooms = request.GET.get('bathrooms')
    location = request.GET.get('location')
    
    properties = Property.objects.all()
    
    if query:
        properties = properties.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query) |
            Q(address__icontains=query)
        )
    
    if property_type:
        properties = properties.filter(property_type=property_type)
    
    if listing_type:
        properties = properties.filter(listing_type=listing_type)
    
    if min_price:
        properties = properties.filter(price__gte=min_price)
    
    if max_price:
        properties = properties.filter(price__lte=max_price)
    
    if min_area:
        properties = properties.filter(area__gte=min_area)
    
    if max_area:
        properties = properties.filter(area__lte=max_area)
    
    if bedrooms:
        properties = properties.filter(bedrooms=bedrooms)
    
    if bathrooms:
        properties = properties.filter(bathrooms=bathrooms)
    
    if location:
        properties = properties.filter(location__icontains=location)
    
    return render(request, 'properties/search_results.html', {'properties': properties})


@login_required_with_message
def add_comment(request, pk):
    """
    إضافة تعليق
    يتيح للمستخدم إضافة تعليق على العقار
    """
    if request.method == 'POST':
        try:
            property = get_object_or_404(Property, pk=pk)
            content = request.POST.get('content')
            
            if not content:
                return JsonResponse({'status': 'error', 'message': 'المحتوى مطلوب'}, status=400)
            
            comment = PropertyComment.objects.create(
                user=request.user,
                property=property,
                content=content
            )
            
            # إنشاء إشعار للمالك
            if request.user != property.owner:
                try:
                    from notifications.models import Notification
                    from django.contrib.contenttypes.models import ContentType
                    from channels.layers import get_channel_layer
                    from asgiref.sync import async_to_sync
                    import json
                    
                    notification = Notification.objects.create(
                        recipient=property.owner,
                        sender=request.user,
                        notification_type='comment',
                        content_type=ContentType.objects.get_for_model(PropertyComment),
                        object_id=comment.id,
                        text=f"علق {request.user.get_full_name() or request.user.username} على عقارك: {property.title}"
                    )
                    
                    # إرسال الإشعار عبر WebSocket
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f'notifications_{property.owner.id}',
                        {
                            'type': 'send_notification',
                            'notification': {
                                'id': notification.id,
                                'text': notification.text,
                                'type': notification.notification_type,
                                'sender': {
                                    'username': request.user.username,
                                    'name': request.user.get_full_name() or request.user.username,
                                    'profile_picture_url': request.user.profile.profile_picture.url if hasattr(request.user, 'profile') and request.user.profile.profile_picture else None
                                },
                                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S')
                            }
                        }
                    )
                except Exception as e:
                    print(f"Error creating notification: {str(e)}")
            
            from django.http import JsonResponse
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'comment': {
                        'id': comment.id,
                        'user': request.user.username,
                        'content': comment.content,
                        'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'profile_picture_url': request.user.profile.profile_picture.url if hasattr(request.user, 'profile') and request.user.profile.profile_picture else None
                    }
                })
            
            return redirect('properties:property_detail', pk=pk)
            
        except Exception as e:
            print(f"Error in add_comment: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'طريقة غير مسموح بها'}, status=405)

@login_required_with_message
def like_property(request, pk):
    """
    الإعجاب بالعقار
    يتيح للمستخدم الإعجاب بالعقار
    """
    if request.method == 'POST':
        try:
            property = get_object_or_404(Property, pk=pk)
            user = request.user
            is_liked = property.liked_by.filter(id=user.id).exists()

            if is_liked:
                property.liked_by.remove(user)
                liked = False
            else:
                property.liked_by.add(user)
                liked = True
                
                # إنشاء إشعار للمالك عند الإعجاب
                if user != property.owner:
                    try:
                        from notifications.models import Notification
                        from django.contrib.contenttypes.models import ContentType
                        from channels.layers import get_channel_layer
                        from asgiref.sync import async_to_sync
                        
                        notification = Notification.objects.create(
                            recipient=property.owner,
                            sender=user,
                            notification_type='like',
                            content_type=ContentType.objects.get_for_model(Property),
                            object_id=property.id,
                            text=f"أعجب {user.get_full_name() or user.username} بعقارك: {property.title}"
                        )
                        
                        # إرسال الإشعار عبر WebSocket
                        channel_layer = get_channel_layer()
                        async_to_sync(channel_layer.group_send)(
                            f'notifications_{property.owner.id}',
                            {
                                'type': 'send_notification',
                                'notification': {
                                    'id': notification.id,
                                    'text': notification.text,
                                    'type': notification.notification_type,
                                    'sender': {
                                        'username': user.username,
                                        'name': user.get_full_name() or user.username,
                                        'profile_picture_url': user.profile.profile_picture.url if hasattr(user, 'profile') and user.profile.profile_picture else None
                                    },
                                    'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S')
                                }
                            }
                        )
                    except Exception as e:
                        print(f"Error creating notification: {str(e)}")

            return JsonResponse({
                'status': 'success',
                'liked': liked,
                'likes_count': property.liked_by.count()
            })
        except Exception as e:
            print(f"Error in like_property: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'طريقة غير مسموح بها'}, status=405)

@login_required_with_message
def follow_user(request, username):
    """
    متابعة المستخدم
    يتيح للمستخدم متابعة مستخدم آخر
    """
    user_to_follow = get_object_or_404(User, username=username)
    if user_to_follow == request.user:
        return JsonResponse({'status': 'error', 'message': 'لا يمكنك متابعة نفسك'}, status=400)
    
    follow, created = UserFollow.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )
    if not created:
        follow.delete()
        return JsonResponse({
            'status': 'unfollowed',
            'count': user_to_follow.followers.count()
        })
    return JsonResponse({
        'status': 'followed',
        'count': user_to_follow.followers.count()
    })

@login_required_with_message
def chat_list(request):
    """
    قائمة المحادثات
    يعرض جميع المحادثات للمستخدم
    """
    chats = Chat.objects.filter(participants=request.user)
    return render(request, 'properties/chat_list.html', {'chats': chats})

@login_required_with_message
def chat_detail(request, chat_id):
    """
    تفاصيل المحادثة
    يعرض جميع تفاصيل المحادثة
    """
    chat = get_object_or_404(Chat, id=chat_id, participants=request.user)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            message = Message.objects.create(
                chat=chat,
                sender=request.user,
                content=content
            )
            return JsonResponse({
                'status': 'success',
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'sender': message.sender.get_full_name() or message.sender.username,
                    'created_at': message.created_at.strftime('%Y/%m/%d %I:%M %p')
                }
            })
    messages = chat.messages.all()
    return render(request, 'properties/chat_detail.html', {
        'chat': chat,
        'messages': messages
    })

@login_required_with_message
def start_chat(request, username):
    """
    بدء محادثة جديدة
    يتيح للمستخدم بدء محادثة جديدة مع مستخدم آخر
    """
    other_user = get_object_or_404(User, username=username)
    if other_user == request.user:
        return JsonResponse({'status': 'error', 'message': 'لا يمكنك بدء محادثة مع نفسك'}, status=400)
    
    # البحث عن محادثة موجودة أو إنشاء واحدة جديدة
    chat = Chat.objects.filter(participants=request.user).filter(participants=other_user).first()
    if not chat:
        chat = Chat.objects.create()
        chat.participants.add(request.user, other_user)
    
    return redirect('properties:chat_detail', chat_id=chat.id)

@login_required_with_message
def like_comment(request, comment_id):
    """
    الإعجاب بالتعليق
    يتيح للمستخدم الإعجاب بالتعليق
    """
    if request.method == 'POST':
        try:
            comment = get_object_or_404(PropertyComment, id=comment_id)
            user = request.user
            
            if CommentLike.objects.filter(comment=comment, user=user).exists():
                CommentLike.objects.filter(comment=comment, user=user).delete()
                liked = False
            else:
                CommentLike.objects.create(comment=comment, user=user)
                liked = True
                
                # إنشاء إشعار لصاحب التعليق
                if user != comment.user:
                    try:
                        from notifications.models import Notification
                        from django.contrib.contenttypes.models import ContentType
                        from channels.layers import get_channel_layer
                        from asgiref.sync import async_to_sync
                        
                        notification = Notification.objects.create(
                            recipient=comment.user,
                            sender=user,
                            notification_type='comment_like',
                            content_type=ContentType.objects.get_for_model(PropertyComment),
                            object_id=comment.id,
                            text=f"أعجب {user.get_full_name() or user.username} بتعليقك على العقار: {comment.property.title}"
                        )
                        
                        # إرسال الإشعار عبر WebSocket
                        channel_layer = get_channel_layer()
                        async_to_sync(channel_layer.group_send)(
                            f'notifications_{comment.user.id}',
                            {
                                'type': 'send_notification',
                                'notification': {
                                    'id': notification.id,
                                    'text': notification.text,
                                    'type': notification.notification_type,
                                    'sender': {
                                        'username': user.username,
                                        'name': user.get_full_name() or user.username,
                                        'profile_picture_url': user.profile.profile_picture.url if hasattr(user, 'profile') and user.profile.profile_picture else None
                                    },
                                    'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S')
                                }
                            }
                        )
                    except Exception as e:
                       print(f"Error creating notification: {str(e)}")
            a=CommentLike.objects.filter(comment=comment).count()
            print(a)
            return JsonResponse({
                'status': 'success',
                'liked': liked,
                'likes_count': CommentLike.objects.filter(comment=comment).count()
            })
        except Exception as e:
            print(f"Error in like_comment: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'طريقة غير مسموح بها'}, status=405)

@login_required_with_message
def reply_to_comment(request, comment_id):
    """
    الرد على التعليق
    يتيح للمستخدم الرد على التعليق
    """
    if request.method == 'POST':
        try:
            parent_comment = get_object_or_404(PropertyComment, id=comment_id)
            content = request.POST.get('content')
            
            if not content:
                return JsonResponse({'status': 'error', 'message': 'Content is required'}, status=400)
                
            reply = PropertyComment.objects.create(
                user=request.user,
                property=parent_comment.property,
                content=content,
                parent=parent_comment
            )
            
            # إنشاء إشعار للمستخدم صاحب التعليق الأصلي
            if request.user != parent_comment.user:
                from notifications.models import Notification
                notification = Notification.objects.create(
                    recipient=parent_comment.user,
                    sender=request.user,
                    notification_type='comment_reply',
                    content_object=reply,
                    text=f'رد {request.user.get_full_name() or request.user.username} على تعليقك'
                )
                
                # إرسال الإشعار عبر WebSocket
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'notifications_{parent_comment.user.id}',
                    {
                        'type': 'send_notification',
                        'notification': {
                            'id': notification.id,
                            'text': notification.text,
                            'type': notification.notification_type,
                            'sender': {
                                'name': request.user.get_full_name() or request.user.username,
                                'avatar': request.user.profile.avatar_url if hasattr(request.user, 'profile') else None,
                            },
                            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S')
                        }
                    }
                )

            return JsonResponse({
                'status': 'success',
                'reply': {
                    'id': reply.id,
                    'content': reply.content,
                    'user': {
                        'username': reply.user.username,
                        'name': reply.user.get_full_name() or reply.user.username,
                        'profile_picture_url': reply.user.profile.avatar_url if hasattr(reply.user, 'profile') else None,
                    },
                    'created_at': reply.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@login_required_with_message
def comment_delete(request, pk):
    """
    حذف التعليق
    يتيح للمستخدم حذف تعليقه
    """
    comment = get_object_or_404(PropertyComment, pk=pk)
    
    # التحقق من أن المستخدم هو صاحب التعليق
    if comment.user != request.user:
        messages.error(request, 'لا يمكنك حذف تعليق شخص آخر')
        return redirect('properties:property_detail', pk=comment.property.pk)
    
    property_id = comment.property.pk
    comment.delete()
    messages.success(request, 'تم حذف التعليق بنجاح')
    
    return redirect('properties:property_detail', pk=property_id)

@login_required_with_message
def received_requests(request):
    """
    الطلبات الواردة
    يعرض جميع الطلبات الواردة للمستخدم
    """
    # عرض جميع الطلبات مرتبة حسب تاريخ الإنشاء
    requests = PropertyRequest.objects.filter(
        is_active=True
    ).select_related('user').order_by('-created_at')

    # تحديث حالة القراءة للطلبات
    requests.update(is_read=True)

    return render(request, 'properties/received_requests.html', {
        'requests': requests
    })

@login_required_with_message
def property_requests(request, property_id):
    """
    طلبات العقار
    يعرض جميع طلبات العقار
    """
    property = get_object_or_404(Property, id=property_id)
    if property.owner != request.user:
        messages.error(request, 'ليس لديك صلاحية لعرض هذه الصفحة')
        return redirect('properties:property_detail', pk=property_id)
    
    # تحديث حالة الطلبات إلى مقروءة
    PropertyRequest.objects.filter(property=property, is_read=False).update(is_read=True)
    
    # جلب جميع الطلبات
    requests = property.requests.all().order_by('-created_at')
    
    return render(request, 'properties/property_requests.html', {
        'property': property,
        'requests': requests
    })
    
    # تحديث حالة الطلبات إلى مقروءة
    PropertyRequest.objects.filter(property=property, is_read=False).update(is_read=True)
    
    # جلب جميع الطلبات
    requests = property.requests.all().order_by('-created_at')
    
    return render(request, 'properties/property_requests.html', {
        'property': property,
        'requests': requests
    })

def property_search(request):
    """
    البحث عن العقارات
    يتيح للمستخدمين البحث عن العقارات حسب معايير مختلفة
    """
    query = request.GET.get('q', '')
    property_type = request.GET.get('type', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    location = request.GET.get('location', '')

    properties = Property.objects.all()

    if query:
        properties = properties.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query)
        )

    if property_type:
        properties = properties.filter(property_type=property_type)

    if min_price:
        properties = properties.filter(price__gte=min_price)

    if max_price:
        properties = properties.filter(price__lte=max_price)

    if location:
        properties = properties.filter(location__icontains=location)

    properties = properties.order_by('-created_at')

    context = {
        'properties': properties,
        'query': query,
        'property_type': property_type,
        'min_price': min_price,
        'max_price': max_price,
        'location': location,
    }

    return render(request, 'properties/property_list.html', context)
