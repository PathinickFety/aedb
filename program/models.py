from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.utils import timezone


# -------------------------
# BENEFICIARY MODEL
# -------------------------

class Beneficiary(models.Model):

    CATEGORY_CHOICES = [
        ('poor', 'Poor People'),
        ('staff', 'Staff Member'),
        ('student', 'Madrassat Student'),
        ('teacher', 'Oustadh'),
        ('elder', 'Elder'),
        ('orphan', 'Orphan'),
        ('sick', 'Sick Person'),
        ('disabled', 'Disabled Person'),
        ('widow', 'Widow'),
        ('refugee', 'Refugee'),
        ('family_beneficiary', 'Family Member of Beneficiary'),
        ('family_staff', 'Family Member of Staff'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='beneficiary_profile',
        null=True,
        blank=True
    )

    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField(blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)

    gender = models.CharField(
        max_length=10,
        choices=[
            ("male", "Male"),
            ("female", "Female")
        ]
    )

    national_id = models.CharField(max_length=50, blank=True)

    phone1 = models.CharField(max_length=20)
    phone2 = models.CharField(max_length=20, blank=True)
    phone3 = models.CharField(max_length=20, blank=True)

    address = models.TextField()

    village = models.CharField(max_length=150, blank=True)
    district = models.CharField(max_length=150, blank=True)
    region = models.CharField(max_length=150, blank=True)

    family_size = models.PositiveIntegerField(default=1)

    monthly_income = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    occupation = models.CharField(max_length=150, blank=True)

    photo = models.ImageField(
        upload_to="beneficiaries/",
        blank=True,
        null=True
    )

    id_document = models.FileField(
        upload_to="beneficiaries/id_documents/",
        blank=True,
        null=True
    )

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES
    )

    remarks = models.TextField(blank=True)

    is_verified = models.BooleanField(default=False)
    is_needed_person = models.BooleanField(default=False)
    is_serious = models.BooleanField(default=False)
    is_muslim = models.BooleanField(default=True)

    participated_programs = models.PositiveIntegerField(default=0)
    # increase this count every time the beneficiary participates in a program to track their involvement and identify those who are most in need of assistance

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-update_at']
        permissions = [
            ('can_verify_beneficiary', 'Can verify beneficiary records'),
            ('can_mark_serious', 'Can mark beneficiary as serious'),
            ('can_mark_muslim', 'Can mark beneficiary as muslim')
        ]

    def get_verified_emoji(self):
        """Returns emoji for verification status"""
        return '✅' if self.is_verified else '❌'
    get_verified_emoji.short_description = 'Verified'

    def get_needed_person_emoji(self):
        """Returns emoji for whether person is in real need"""
        return '✅' if self.is_needed_person else '❌'
    get_needed_person_emoji.short_description = 'In Need'

    def get_serious_emoji(self):
        """Returns emoji for whether person follows instructions and rules"""
        return '✅' if self.is_serious else '❌'
    get_serious_emoji.short_description = 'Serious'

    def get_muslim_emoji(self):
        """Returns emoji for whether person is muslim (important for Zakaat, Sadaqah)"""
        return '☪️' if self.is_muslim else '❌'
    get_muslim_emoji.short_description = 'Muslim'

    @property
    def latest_verification(self):
        """Get the most recent verification record"""
        return self.verifications.first()
    
    @property
    def verification_status(self):
        """Get current verification status"""
        latest = self.latest_verification
        return latest.status if latest else 'unverified'

    def __str__(self):
        return self.full_name


class PoorBeneficiary(models.Model):

    beneficiary = models.OneToOneField(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name="poor_profile"
    )

    employment_status = models.CharField(max_length=100)

    income_source = models.CharField(max_length=150)

    monthly_income = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    house_type = models.CharField(max_length=100)

    house_owner = models.BooleanField(default=False)

    receives_government_help = models.BooleanField(default=False)

    number_of_children = models.PositiveIntegerField(default=0)

    has_food_shortage = models.BooleanField(default=False)

    debt_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    priority_score = models.PositiveIntegerField(default=0)
    
