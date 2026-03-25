from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User


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

    is_needed_person = models.BooleanField(default=False)
    is_serious = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-update_at']

    def __str__(self):
        return self.full_name


# -------------------------
# PROGRAM MODEL
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