from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from ewaste_management.models import Incentive, User, CEApplication, WasteCollectionSlot, Appliance, MovementRecord, Component, Topic, Comment, Publication, CEApplication, IncentiveRedemptionRecord, Consultation, WasteCollectionSlot, University, Organization, WasteCollectionBooking, WasteCollectionSlot
from .forms import IncentiveFrom, TopicForm, CommentForm, UserForm, CEApplicationForm, PublicationForm, UniversityProfileForm, MovementRecordForm, ConsultationForm
from django.core.serializers import serialize
import json
from datetime import datetime

# Create your views here.
@login_required(login_url='users:login')
def index(request):
    return render(request, 'ewaste_management/index.html')

@login_required(login_url='users:login')
def dashboard(request):
    return render(request, 'ewaste_management/dashboard.html', {
        "user": request.user
    })

@login_required(login_url='users:login')
def incentives(request):
    if request.user.role == "organization_team" :
        return HttpResponseForbidden()
    if request.method == "POST":
        if request.POST.get("search") or not request.POST.get("search") == "":
            incentives = Incentive.objects.filter(name__icontains=request.POST.get("search"), is_active=True)
        else:
            incentives = Incentive.objects.filter(is_active=True)
        return render(request, 'ewaste_management/incentives.html', {
            "incentives": incentives,
            "user": request.user
        })
    elif request.method == "GET":
        incentives = Incentive.objects.filter(is_active=True)
        return render(request, 'ewaste_management/incentives.html', {
            "incentives": incentives,
            "user": request.user
        })


# No html rendering required
@login_required(login_url='users:login')
def edit_incentive(request, incentive_id):
    if not request.user.role == "admin":
        return HttpResponseForbidden()
    if request.method == "POST":
        try:
            if Incentive.objects.filter(name=request.POST.get("name")).exclude(id=incentive_id).exists():
                incentive = Incentive.objects.get(pk=incentive.id)
                return render(request, 'ewaste_management/incentive.html', {
                    "user": request.user,
                    "incentive": incentive,
                    "message": "Title exists"
                })
            elif int(request.POST.get("points_required")) <= 0:
                incentive = Incentive.objects.get(pk=incentive_id)
                return render(request, 'ewaste_management/incentive.html', {
                    "user": request.user,
                    "incentive": incentive,
                    "message": "Points require to be greater than zero"
                })
        except ValueError:
            incentive = Incentive.objects.get(pk=incentive_id)
            return render(request, 'ewaste_management/incentive.html', {
                "user": request.user,
                "incentive": incentive,
                "message": "Points required to be a number"
            }) 
        try:
            incentive = Incentive.objects.get(pk=incentive_id)
            incentive.name = request.POST.get("name", incentive.name)
            incentive.description = request.POST.get("description", incentive.description)
            incentive.points_required = request.POST.get("points_required", incentive.points_required)
            incentive.save()
            return HttpResponseRedirect(reverse("ewaste_management:incentives"))
        except Incentive.DoesNotExist:
            return HttpResponseBadRequest()
    elif request.method == "GET":
        incentive = Incentive.objects.get(pk =incentive_id)
        return render(request, 'ewaste_management/incentive.html', {
            "incentive": incentive,
            "user": request.user
        })
    
@login_required(login_url='users:login')
def delete_incentive(request, incentive_id):
    if not request.user.role == "admin":
        return HttpResponseForbidden()
    try:
        incentive = Incentive.objects.get(pk=incentive_id)
        incentive.is_active = False
        incentive.save()
        return HttpResponseRedirect(reverse("ewaste_management:incentives"))
    except Incentive.DoesNotExist:
        return HttpResponseBadRequest()


@login_required(login_url='users:login')
def add_incentive(request):
    if not request.user.role == "admin":
        return HttpResponseForbidden()
    if request.method == "POST":
        form = IncentiveFrom(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("ewaste_management:incentives"))
        else:
            return render(request, "ewaste_management/add_incentive.html", {
                "message": form.errors,
                  "user": request.user
            })
    return render(request, 'ewaste_management/add_incentive.html', {"user": request.user})

@login_required(login_url='users:login')
def accounts(request):
    if not request.user.role == "admin":
        return HttpResponseForbidden()
    accounts = User.objects.all()
    accounts_json = serialize('json', accounts)
    return render(request, 'ewaste_management/accounts.html', {
        "user": request.user,
        "users": accounts,
        "accounts_json": accounts_json
    })

@login_required(login_url='users:login')
def account(request, account_username):
    if not request.user.role == "admin":
        return HttpResponseForbidden()
    account = User.objects.get(username=account_username)
    return render(request, 'ewaste_management/account.html', {
        "user": request.user,
        "requested_user": account
    })


# No html rendering required
def account_action(request, account_username):
    if not request.user.role == "admin":
        return HttpResponseForbidden()
    account = User.objects.get(username=account_username)
    if account.is_active:
        try:
            account.is_active = False
            account.save()
            return HttpResponseRedirect(reverse("ewaste_management:accounts"))
        except User.DoesNotExist:
            return HttpResponseBadRequest()
    elif not account.is_active:
        try:
            account.is_active = True
            account.save()
            return HttpResponseRedirect(reverse("ewaste_management:accounts"))
        except User.DoesNotExist:
            return HttpResponseBadRequest()
    else:
        return HttpResponseBadRequest()


