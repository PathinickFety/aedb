from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.utils.html import format_html
from django.urls import reverse
from .models import Program, Beneficiary, BeneficiaryVerification


# Define a role-permission matrix
ROLE_PERMISSION_MATRIX = {
    'Admin': [
        'program.add_program', 'program.change_program', 'program.delete_program', 'program.view_program',
        'program.add_beneficiary', 'program.change_beneficiary', 'program.delete_beneficiary', 'program.view_beneficiary',
        'program.can_verify_beneficiary', 'program.can_mark_serious', 'program.can_mark_muslim',
        'program.can_publish_program', 'program.can_view_program_stats',
        'program.add_beneficiaryverification', 'program.change_beneficiaryverification', 'program.delete_beneficiaryverification', 'program.view_beneficiaryverification',
        'program.can_approve_verification', 'program.can_reject_verification'
    ],
    'Staff': [
        'program.add_program', 'program.change_program', 'program.view_program',
        'program.add_beneficiary', 'program.change_beneficiary', 'program.view_beneficiary',
        'program.can_verify_beneficiary', 'program.can_mark_serious', 'program.can_mark_muslim',
        'program.add_beneficiaryverification', 'program.change_beneficiaryverification', 'program.view_beneficiaryverification',
        'program.can_approve_verification', 'program.can_reject_verification'
    ],
    'Volunteer': [
        'program.view_program', 'program.view_beneficiary', 'program.view_beneficiaryverification'
    ]
}


def enforce_role_permissions(sender=None, **kwargs):
    """Ensure groups exist and their permissions are assigned."""
    for role, perms in ROLE_PERMISSION_MATRIX.items():
        group, created = Group.objects.get_or_create(name=role)
        if created:
            group.permissions.clear()
        for perm_code in perms:
            app_label, codename = perm_code.split('.')
            try:
                perm = Permission.objects.get(content_type__app_label=app_label, codename=codename)
                group.permissions.add(perm)
            except Permission.DoesNotExist:
                continue


class RoleAwareModelAdmin(admin.ModelAdmin):
    """Admin mixin that authorizes based on model permissions and user groups."""

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return request.user.has_perm(f'{self.model._meta.app_label}.view_{self.model._meta.model_name}')

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return request.user.has_perm(f'{self.model._meta.app_label}.add_{self.model._meta.model_name}')

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return request.user.has_perm(f'{self.model._meta.app_label}.change_{self.model._meta.model_name}')

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return request.user.has_perm(f'{self.model._meta.app_label}.delete_{self.model._meta.model_name}')

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}
        extra_context['role_matrix'] = ROLE_PERMISSION_MATRIX
        extra_context['current_user_roles'] = [g.name for g in request.user.groups.all()]
        return super().changelist_view(request, extra_context=extra_context)


class BeneficiaryAdmin(RoleAwareModelAdmin):
    list_display = [
        'full_name',
        'get_verified_emoji',
        'verification_status_display',
        'get_needed_person_emoji',
        'get_serious_emoji',
        'get_muslim_emoji',
        'category',
        'phone1',
        'created_at',
        'verification_actions'
    ]
    
    fieldsets = (
        ('Verification Status', {
            'fields': ('is_verified',)
        }),
        ('Personal Information', {
            'fields': ('full_name', 'date_of_birth', 'age', 'photo')
        }),
        ('Contact Information', {
            'fields': ('phone1', 'phone2', 'phone3', 'address')
        }),
        ('Beneficiary Details', {
            'fields': ('category', 'family_size', 'remarks')
        }),
        ('Status Flags', {
            'fields': ('is_needed_person', 'is_serious', 'is_muslim')
        }),
        ('Program Information', {
            'fields': ('participated_programs',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'update_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'update_at', 'participated_programs']
    search_fields = ['full_name', 'phone1', 'phone2', 'phone3']
    list_filter = ['category', 'is_verified', 'is_needed_person', 'is_serious', 'is_muslim', 'created_at']
    
    def verification_status_display(self, obj):
        """Display current verification status"""
        status = obj.verification_status
        if status == 'approved':
            return format_html('<span style="color: green;">✅ Approved</span>')
        elif status == 'rejected':
            return format_html('<span style="color: red;">❌ Rejected</span>')
        elif status == 'pending':
            return format_html('<span style="color: orange;">⏳ Pending</span>')
        else:
            return format_html('<span style="color: gray;">❓ Unverified</span>')
    verification_status_display.short_description = 'Verification Status'
    
    def verification_actions(self, obj):
        """Display verification workflow actions"""
        if obj.verification_status == 'unverified':
            create_url = reverse('admin:program_beneficiaryverification_add') + f'?beneficiary={obj.pk}'
            return format_html('<a class="button" href="{}">Request Verification</a>', create_url)
        elif obj.verification_status == 'pending':
            return format_html('<span style="color: orange;">Awaiting Review</span>')
        else:
            latest_verification = obj.latest_verification
            if latest_verification:
                view_url = reverse('admin:program_beneficiaryverification_change', args=[latest_verification.pk])
                return format_html('<a href="{}">View Details</a>', view_url)
        return '-'
    verification_actions.short_description = 'Verification Actions'


class ProgramAdmin(RoleAwareModelAdmin):
    list_display = ['name', 'program_type', 'date', 'place', 'is_finished', 'created_at']
    list_filter = ['program_type', 'is_finished', 'date']
    search_fields = ['name', 'place', 'responsible']


class BeneficiaryVerificationAdmin(RoleAwareModelAdmin):
    list_display = [
        'beneficiary',
        'status',
        'verified_by',
        'verified_at',
        'created_at',
        'verification_actions'
    ]
    list_filter = ['status', 'verified_at', 'created_at']
    search_fields = ['beneficiary__full_name', 'verification_notes']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Verification Details', {
            'fields': ('beneficiary', 'status', 'verified_by', 'verified_at')
        }),
        ('Notes', {
            'fields': ('verification_notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def verification_actions(self, obj):
        """Display action buttons for verification workflow"""
        if obj.status == 'pending':
            approve_url = reverse('admin:program_beneficiaryverification_change', args=[obj.pk])
            return format_html(
                '<a class="button" href="{}?action=approve">Approve</a> '
                '<a class="button" href="{}?action=reject">Reject</a>',
                approve_url, approve_url
            )
        return obj.get_status_display()
    verification_actions.short_description = 'Actions'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('beneficiary', 'verified_by')
    
    def save_model(self, request, obj, form, change):
        """Handle verification workflow actions"""
        action = request.GET.get('action')
        if action == 'approve' and obj.status == 'pending':
            obj.approve(request.user)
        elif action == 'reject' and obj.status == 'pending':
            obj.reject(request.user)
        else:
            super().save_model(request, obj, form, change)


admin.site.register(Beneficiary, BeneficiaryAdmin)
admin.site.register(Program, ProgramAdmin)
admin.site.register(BeneficiaryVerification, BeneficiaryVerificationAdmin)