class StudentBeneficiary(models.Model):

    beneficiary = models.OneToOneField(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )

    madrassa_name = models.CharField(max_length=255)

    level = models.CharField(max_length=100)

    memorized_juz = models.PositiveIntegerField(default=0)

    school_name = models.CharField(max_length=255, blank=True)

    school_grade = models.CharField(max_length=100, blank=True)

    orphan = models.BooleanField(default=False)

    sponsor_name = models.CharField(max_length=255, blank=True)

    boarding = models.BooleanField(default=False)

    attendance_percentage = models.PositiveIntegerField(default=100)
    
class StaffBeneficiary(models.Model):

    beneficiary = models.OneToOneField(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name="staff_profile"
    )

    employee_id = models.CharField(max_length=50)

    department = models.CharField(max_length=100)

    position = models.CharField(max_length=100)

    employment_date = models.DateField()

    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    active = models.BooleanField(default=True)
    
class TeacherBeneficiary(models.Model):

    beneficiary = models.OneToOneField(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name="teacher_profile"
    )

    specialization = models.CharField(max_length=200)

    years_of_experience = models.PositiveIntegerField()

    qualification = models.CharField(max_length=200)

    teaches_quran = models.BooleanField(default=True)

    monthly_allowance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    

class ElderBeneficiary(models.Model):

    beneficiary = models.OneToOneField(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name="elder_profile"
    )

    lives_alone = models.BooleanField(default=False)

    mobility_problem = models.BooleanField(default=False)

    chronic_disease = models.BooleanField(default=False)

    caregiver_name = models.CharField(max_length=255, blank=True)

    receives_pension = models.BooleanField(default=False)

    pension_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    

class OrphanBeneficiary(models.Model):

    beneficiary = models.OneToOneField(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name="orphan_profile"
    )

    father_alive = models.BooleanField(default=False)

    mother_alive = models.BooleanField(default=True)

    guardian_name = models.CharField(max_length=255)

    guardian_phone = models.CharField(max_length=20)

    school_name = models.CharField(max_length=255)

    sponsor = models.CharField(max_length=255, blank=True)

    receives_monthly_support = models.BooleanField(default=False)
    
class SickBeneficiary(models.Model):

    beneficiary = models.OneToOneField(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name="medical_profile"
    )

    disease = models.CharField(max_length=255)

    hospital = models.CharField(max_length=255)

    doctor = models.CharField(max_length=255)

    treatment_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    needs_surgery = models.BooleanField(default=False)

    chronic = models.BooleanField(default=False)

    disability_caused = models.BooleanField(default=False)
    
class DisabledBeneficiary(models.Model):

    beneficiary = models.OneToOneField(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name="disability_profile"
    )

    disability_type = models.CharField(max_length=100)

    disability_percentage = models.PositiveIntegerField()

    uses_wheelchair = models.BooleanField(default=False)

    needs_assistant = models.BooleanField(default=False)

    can_work = models.BooleanField(default=True)
    
class WidowBeneficiary(models.Model):

    beneficiary = models.OneToOneField(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name="widow_profile"
    )

    husband_date_of_death = models.DateField()

    children = models.PositiveIntegerField(default=0)

    employed = models.BooleanField(default=False)

    monthly_income = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    receives_support = models.BooleanField(default=False)
    
class RefugeeBeneficiary(models.Model):

    beneficiary = models.OneToOneField(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name="refugee_profile"
    )

    country_of_origin = models.CharField(max_length=100)

    refugee_card_number = models.CharField(max_length=100)

    arrival_date = models.DateField()

    refugee_camp = models.CharField(max_length=255)

    has_permanent_home = models.BooleanField(default=False)

    employment_status = models.CharField(max_length=100)
    