@login_required(login_url='users:login')
def ces(request):
    if not request.user.role == "admin":
        return HttpResponseForbidden()
    ces = CEApplication.objects.all()
    return render(request, 'ewaste_management/ces.html', {
        "user": request.user,
        "ces": ces
    })

@login_required(login_url='users:login')
def ce(request, ce_id):
    if not request.user.role == "admin":
        return HttpResponseForbidden()
    try:
        ce = CEApplication.objects.get(pk=ce_id)
    except CEApplication.DoesNotExist:
        return HttpResponseBadRequest()
    return render(request, 'ewaste_management/ce.html', {
        "user": request.user,
        "ce": ce
    })

# No html rendering required
@login_required(login_url='users:login')
def approve_ce(request, ce_id):
    if not request.user.role == "admin":
        return HttpResponseForbidden()
    try:
        ce = CEApplication.objects.get(pk=ce_id)
        ce.status = "approved"
        ce.save()
        user = User.objects.get(pk=ce.applicant.email)
        user.role = "campus_expert"
        user.university = ce.university
        user.save()
        return HttpResponseRedirect(reverse("ewaste_management:ces"))
    except CEApplication.DoesNotExist:
        return HttpResponseBadRequest()

@login_required(login_url='users:login')
def reject_ce(request, ce_id):
    if not request.user.role == "admin":
        return HttpResponseForbidden()
    try:
        ce = CEApplication.objects.get(pk=ce_id)
        ce.status = "rejected"
        ce.save()
        return HttpResponseRedirect(reverse("ewaste_management:ces"))
    except CEApplication.DoesNotExist:
        return HttpResponseBadRequest()

## Track
@login_required(login_url='users:login')
def log(request):
    if not request.user.role == "admin":
        return HttpResponseForbidden()
    pickups = WasteCollectionSlot.objects.all()
    appliances = Appliance.objects.all()
    movements = MovementRecord.objects.all()
    components = Component.objects.all()
    return render(request, 'ewaste_management/log.html',{
        "user": request.user,
        "pickups": pickups,
        "appliances": appliances,
        "movements": movements,
        "components": components
    })

@login_required(login_url='users:login')
def forum(request):
    if not request.user.role == "campus_expert" and not request.user.role == "university_community":
        return HttpResponseForbidden()
    topics = Topic.objects.all()
    comments = Comment.objects.all()
    return render(request, 'ewaste_management/forum.html', {
        "user": request.user,
        "topics": topics,
        "comments": comments
    })

@login_required(login_url='users:login')
def view_topic(request, topic_id):
    if not request.user.role == "campus_expert" and not request.user.role == "university_community":
        return HttpResponseForbidden()
    try:
        topic = Topic.objects.get(pk=topic_id)
    except Topic.DoesNotExist:
        return HttpResponseBadRequest()
    comments = Comment.objects.filter(topic=topic_id)
    return render(request, 'ewaste_management/topic.html', {
        "user": request.user,
        "topic": topic,
        "comments": comments
    })

@login_required(login_url='users:login')
def edit_topic(request, topic_id):
    if not request.user.role == "campus_expert" and not request.user.role == "university_community":
        return HttpResponseForbidden()
    if request.method == "POST":
        if Topic.objects.filter(title=request.POST.get("title")).exclude(id=topic_id).exists():
            try:
                topic = Topic.objects.get(pk=topic_id)
            except Topic.DoesNotExist:
                return HttpResponseBadRequest()
            return render(request, 'ewaste_management/edit_topic.html', {
                "user": request.user,
                "topic": topic,
                "message": "Title exists"
            })
        else:
            try:
                topic = Topic.objects.get(pk=topic_id)
                topic.title = request.POST.get("title", topic.title)
                topic.content = request.POST.get("content", topic.content)
                topic.save()
                return HttpResponseRedirect(reverse("ewaste_management:forum"))
            except Topic.DoesNotExist:
                return HttpResponseBadRequest()
    if request.method == "GET":
        try:
            topic = Topic.objects.get(pk=topic_id)
        except Topic.DoesNotExist:
            return HttpResponseBadRequest()
        return render(request, 'ewaste_management/edit_topic.html', {
            "user": request.user,
            "topic": topic
        })

@login_required(login_url='users:login')
def add_topic(request):
    if not request.user.role == "campus_expert" and not request.user.role == "university_community":
        return HttpResponseForbidden()
    if request.method == "POST":
        form = TopicForm(request.POST, request.FILES)
        if form.is_valid():
            topic = Topic()
            topic.title = request.POST.get("title")
            topic.content = request.POST.get("content")
            topic.user = request.user
            topic.save()
            return HttpResponseRedirect(reverse("ewaste_management:forum"))
        else:
            topics = Topic.objects.all()
            comments = Comment.objects.all()
            return render(request, "ewaste_management/forum.html", {
                "message": form.errors, 
                "user": request.user,
                "topics": topics,
                "comments": comments
            })
    if request.method == "GET":
        return HttpResponseBadRequest()

