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
        ('orphan', 'Orphan kid'),
        ('sick', 'Sick Person'),
        ('disabled', 'Disabled Person'),
        ('widow', 'Widow'),
        ('refugee', 'Refugee'),
        ('family', 'Family member of a beneficiary'),
        ('family', 'Family member of staff'),
        ('other', 'Other'),
    ]

    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField(blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)  # Optional age field for easier sorting/filtering

    phone1 = models.CharField(max_length=20)
    phone2 = models.CharField(max_length=20, blank=True, null=True)
    phone3 = models.CharField(max_length=20, blank=True, null=True)

    address = models.TextField()
    family_size = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)]
    )

    photo = models.ImageField(
        upload_to='beneficiaries/',
        blank=True,
        null=True
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )
    remarks = models.TextField(blank=True, null=True)

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