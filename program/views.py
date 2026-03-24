from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Program, Beneficiary
from .forms import ProgramForm, BeneficiaryForm


# =====================
# PROGRAM VIEWS
# =====================

def home(request):
    """List all programs with search functionality"""
    programs = Program.objects.all()
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

    context = {
        'programs': programs,
        'beneficiaries': beneficiaries,
        'search_query': search_query,
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
    program = Program.objects.get(id=id)
    beneficiaries = program.beneficiaries.all()

    context = {
        'program': program,
        'beneficiaries': beneficiaries,
    }
    return render(request, 'program/program_detail.html', context)


def program_create(request):
    """Create a new program"""
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

    context = {
        'beneficiary': beneficiary,
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