# No html rendering required
@login_required(login_url='users:login')
def add_comment(request, topic_id):
    if not request.user.role == "campus_expert" and not request.user.role == "university_community":
        return HttpResponseForbidden()
    if request.method == "POST":
        form = CommentForm(request.POST, request.FILES)
        comment = Comment()
        if form.is_valid():
            comment.user = request.user
            comment.topic = Topic.objects.get(pk=topic_id)
            comment.content = request.POST.get("content", comment.content)
            comment.save()
            return HttpResponseRedirect(reverse("ewaste_management:forum"))
        else:
            return HttpResponseBadRequest()
    elif request.method == "GET":
        topic = Topic.objects.get(pk=topic_id)
        return render(request, 'ewaste_management/add_comment.html', {
            "user": request.user,
            "topic" : topic
        })
    else:
        Http404()

# No html rendering required
@login_required(login_url='users:login')
def edit_comment(request, topic_id, comment_id):
    if not request.user.role == "campus_expert" and not request.user.role == "university_community":
        return HttpResponseForbidden()
    if request.method == "POST":
        form = CommentForm(request.POST, request.FILES)
        if not form.is_valid():
            return HttpResponseBadRequest()
        try:
            comment = Comment.objects.get(pk=comment_id)
            comment.content = request.POST.get("content", comment.content)
            comment.save()
            return HttpResponseRedirect(reverse("ewaste_management:forum"))
        except Comment.DoesNotExist:
            return HttpResponseBadRequest()
    else:
        return Http404()

@login_required(login_url='users:login')
def uemip(request):
    if not request.user.role == "campus_expert" and not request.user.role == "university_community":
        return HttpResponseForbidden()
    publications = Publication.objects.all()
    return render(request, 'ewaste_management/uemip.html', {
        "user": request.user,
        "publications": publications
    })

@login_required(login_url='users:login')
def view_publication(request, publication_id):
    if not request.user.role == "campus_expert" and not request.user.role == "university_community":
        return HttpResponseForbidden()
    try:
        publication = Publication.objects.get(pk=publication_id)
    except Publication.DoesNotExist:
        return HttpResponseBadRequest()
    return render(request, 'ewaste_management/view_publication.html', {
        "publication": publication
    })

@login_required(login_url='users:login')
def university_profile(request, university_id):
    if not request.user.role == "campus_expert" and not request.user.role == "university_community":
        return HttpResponseForbidden()
    try:
        university = University.objects.get(pk=university_id)
    except University.DoesNotExist:
        return HttpResponseBadRequest()
    return render(request, 'ewaste_management/university_profile.html', {
        "university": university
    })

@login_required(login_url='users:login')
def universities_profile(request):
    if not request.user.role == "campus_expert" and not request.user.role == "university_community":
        return HttpResponseForbidden()
    try:
        universities = University.objects.all()
    except University.DoesNotExist:
        return HttpResponseBadRequest()
    return render(request, 'ewaste_management/universities_profile.html', {
        "universities": universities
    })

@login_required(login_url='users:login')
def profile(request):
    user = request.user
    return render(request, 'ewaste_management/profile.html', {
        "user": user
    })

@login_required(login_url='users:login')
def edit_profile(request):
    if request.method == "POST":
        user = request.user
        user.phone_number = request.POST.get("phone_number", user.phone_number)
        user.bio = request.POST.get("bio", user.bio)
        if request.POST.get('university') and request.POST.get("university") != "":
            user.university = University.objects.get(pk=request.POST.get("university"))
        if request.POST.get('organization') and request.POST.get("organization") != "": 
            user.organization = Organization.objects.get(pk=request.POST.get("organization"))
        if request.POST.get("password") != "":
            user.set_password(request.POST.get("password"))
        user.save()
        return HttpResponseRedirect(reverse("ewaste_management:profile"))
    elif request.method == "GET":
        user = request.user
        universities = University.objects.all()
        organizations = Organization.objects.all()
        return render(request, 'ewaste_management/edit_profile.html', {
            "user": user,
            "universities" : universities,
            "organizations" : organizations
        })
    
@login_required(login_url='users:login')
def ce_application(request):
    if  not request.user.role == "university_community" and not request.user.role == "campus_expert":
        return HttpResponseForbidden()
    try:
        ce_application = CEApplication.objects.filter(applicant=request.user)
        universities = University.objects.all()
    except CEApplication.DoesNotExist:
        ce_application = None
    return render(request, 'ewaste_management/ce_application.html', {
        "ce_applications": ce_application,
        "universities": universities,
        "user": request.user
    })

# No html rendering required
@login_required(login_url='users:login')
def submit_ce_application(request):
    if not request.user.role == "university_community":
        return HttpResponseForbidden()
    if request.method == "POST":
        form = CEApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            ce_application = CEApplication()
            ce_application.applicant = request.user
            university = University.objects.get(pk=request.POST.get("university"))
            ce_application.university = university
            application_detail = "motivation: " + request.POST.get("motivation") + "\n" + "experience: " + request.POST.get("experience")
            ce_application.application_detail = application_detail
            ce_application.save()
            return HttpResponseRedirect(reverse("ewaste_management:ce_application"))
        else:
            return HttpResponse(form.errors)
    else:
        return Http404()

