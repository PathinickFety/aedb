from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Program, Beneficiary, ProgramLike, ProgramComment, ProgramShare
from .forms import ProgramForm, BeneficiaryForm


# =====================
# AUTHENTICATION VIEWS
# =====================

def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created successfully.')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'program/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'program/login.html', {'form': form})


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def profile_view(request):
    """User profile view - users can only edit their own profile"""
    user = request.user
    
    if request.method == 'POST':
        # Additional security check - ensure user is editing their own profile
        if str(user.id) != str(request.POST.get('user_id', user.id)):
            messages.error(request, 'You can only edit your own profile.')
            return redirect('profile')
            
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        messages.success(request, 'Your profile has been updated successfully.')
        return redirect('profile')
    
    return render(request, 'program/profile.html', {
        'user': user
    })


# =====================
# PROGRAM VIEWS
# =====================

def home(request):
    """List all programs with search functionality"""
    # Show all programs to authenticated users, only unfinished to anonymous users
    if request.user.is_authenticated:
        programs = Program.objects.all()
    else:
        programs = Program.objects.filter(is_finished=False)
    
    beneficiaries = Beneficiary.objects.all()
    search_query = request.GET.get('q', '').strip()
    
    # Apply search filters if query is provided
    if search_query:
        # Filter programs by name, type, place, responsible person, or notes
        programs = programs.filter(
            Q(name__icontains=search_query) |
            Q(program_type__icontains=search_query) |
            Q(place__icontains=search_query) |
            Q(responsible__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
        
        # Filter beneficiaries by full name, phone numbers, or address
        beneficiaries = beneficiaries.filter(
            Q(full_name__icontains=search_query) |
            Q(phone1__icontains=search_query) |
            Q(phone2__icontains=search_query) |
            Q(phone3__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(category__icontains=search_query)
        )

    # Get statistics for authenticated users
    stats = {}
    if request.user.is_authenticated:
        stats = {
            'total_programs': Program.objects.count(),
            'active_programs': Program.objects.filter(is_finished=False).count(),
            'finished_programs': Program.objects.filter(is_finished=True).count(),
            'total_beneficiaries': Beneficiary.objects.count(),
            'total_likes': ProgramLike.objects.count(),
            'total_comments': ProgramComment.objects.count(),
            'total_shares': ProgramShare.objects.count(),
        }

    context = {
        'programs': programs,
        'beneficiaries': beneficiaries,
        'search_query': search_query,
        'stats': stats,
        'is_authenticated': request.user.is_authenticated,
    }
    return render(request, 'program/home.html', context)


def programs_list(request):
    """View all programs with search functionality"""
    programs = Program.objects.all()
    search_query = request.GET.get('q', '').strip()
    
    if search_query:
        programs = programs.filter(
            Q(name__icontains=search_query) |
            Q(program_type__icontains=search_query) |
            Q(place__icontains=search_query) |
            Q(responsible__icontains=search_query) |
            Q(notes__icontains=search_query)
        )

    context = {
        'programs': programs,
        'search_query': search_query,
    }
    return render(request, 'program/programs_list.html', context)


def beneficiaries_list(request):
    """View all beneficiaries with search functionality"""
    beneficiaries = Beneficiary.objects.all()
    search_query = request.GET.get('q', '').strip()
    
    if search_query:
        beneficiaries = beneficiaries.filter(
            Q(full_name__icontains=search_query) |
            Q(phone1__icontains=search_query) |
            Q(phone2__icontains=search_query) |
            Q(phone3__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(category__icontains=search_query)
        )

    context = {
        'beneficiaries': beneficiaries,
        'search_query': search_query,
    }
    return render(request, 'program/beneficiaries_list.html', context)


def program_detail(request, id):
    """View program details"""
    program = get_object_or_404(Program, id=id)
    
    # Check if user can view this program
    if program.is_finished and not request.user.is_authenticated:
        messages.error(request, 'This program has finished and is no longer available.')
        return redirect('home')
    
    beneficiaries = program.beneficiaries.all()
    
    # Get interaction data for authenticated users
    user_like = None
    user_share = None
    comments = []
    like_count = 0
    share_count = 0
    
    if request.user.is_authenticated:
        user_like = ProgramLike.objects.filter(user=request.user, program=program).first()
        user_share = ProgramShare.objects.filter(user=request.user, program=program).first()
        comments = ProgramComment.objects.filter(program=program).select_related('user')
        like_count = ProgramLike.objects.filter(program=program).count()
        share_count = ProgramShare.objects.filter(program=program).count()

    context = {
        'program': program,
        'beneficiaries': beneficiaries,
        'user_like': user_like,
        'user_share': user_share,
        'comments': comments,
        'like_count': like_count,
        'share_count': share_count,
        'can_interact': request.user.is_authenticated,
    }
    return render(request, 'program/program_detail.html', context)


def program_create(request):
    """Create a new program"""
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to create programs.')
        return redirect('login')
        
    if request.method == 'POST':
        form = ProgramForm(request.POST)
        if form.is_valid():
            program = form.save()
            messages.success(request, 'Program created successfully!')
            return redirect('program_detail', id=program.id)
    else:
        form = ProgramForm()
    
    context = {
        'form': form,
        'title': 'Create Program',
    }
    return render(request, 'program/program_form.html', context)


def program_update(request, id):
    """Update an existing program"""
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to edit programs.')
        return redirect('login')
        
    program = get_object_or_404(Program, id=id)
    
    if request.method == 'POST':
        form = ProgramForm(request.POST, instance=program)
        if form.is_valid():
            form.save()
            messages.success(request, 'Program updated successfully!')
            return redirect('program_detail', id=program.id)
    else:
        form = ProgramForm(instance=program)
    
    context = {
        'form': form,
        'program': program,
        'title': 'Edit Program',
    }
    return render(request, 'program/program_form.html', context)


def program_delete(request, id):
    """Delete a program"""
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to delete programs.')
        return redirect('login')
        
    program = get_object_or_404(Program, id=id)
    
    if request.method == 'POST':
        program.delete()
        messages.success(request, 'Program deleted successfully!')
        return redirect('home')
    
    context = {
        'program': program,
    }
    return render(request, 'program/program_confirm_delete.html', context)


# =====================
# BENEFICIARY VIEWS
# =====================

def beneficiary_detail(request, id):
    """View beneficiary details"""
    beneficiary = Beneficiary.objects.get(id=id)
    programs = beneficiary.programs.all().order_by('-date')

    context = {
        'beneficiary': beneficiary,
        'programs': programs,
    }
    return render(request, 'program/beneficiary_detail.html', context)


def beneficiary_create(request):
    """Create a new beneficiary"""
    if request.method == 'POST':
        form = BeneficiaryForm(request.POST, request.FILES)
        if form.is_valid():
            beneficiary = form.save()
            messages.success(request, 'Beneficiary created successfully!')
            return redirect('beneficiary_detail', id=beneficiary.id)
    else:
        form = BeneficiaryForm()
    
    context = {
        'form': form,
        'title': 'Add Beneficiary',
    }
    return render(request, 'program/beneficiary_form.html', context)


def beneficiary_update(request, id):
    """Update an existing beneficiary"""
    beneficiary = get_object_or_404(Beneficiary, id=id)
    
    if request.method == 'POST':
        form = BeneficiaryForm(request.POST, request.FILES, instance=beneficiary)
        if form.is_valid():
            form.save()
            messages.success(request, 'Beneficiary updated successfully!')
            return redirect('beneficiary_detail', id=beneficiary.id)
    else:
        form = BeneficiaryForm(instance=beneficiary)
    
    context = {
        'form': form,
        'beneficiary': beneficiary,
        'title': 'Edit Beneficiary',
    }
    return render(request, 'program/beneficiary_form.html', context)


def beneficiary_delete(request, id):
    """Delete a beneficiary"""
    beneficiary = get_object_or_404(Beneficiary, id=id)
    
    if request.method == 'POST':
        beneficiary.delete()
        messages.success(request, 'Beneficiary deleted successfully!')
        return redirect('home')
    
    context = {
        'beneficiary': beneficiary,
    }
    return render(request, 'program/beneficiary_confirm_delete.html', context)

    # VISION & HELP PAGES

def our_vision(request):
    """Our vision page"""
    return render(request, 'program/our_vision.html')

def help(request):
    """Help page"""
    return render(request, 'program/help.html')

def upcoming_updates(request):
    """Upcoming updates page"""
    return render(request, 'program/upcoming_update.html')


# =====================
# AJAX API ENDPOINTS
# =====================

@require_http_methods(["GET"])
def search_beneficiaries_ajax(request):
    """AJAX endpoint to search beneficiaries for Select2"""
    search_query = request.GET.get('q', '').strip()
    page = int(request.GET.get('page', 1))
    results_per_page = 20
    
    # Build queryset
    beneficiaries = Beneficiary.objects.all()
    
    # Filter by search query if provided
    if search_query:
        beneficiaries = beneficiaries.filter(
            Q(full_name__icontains=search_query) |
            Q(phone1__icontains=search_query) |
            Q(phone2__icontains=search_query) |
            Q(phone3__icontains=search_query) |
            Q(category__icontains=search_query)
        )
    
    # Calculate pagination
    total_count = beneficiaries.count()
    start = (page - 1) * results_per_page
    end = start + results_per_page
    
    # Get paginated results
    paginated_beneficiaries = beneficiaries[start:end]
    
    # Format response for Select2
    results = []
    for beneficiary in paginated_beneficiaries:
        results.append({
            'id': beneficiary.id,
            'text': f"{beneficiary.full_name} ({beneficiary.category}) - {beneficiary.phone1}"
        })
    
    return JsonResponse({
        'results': results,
        'pagination': {
            'more': end < total_count
        }
    })


# =====================
# PROGRAM INTERACTION VIEWS
# =====================

@login_required
def program_like(request, program_id):
    """Toggle like on a program"""
    program = get_object_or_404(Program, id=program_id)
    
    like, created = ProgramLike.objects.get_or_create(
        user=request.user,
        program=program
    )
    
    if not created:
        # Unlike if already liked
        like.delete()
        liked = False
    else:
        liked = True
    
    like_count = ProgramLike.objects.filter(program=program).count()
    
    return JsonResponse({
        'liked': liked,
        'like_count': like_count
    })


@login_required
def program_comment(request, program_id):
    """Add a comment to a program"""
    if request.method == 'POST':
        program = get_object_or_404(Program, id=program_id)
        content = request.POST.get('content', '').strip()
        
        if content:
            comment = ProgramComment.objects.create(
                user=request.user,
                program=program,
                content=content
            )
            
            return JsonResponse({
                'success': True,
                'comment': {
                    'id': comment.id,
                    'user': comment.user.username,
                    'content': comment.content,
                    'created_at': comment.created_at.strftime('%b %d, %Y %I:%M %p'),
                    'user_full_name': comment.user.get_full_name() or comment.user.username
                }
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def program_share(request, program_id):
    """Share a program"""
    program = get_object_or_404(Program, id=program_id)
    
    share, created = ProgramShare.objects.get_or_create(
        user=request.user,
        program=program
    )
    
    if created:
        share_count = ProgramShare.objects.filter(program=program).count()
        return JsonResponse({
            'shared': True,
            'share_count': share_count
        })
    
    return JsonResponse({'shared': False, 'error': 'Already shared'})


@login_required
def delete_comment(request, comment_id):
    """Delete a comment (only by comment author)"""
    comment = get_object_or_404(ProgramComment, id=comment_id)
    
    if comment.user != request.user:
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    comment.delete()
    return JsonResponse({'success': True})


# =====================
# TICKET VIEWS
# =====================

def beneficiary_ticket(request, beneficiary_id, program_id):
    """Generate a printable ticket for a beneficiary's program participation"""
    beneficiary = get_object_or_404(Beneficiary, id=beneficiary_id)
    program = get_object_or_404(Program, id=program_id)
    
    # Check if beneficiary is actually enrolled in this program
    if not program.beneficiaries.filter(id=beneficiary_id).exists():
        messages.error(request, 'This beneficiary is not enrolled in the selected program.')
        return redirect('beneficiary_detail', id=beneficiary_id)
    
    context = {
        'beneficiary': beneficiary,
        'program': program,
        'ticket_number': f"{program.id:04d}-{beneficiary.id:04d}",
        'generated_at': timezone.now(),
        'auto_print': request.GET.get('print') == '1',  # Enable auto-print only for actual print requests
    }
    
    # If it's a print request, render the print template
    if request.GET.get('print') == '1':
        return render(request, 'program/ticket_print.html', context)
    
    # Otherwise, show the ticket preview
    return render(request, 'program/ticket.html', context) 