class FamilyBeneficiary(models.Model):

    beneficiary = models.OneToOneField(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name="family_profile"
    )

    related_person = models.ForeignKey(
        Beneficiary,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    relationship = models.CharField(max_length=100)

    dependent = models.BooleanField(default=True)
    

# -------------------------# BENEFICIARY VERIFICATION MODEL
# -------------------------

class BeneficiaryVerification(models.Model):
    """Model for tracking beneficiary verification workflow"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    beneficiary = models.ForeignKey(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name='verifications'
    )
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='beneficiary_verifications'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    verification_notes = models.TextField(blank=True, null=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Beneficiary Verification'
        verbose_name_plural = 'Beneficiary Verifications'
        permissions = [
            ('can_approve_verification', 'Can approve beneficiary verifications'),
            ('can_reject_verification', 'Can reject beneficiary verifications'),
        ]
    
    def __str__(self):
        return f"{self.beneficiary.full_name} - {self.get_status_display()}"
    
    def approve(self, user, notes=None):
        """Approve the verification"""
        self.status = 'approved'
        self.verified_by = user
        self.verified_at = timezone.now()
        self.verification_notes = notes or self.verification_notes
        self.save()
        # Update beneficiary verification status
        self.beneficiary.is_verified = True
        self.beneficiary.save()
        # Notify beneficiary user (if any)
        try:
            from django.core.mail import send_mail
            recipient = self.beneficiary.user.email if self.beneficiary.user and self.beneficiary.user.email else None
            if recipient:
                subject = f"Your profile has been verified"
                message = f"Hello {self.beneficiary.full_name},\n\nYour beneficiary profile has been approved and marked as verified.\n\nNotes: {self.verification_notes or 'None'}"
                send_mail(subject, message, None, [recipient], fail_silently=True)
        except Exception:
            pass
    
    def reject(self, user, notes=None):
        """Reject the verification"""
        self.status = 'rejected'
        self.verified_by = user
        self.verified_at = timezone.now()
        self.verification_notes = notes or self.verification_notes
        self.save()
        # Update beneficiary verification status
        self.beneficiary.is_verified = False
        self.beneficiary.save()
        # Notify beneficiary user (if any)
        try:
            from django.core.mail import send_mail
            recipient = self.beneficiary.user.email if self.beneficiary.user and self.beneficiary.user.email else None
            if recipient:
                subject = f"Your profile verification was rejected"
                message = f"Hello {self.beneficiary.full_name},\n\nYour beneficiary profile verification request was rejected.\n\nNotes: {self.verification_notes or 'None'}"
                send_mail(subject, message, None, [recipient], fail_silently=True)
        except Exception:
            pass


# -------------------------  # PROGRAM MODEL
# -------------------------
class Program(models.Model):

    PROGRAM_TYPE_CHOICES = [
        ('zakaat', 'Zakaat Distribution'),
        ('food_pack', 'Food Pack Distribution'),
        ('iftar', 'Iftar Distribution'),
        ('sadaqah', 'Sadaqah'),
        ('clothing', 'Clothing Distribution'),
        ('school_supplies', 'School Supplies Distribution'),
        ('medical', 'Medical Assistance'),
        ('sponsorship', 'Sponsorship Program'),
        ('training', 'Training/Workshop'),
        ('hot meal', 'Hot Meal Distribution'),
        ('dawrah', 'Dawrah'),
        ('qurbani', 'Qurbani'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=255)
    program_type = models.CharField(
        max_length=20,
        choices=PROGRAM_TYPE_CHOICES
    )

    date = models.DateField()
    time = models.TimeField()
    place = models.CharField(max_length=255)

    responsible = models.CharField(max_length=255)
    # change this to ForeignKey(User) later when we have user accounts

    beneficiaries = models.ManyToManyField(
        Beneficiary,
        related_name='programs',
        blank=True
    )
    notes = models.TextField(blank=True, null=True)
    is_finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-update_at']
        permissions = [
            ('can_publish_program', 'Can publish programs'),
            ('can_view_program_stats', 'Can view program statistics')
        ]

    def __str__(self):
        return f"{self.name} - {self.date}"


# -------------------------  
# PROGRAM INTERACTION MODELS
# -------------------------

class ProgramLike(models.Model):
    """Model for program likes"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'program']  # One like per user per program

    def __str__(self):
        return f"{self.user.username} liked {self.program.name}"


class ProgramComment(models.Model):
    """Model for program comments"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.program.name}"


class ProgramShare(models.Model):
    """Model for program shares"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'program']  # One share per user per program

    def __str__(self):
        return f"{self.user.username} shared {self.program.name}"
    
    