# No html rendering required
@login_required(login_url='users:login')
def redeem_incentive(request, incentive_id):
    if not request.user.role == "university_community" and not request.user.role == "campus_expert":
        return HttpResponseForbidden()
    if request.method == "POST":
        incentive = Incentive.objects.get(pk=incentive_id)
        if IncentiveRedemptionRecord.objects.filter(user=request.user, incentive=incentive).exists():
            incentive_redemption = IncentiveRedemptionRecord.objects.get(user=request.user, incentive=incentive)
            incentive_redemption.quantity += 1
            request.user.point_earned -= incentive.points_required
            request.user.save()
            incentive_redemption.save()
        else:
            incentive_redemption = IncentiveRedemptionRecord()
            incentive_redemption.incentive = incentive
            incentive_redemption.user = request.user
            incentive_redemption.quantity = 1
            request.user.point_earned -= incentive.points_required
            request.user.save()
            incentive_redemption.save()

        return HttpResponseRedirect(reverse("ewaste_management:incentives"))
    else:
        return Http404()

@login_required(login_url='users:login')
def consultations(request):
    if not request.user.role == "campus_expert" and not request.user.role == "university_community":
        return HttpResponseForbidden()
    if request.method == "POST" and request.POST.get('status') != "":
        consultations = Consultation.objects.filter(status=request.POST.get('status'))
        return render(request, 'ewaste_management/consultations.html',{
            "user": request.user,
            "consultations": consultations
        })
    consultations = Consultation.objects.all()
    return render(request, 'ewaste_management/consultations.html', {
        "user": request.user,
        "consultations": consultations
    })

@login_required(login_url='users:login')
def consultation(request):
    # if not request.user.role == "campus_expert" and not request.user.role == "university_community":
    #     return HttpResponseForbidden()
    # try:
    #     if request.GET.get("search") or not request.GET.get("search") == "":
    #         consultation = Consultation.objects.get(user=User.objects.get(username_icontains=request.GET.get("search")))
    #         consultation += Consultation.objects.filter(university=University.objects.get(university_name_icontains=request.GET.get("search")))
    #         return render(request, 'ewaste_management/consultation.html', {
    #             "user": request.user,
    #             "consultation": consultation
    #         })
    # except Consultation.DoesNotExist:
    #     return HttpResponseBadRequest()
    consultation = Consultation.objects.all()
    return render(request, 'ewaste_management/consultation.html', {
        "user": request.user,
        "available_slot": consultation,
        "user_consultations": consultation
    })

# No html rendering required
@login_required(login_url='users:login')
def book_consultation(request, consultation_id):
    if not request.user.role == "campus_expert" and not request.user.role == "university_community":
        return HttpResponseForbidden()
    if request.method == "POST":
        try:
            consultation = Consultation.objects.get(pk=consultation_id)
        except Consultation.DoesNotExist:
            return HttpResponseBadRequest()
        print("booking.....")
        consultation.user = request.user
        consultation.status = "booked"
        consultation.save()
    return HttpResponseRedirect(reverse("ewaste_management:consultations"))

@login_required(login_url='users:login')
def pickup(request):
    if request.user.role == "admin":
        return HttpResponseForbidden()
    if request.user.role == 'organization_team':
        pickups = WasteCollectionSlot.objects.filter(organization=request.user.organization).order_by('-collection_date_time')
    else:
        pickups = WasteCollectionSlot.objects.all()
    if request.user.role == "campus_expert" or request.user.role == "university_community":
        booking_slots = WasteCollectionBooking.objects.filter(user=request.user)
    else:
        organization_slots = WasteCollectionSlot.objects.filter(organization=request.user.organization)
        booking_slots = WasteCollectionBooking.objects.filter(waste_collection_slot__in=organization_slots)
    return render(request, 'ewaste_management/pickup.html', {
        "user": request.user,
        "pickups": pickups,
        "booking_slots": booking_slots
    })

@login_required(login_url='users:login')
def my_appointments(request):
    if request.user.role == "admin":
        return HttpResponseForbidden()
    if request.user.role == 'organization_team':
        pickups = WasteCollectionSlot.objects.filter(organization=request.user.organization).order_by('-collection_date_time')
    else:
        pickups = WasteCollectionSlot.objects.all()
    if request.user.role == "campus_expert" or request.user.role == "university_community":
        booking_slots = WasteCollectionBooking.objects.filter(user=request.user)
    else:
        organization_slots = WasteCollectionSlot.objects.filter(organization=request.user.organization)
        booking_slots = WasteCollectionBooking.objects.filter(waste_collection_slot__in=organization_slots)
    return render(request, 'ewaste_management/my_appointments.html', {
        "user": request.user,
        "pickups": pickups,
        "booking_slots": booking_slots
    })


