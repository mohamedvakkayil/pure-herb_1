"""Create Admin, Manager, Staff, Viewer groups and assign permissions."""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from journal.models import JournalEntry, ApprovalRequest, UserRequest, ActivityLog


class Command(BaseCommand):
    help = 'Create Admin, Manager, Staff, Viewer groups with appropriate permissions'

    def handle(self, *args, **options):
        # Create groups
        admin_grp, _ = Group.objects.get_or_create(name='Admin')
        manager_grp, _ = Group.objects.get_or_create(name='Manager')
        staff_grp, _ = Group.objects.get_or_create(name='Staff')
        viewer_grp, _ = Group.objects.get_or_create(name='Viewer')

        # JournalEntry permissions
        ct_journal = ContentType.objects.get_for_model(JournalEntry)
        add_journal = Permission.objects.get(codename='add_journalentry', content_type=ct_journal)
        change_journal = Permission.objects.get(codename='change_journalentry', content_type=ct_journal)
        delete_journal = Permission.objects.get(codename='delete_journalentry', content_type=ct_journal)
        view_journal = Permission.objects.get(codename='view_journalentry', content_type=ct_journal)

        # Staff and Manager: add, change, delete, view
        staff_grp.permissions.add(add_journal, change_journal, delete_journal, view_journal)
        manager_grp.permissions.add(add_journal, change_journal, delete_journal, view_journal)

        # Viewer: view only
        viewer_grp.permissions.add(view_journal)

        # Admin gets all permissions via is_staff/superuser or we add all
        admin_grp.permissions.add(add_journal, change_journal, delete_journal, view_journal)

        # ApprovalRequest and UserRequest for admin/manager if needed
        ct_approval = ContentType.objects.get_for_model(ApprovalRequest)
        for perm in Permission.objects.filter(content_type=ct_approval):
            admin_grp.permissions.add(perm)
            manager_grp.permissions.add(perm)

        ct_user_req = ContentType.objects.get_for_model(UserRequest)
        for perm in Permission.objects.filter(content_type=ct_user_req):
            admin_grp.permissions.add(perm)
            manager_grp.permissions.add(perm)

        ct_activity = ContentType.objects.get_for_model(ActivityLog)
        for perm in Permission.objects.filter(content_type=ct_activity):
            admin_grp.permissions.add(perm)
            manager_grp.permissions.add(perm)

        self.stdout.write(self.style.SUCCESS('Groups created/updated: Admin, Manager, Staff, Viewer'))