@login_required(login_url='users:login')
def search_pickup(request):
    if request.user.role == "admin":
        return HttpResponseForbidden()
    if request.method == "POST":
        search_query = request.POST.get("search")
        if search_query == "":
            return HttpResponseRedirect(reverse("ewaste_management:pickup"))
        if request.user.role == 'organization_team':
            pickups = WasteCollectionSlot.objects.filter(
            organization=request.user.organization, location__icontains=search_query
            ).order_by('-collection_date_time')
        else:
            pickups = WasteCollectionSlot.objects.filter(location__icontains=search_query)
        if request.user.role == "campus_expert" or request.user.role == "university_community":
            booking_slots = WasteCollectionBooking.objects.filter(
            user=request.user, waste_collection_slot__location__icontains=search_query
            )
        else:
            organization_slots = WasteCollectionSlot.objects.filter(
            organization=request.user.organization, location__icontains=search_query
            )
            booking_slots = WasteCollectionBooking.objects.filter(
            waste_collection_slot__in=organization_slots
            )
        return render(request, 'ewaste_management/pickup.html', {
            "user": request.user,
            "pickups": pickups,
            "booking_slots": booking_slots
        })
    elif request.method == "GET":
        return HttpResponseRedirect(reverse("ewaste_management:pickup"))

@login_required(login_url='users:login')
def pickup_detail(request, pickup_id):
    if not request.user.role == "campus_expert" and not request.user.role == "university_community":
        return HttpResponseForbidden()
    try:
        pickup = WasteCollectionSlot.objects.get(pk=pickup_id)
    except WasteCollectionSlot.DoesNotExist:
        return HttpResponseBadRequest()
    return render(request, 'ewaste_management/pickup_details.html', {
        "pickup": pickup
    })

# No html rendering required
@login_required(login_url='users:login')
def book_pickup(request):
    if not request.user.role == "campus_expert" and not request.user.role == "university_community":
        return HttpResponseForbidden()
    if request.method == "POST":
        try:
            pickup = WasteCollectionSlot.objects.get(pk=request.POST.get("pickup_id"))
        except WasteCollectionSlot.DoesNotExist:
            return HttpResponseBadRequest()
        pickup.user = request.user
        pickup.status = "booked"
        pickup.save()
        waste_collection_booking = WasteCollectionBooking()
        waste_collection_booking.user = request.user
        waste_collection_booking.waste_collection_slot = pickup
        waste_collection_booking.preferrable_time = request.POST.get("time")
        waste_collection_booking.address = request.POST.get("street") + ", " + request.POST.get("city") + ", " + request.POST.get("zip") + ", " + request.POST.get("state") + ", " + request.POST.get("country")
        waste_collection_booking.status = "pending"
        waste_collection_booking.save()

        appliances_name = request.POST.getlist("item[]")
        serial_number = request.POST.getlist("serial_number[]")
        counter = 0
        for appliance_name in appliances_name:
            appliance = Appliance()
            appliance.serial_number = serial_number[counter]
            appliance.product_name = appliance_name
            appliance.waste_collection_booking = waste_collection_booking
            appliance.save()
            counter += 1

        return HttpResponseRedirect(reverse("ewaste_management:pickup"))
    else: 
        return Http404()

# No html rendering required
@login_required(login_url='users:login')
def delete_topic(request, topic_id):
    if not request.user.role == "campus_expert" and not request.user.role == "university_community":
        return HttpResponseForbidden()
    if request.method == "POST":
        try:
            topic = Topic.objects.get(pk=topic_id)
            topic.delete()
            return HttpResponseRedirect(reverse("ewaste_management:forum"))
        except Topic.DoesNotExist:
            return HttpResponseBadRequest()
    else:
        return Http404()

# No html rendering required
@login_required(login_url='users:login')
def delete_comment(request, topic_id, comment_id):
    if not request.user.role == "campus_expert" and not request.user.role == "university_community":
        return HttpResponseForbidden()
    if request.method == "POST":
        try:
            comment = Comment.objects.get(pk=comment_id)
            comment.delete()
            return HttpResponseRedirect(reverse("ewaste_management:forum"))
        except Comment.DoesNotExist:
            return HttpResponseBadRequest()
    else:
        return Http404()

@login_required(login_url='users:login')
def add_publication(request):
    if not request.user.role == "campus_expert":
        return HttpResponseForbidden()
    if request.method == "POST":
        form = PublicationForm(request.POST)
        if form.is_valid():
            publication = Publication()
            publication.user = request.user
            publication.title = request.POST.get("title")
            publication.publication_detail = request.POST.get("publication_detail")
            publication.publication_location = request.POST.get("publication_location")
            publication.publication_university = request.user.university
            publication.event_start_date = request.POST.get("event_start_date")
            publication.event_end_date = request.POST.get("event_end_date")
            publication.save()
            return HttpResponseRedirect(reverse("ewaste_management:uemip"))
        else:
             return render(request, 'ewaste_management/add_publication.html', {
            "user": request.user,
            "message": form.errors
        })
    elif request.method == "GET":
        return render(request, 'ewaste_management/add_publication.html', {
            "user": request.user
        })

    return render(request, 'ewaste_management/add_publication.html')

@login_required(login_url='users:login')
def edit_publication(request, publication_id):
    if not request.user.role == "campus_expert":
        return HttpResponseForbidden()
    if request.method == "POST":
        form = PublicationForm(request.POST, request.FILES)
        if not form.is_valid():
            return HttpResponseBadRequest()
        try:
            publication = Publication.objects.get(pk=publication_id)
            publication.title = request.POST.get("title", publication.title)
            publication.publication_detail = request.POST.get("publication_detail", publication.publication_detail)
            publication.publication_location = request.POST.get("publication_location", publication.publication_location)
            publication.publication_university = request.user.university
            publication.event_start_date = request.POST.get("event_start_date", publication.event_start_date)
            publication.event_end_date = request.POST.get("event_end_date", publication.event_end_date)
            publication.save()
            return HttpResponseRedirect(reverse("ewaste_management:uemip"))
        except Publication.DoesNotExist:
            return HttpResponseBadRequest()
    elif request.method == "GET":
        try:
            publication = Publication.objects.get(pk=publication_id)
        except Publication.DoesNotExist:
            return HttpResponseBadRequest()
        return render(request, 'ewaste_management/edit_publication.html', {
            "user": request.user,
            "publication": publication
        })

@login_required(login_url='users:login')
def add_university_profile(request):
    if not request.user.role == "campus_expert":
        return HttpResponseForbidden()
    if request.method == "POST":
        form = UniversityProfileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("ewaste_management:uemip"))
        else:
            return render(request, 'ewaste_management/add_university_profile.html', {
                "message": form.errors
            })
    return render(request, 'ewaste_management/add_university_profile.html')

@login_required(login_url='users:login')
def edit_university_profile(request, university_id):
    if not request.user.role == "campus_expert":
        return HttpResponseForbidden()
    if request.method == "POST":
        if University.objects.filter(university_name=request.POST.get("university_name")).exclude(id=university_id).exists():
            return HttpResponseBadRequest()
        try:
            university_profile = University.objects.get(pk=university_id)
            university_profile.university_name = request.POST.get("university_name", university_profile.university_name)
            university_profile.address = request.POST.get("address", university_profile.address)
            university_profile.bio = request.POST.get("bio", university_profile.bio)
            university_profile.save()
            return HttpResponseRedirect(reverse("ewaste_management:universities_profile"))
        except University.DoesNotExist:
            return HttpResponseBadRequest()
    elif request.method == "GET":
        try:
            university = University.objects.get(pk=university_id)
        except University.DoesNotExist:
            return HttpResponseBadRequest()
        return render(request, 'ewaste_management/edit_university_profile.html', {
            "user": request.user,
            "university": university
        })

@login_required(login_url='users:login')
def add_consultation(request):
    if not request.user.role == "campus_expert":
        return HttpResponseForbidden()
    if request.method == "POST":
        form = ConsultationForm(request.POST, request.FILES)
        if form.is_valid():
            consultation = Consultation()
            consultation.consultant = request.user
            consultation.date = request.POST.get("date")
            consultation.time = request.POST.get("time")
            consultation.location = request.POST.get("location")
            consultation.duration_hr = request.POST.get("duration_hr")
            consultation.status = "available"
            consultation.save()
            return HttpResponseRedirect(reverse("ewaste_management:consultations"))
        else:
            return HttpResponseBadRequest()
    elif request.method == "GET":
        return render(request, 'ewaste_management/add_consultation.html', {
            "user": request.user
        })

@login_required(login_url='users:login')
def edit_consultation(request, consultation_id):
    if not request.user.role == "campus_expert":
        return HttpResponseForbidden()
    if request.method == "POST":
        try:
            consultation = Consultation.objects.get(pk=consultation_id)
            consultation.date = request.POST.get("date")
            consultation.time = request.POST.get("time")
            consultation.location = request.POST.get("location")
            consultation.duration_hr = request.POST.get('duration_hr')
            consultation.save()
            return HttpResponseRedirect(reverse("ewaste_management:consultations"))
        except Consultation.DoesNotExist:
            return HttpResponseBadRequest()
    elif request.method == "GET":
        try:
            consultation = Consultation.objects.get(pk=consultation_id)
        except Consultation.DoesNotExist:
            return HttpResponseBadRequest()
        return render(request, 'ewaste_management/edit_consultation.html', {
            "user": request.user,
            "consultation": consultation
        })

@login_required(login_url='users:login')
def schedule_pickup(request):
    if request.method == "POST":
        waste_collection_slot = WasteCollectionSlot()
        if not request.POST.get('state') or not request.POST.get('district') or request.POST.get('date') or request.POST.get('time'):
            HttpResponseBadRequest
        location = request.POST.get('state') + "-" + request.POST.get('district')
        date  = request.POST.get('date')
        time = request.POST.get('time')
        datetime_obj = datetime.strptime(date + " " + time, "%Y-%m-%d %H:%M")
        waste_collection_slot.organization = request.user.organization
        waste_collection_slot.location = location
        waste_collection_slot.collection_date_time = datetime_obj
        waste_collection_slot.status = 'available'
        waste_collection_slot.save()
        return HttpResponseRedirect(reverse('ewaste_management:pickup'))
    elif request.method == "GET":
        return render(request, 'ewaste_management/schedule_pickup.html')

#  Not Done yet
def edit_pickup(request, pickup_id):
    pickup = WasteCollectionSlot.objects.get(pk=pickup_id)
    if request.method == "POST":
        if not request.POST.get('state') or not request.POST.get('district') or request.POST.get('date') or request.POST.get('time'):
            HttpResponseBadRequest
        location = request.POST.get('state') + "-" + request.POST.get('district')
        date  = request.POST.get('date')
        time = request.POST.get('time')
        datetime_obj = datetime.strptime(date + " " + time, "%Y-%m-%d %H:%M")
        waste_collection_slot = WasteCollectionSlot.objects.get(pk=pickup_id)
        waste_collection_slot.location = location
        waste_collection_slot.collection_date_time = datetime_obj
        waste_collection_slot.status = 'edited'
        waste_collection_slot.save()
        return HttpResponseRedirect(reverse('ewaste_management:pickup'))
    elif request.method == "GET":
        pickup = WasteCollectionSlot.objects.get(pk=pickup_id)
        location = pickup.location.split("-")
        print(pickup.location.split("-"))
        return render(request, 'ewaste_management/edit_pickup.html', {
            "pickup": pickup,
            "state": location[0],
            "district": location[1],

        })

# No html rendering required
def delete_pickup(request, pickup_id):
    waste_collection_slot = WasteCollectionSlot.objects.get(pk=pickup_id)
    waste_collection_slot.status = 'cancelled'
    waste_collection_slot.save()
    return HttpResponseRedirect(reverse('ewaste_management:pickup'))

def views(request):
    return render(request, 'ewaste_management/views.html')

def track(request):
    components = Component.objects.all()
    return render(request, 'ewaste_management/track.html', {
        "user": request.user,
        "components": components
    })

@login_required(login_url='users:login')
def add_track(request):
    if not request.user.role == "organization_team":
        return HttpResponseForbidden()
    if request.method == "GET":
        organization = Organization.objects.all()
        appliances = Appliance.objects.all()
        return render(request, 'ewaste_management/add_track.html', {
            "user": request.user,
            "organizations": organization,
            "appliances": appliances
        })
    elif request.method == "POST":
        print(request.POST)
        print(request.POST.get('recipient'))
        movementRecord = MovementRecord()
        movementRecord.supplier = request.user.organization
        if request.POST.get('recipient') and request.POST.get('recipient') != "":
            movementRecord.recipeint = Organization.objects.get(pk=request.POST.get('recipient'))
            print(movementRecord.recipeint)
        if request.POST.get('recipient_company') != "":
            movementRecord.recipeint_company = request.POST.get('recipient_company')
        movementRecord.save()
        
        if request.POST.getlist('appliance[]'):
            appliences = request.POST.getlist('appliance[]')
            print(appliences)
            component_names = request.POST.getlist('component_name[]')
            print(component_names)
            amounts = request.POST.getlist('amount[]')
            print(amounts)
            status = request.POST.getlist('status[]')
            print(status)
            counter = 0
            for applience in appliences:
                component = Component()
                appliance = Appliance.objects.get(pk=applience)
                component.appliance = appliance
                component.component_name = component_names[counter]
                component.amount = amounts[counter]
                component.status = status[counter]
                component.save()
                component.record.set([movementRecord])
                counter += 1
                component.save()
        return HttpResponseRedirect(reverse("ewaste_management:track"))





def custom_403(request, exception=None):
    return render(request, 'ewaste_management/403.html', status=403)

def custom_400(request, exception=None):
    return render(request, 'ewaste_management/400.html', status=400)

def log_details(request):
    appliances = Appliance.objects.all()
    components = Component.objects.all()
    return render(request, 'ewaste_management/log_details.html', {
        "user": request.user,
        "appliances": appliances,
        "components": components
    })

@login_required(login_url='users:login')
def organization_profile(request):
    if request.user.role != "organization_team":
        return HttpResponseForbidden()
    try:
        organization = Organization.objects.get(pk=request.user.organization.id)
    except Organization.DoesNotExist:
        return HttpResponseBadRequest()
    return render(request, 'ewaste_management/organization_profile.html', {
        "user": request.user,
        "organization": organization
    })

@login_required(login_url='users:login')
def edit_organization_profile(request):
    organization = Organization.objects.get(pk=request.user.organization.id)
    if request.method == "POST" :
        if Organization.objects.filter(organization_name=request.POST.get("orgnization_name")).exclude(id=request.user.organization.id).exists():
            return render(request, 'ewaste_management/edit_organization_profile.html', {
                "user": request.user,
                "organization": organization,
                "message": "Organization name exists"
            })
        else:
            organization = Organization.objects.get(pk=request.user.organization.id)
            organization.address = request.POST.get("address")
            organization.organization_type = request.POST.get("organization_type")
            organization.additional_information = request.POST.get("additional_information")
            organization.website = request.POST.get("website")
            organization.save()
            return HttpResponseRedirect(reverse("ewaste_management:organization_profile"))
    return render(request, 'ewaste_management/edit_organization_profile.html', {
        "user": request.user,
        "organization": organization
    })


def pickup_summary(request):
    waste_collection_booking = WasteCollectionBooking.objects.all()
    return render(request, 'ewaste_management/pickup_summary.html', {
        "waste_collection_booking": waste_collection_booking
        })

def past_pickup_summary(request):
    waste_collection_booking = WasteCollectionBooking.objects.all()
    return render(request, 'ewaste_management/past_pickup_summary.html', {
        "waste_collection_booking": waste_collection_booking
    })

def all_topics(request):
    if request.method == "GET" :
        topics = Topic.objects.all()
        comments = Comment.objects.all()
        return render(request, 'ewaste_management/all_forum.html', {
            "user": request.user,
            "topics": topics,
            "comments": comments
        })
    elif request.method == "POST":
        if request.POST.get("search") != "":
            topics = Topic.objects.filter(title__icontains=request.POST.get("search"))
            comments = Comment.objects.filter( content__icontains=request.POST.get("search"))
        else:
            topics = Topic.objects.all()
            comments = Comment.objects.all()
        if request.POST.get("sort") == "newest":
            topics = topics.order_by('-created_at')
            comments = comments.order_by('-created_at')
        elif request.POST.get("sort") == "oldest":
            topics = topics.order_by('created_at')
            comments = comments.order_by('created_at')
        return render(request, 'ewaste_management/all_forum.html', {
                "user": request.user,
                "topics": topics,
                "comments": comments
            })

def user_created_topics(request):
    if request.method == "GET":
        topic = Topic.objects.filter(user=request.user)
        comments = Comment.objects.filter(user=request.user)
        return render(request, 'ewaste_management/user_created_topic.html', {
            "user": request.user,
            "topics": topic,
            "comments": comments
        })
    elif request.method == "POST":
        if request.POST.get("search") != "":
            topics = Topic.objects.filter(user=request.user, title__icontains=request.POST.get("search"))
            comments = Comment.objects.filter(user=request.user, content__icontains=request.POST.get("search"))
        else:
            topics = Topic.objects.filter(user=request.user)
            comments = Comment.objects.filter(user=request.user)
        if request.POST.get("sort") == "newest":
            topics = topics.order_by('-created_at')
            comments = comments.order_by('-created_at')
        elif request.POST.get("sort") == "oldest":
            topics = topics.order_by('created_at')
            comments = comments.order_by('created_at')
        return render(request, 'ewaste_management/user_created_topic.html', {
                "user": request.user,
                "topics": topics,
                "comments": comments
            })

def cancel_consultation(request, consultation_id):
    if not request.user.role == "campus_expert" and not request.user.role == "university_community":
        return HttpResponseForbidden()
    try:
        consultation = Consultation.objects.get(pk=consultation_id)
        consultation.user = None
        consultation.status = 'available'
        consultation.save()
        return HttpResponseRedirect(reverse("ewaste_management:consultations"))
    except Consultation.DoesNotExist:
        return HttpResponseBadRequest()

def organization_profiles(request):
    if request.user.role == "admin":
        return HttpResponseForbidden()
    if request.user.role == 'university_community' or request.user.role == 'campus_expert':
        organizations = Organization.objects.filter(organization_type='collection')
    elif request.user.role == 'organization_team' and request.user.organization.organization_type == 'collection':
        organizations = Organization.objects.filter(organization_type='processing')
    elif request.user.role == 'organization_team' and request.user.organization.organization_type == 'processing':
        organizations = Organization.objects.filter(organization_type='recycling')
    return render(request, 'ewaste_management/profile_list.html', {
        "user": request.user,
        "organizations": organizations
    })

def cancel_pickup(request, pickup_id):
    try:
        pickup = WasteCollectionBooking.objects.get(pk=pickup_id)
        pickup.status = 'cancelled'
        pickup.save()
        return HttpResponseRedirect(reverse("ewaste_management:pickup"))
    except WasteCollectionSlot.DoesNotExist:
        return HttpResponseBadRequest()
    
def reject_pickup(request, pickup_id):
    try:
        pickup = WasteCollectionBooking.objects.get(pk=pickup_id)
        pickup.status = 'rejected'
        pickup.save()
        return HttpResponseRedirect(reverse("ewaste_management:pickup"))
    except WasteCollectionSlot.DoesNotExist:
        return HttpResponseBadRequest()
    
def confirm_pickup(request, pickup_id):
    try:
        pickup = WasteCollectionBooking.objects.get(pk=pickup_id)
        pickup.status = 'confirmed'
        pickup.save()
        return HttpResponseRedirect(reverse("ewaste_management:pickup"))
    except WasteCollectionSlot.DoesNotExist:
        return HttpResponseBadRequest()

def collected_pickup(request, pickup_id):
    try:
        pickup = WasteCollectionBooking.objects.get(pk=pickup_id)
        pickup.status = 'collected'
        pickup.save()
        user = pickup.user
        user.point_earned += 5
        user.save()
        return HttpResponseRedirect(reverse("ewaste_management:pickup"))
    except WasteCollectionSlot.DoesNotExist:
        return HttpResponseBadRequest()

def view_pickup(request, booking_id):
    requested_booking = WasteCollectionBooking.objects.get(pk=booking_id)
    booking_items = Appliance.objects.filter(waste_collection_booking=requested_booking)
    print(booking_items)
    print(booking_id)
    return render(request, 'ewaste_management/view_pickup.html', {
        "user": request.user,
        "booking_items": booking_items
    })

def demote_account(request, account_username):
    if not request.user.role == "admin":
        return HttpResponseForbidden()
    try:
        user = User.objects.get(username=account_username)
        user.role = "university_community"
        user.save()
        return HttpResponseRedirect(reverse("ewaste_management:accounts"))
    except User.DoesNotExist:
        return HttpResponseBadRequest()
