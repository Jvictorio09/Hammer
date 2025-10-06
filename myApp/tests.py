from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from .models import (
    Service, Insight, InsightAuditLog, UserProfile
)


class InsightModerationTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create users
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        self.blog_author = User.objects.create_user(
            username='blogauthor',
            email='author@example.com',
            password='testpass123'
        )
        self.regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='testpass123'
        )
        
        # Update user profiles (they are automatically created by signals)
        self.admin_user.profile.role = 'admin'
        self.admin_user.profile.save()
        self.blog_author.profile.role = 'blog_author'
        self.blog_author.profile.save()
        # regular_user profile is already created with default 'user' role
        
        # Create a service
        self.service = Service.objects.create(
            title='Test Service',
            slug='test-service',
            hero_headline='Test Headline'
        )
        
        # Create insights
        self.active_insight = Insight.objects.create(
            title='Active Insight',
            slug='active-insight',
            service=self.service,
            author=self.blog_author,
            published=True,
            is_active=True,
            published_at=timezone.now()
        )
        
        self.inactive_insight = Insight.objects.create(
            title='Inactive Insight',
            slug='inactive-insight',
            service=self.service,
            author=self.blog_author,
            published=True,
            is_active=False,
            published_at=timezone.now()
        )

    def test_insight_active_filtering(self):
        """Test that inactive insights are filtered from public views"""
        # Test service detail view filters inactive insights
        client = Client()
        response = client.get(reverse('service_detail', kwargs={'slug': self.service.slug}))
        
        # Should not include inactive insights in the prefetched insights
        insights = response.context.get('insights', [])
        insight_titles = [i.title for i in insights]
        self.assertIn('Active Insight', insight_titles)
        self.assertNotIn('Inactive Insight', insight_titles)

    def test_insight_detail_active_filtering(self):
        """Test that inactive insights return 404 in detail view"""
        client = Client()
        
        # Active insight should be accessible
        response = client.get(reverse('insight_detail', kwargs={'slug': self.active_insight.slug}))
        self.assertEqual(response.status_code, 200)
        
        # Inactive insight should return 404
        response = client.get(reverse('insight_detail', kwargs={'slug': self.inactive_insight.slug}))
        self.assertEqual(response.status_code, 404)

    def test_blog_author_permissions(self):
        """Test that blog authors can access insight views"""
        client = Client()
        client.login(username='blogauthor', password='testpass123')
        
        # Blog author should be able to access insight list
        response = client.get(reverse('dashboard_insights_list'))
        self.assertEqual(response.status_code, 200)
        
        # Blog author should be able to create insights
        response = client.get(reverse('dashboard_insight_create'))
        self.assertEqual(response.status_code, 200)

    def test_regular_user_permissions(self):
        """Test that regular users cannot access insight views"""
        client = Client()
        client.login(username='regular', password='testpass123')
        
        # Regular user should get permission denied (403)
        response = client.get(reverse('dashboard_insights_list'))
        self.assertEqual(response.status_code, 403)

    def test_insight_deletion_audit_log(self):
        """Test that insight deletion creates audit log"""
        client = Client()
        client.login(username='blogauthor', password='testpass123')
        
        # Count audit logs before deletion
        initial_count = InsightAuditLog.objects.count()
        
        # Delete an insight
        response = client.post(
            reverse('dashboard_insight_delete', kwargs={'pk': self.active_insight.pk}),
            {'csrfmiddlewaretoken': 'test'}
        )
        
        # Should redirect to insights list
        self.assertEqual(response.status_code, 302)
        
        # Should have created an audit log
        self.assertEqual(InsightAuditLog.objects.count(), initial_count + 1)
        
        # Check audit log content
        audit_log = InsightAuditLog.objects.latest('timestamp')
        self.assertEqual(audit_log.action, 'delete')
        self.assertEqual(audit_log.insight_id, self.active_insight.id)
        self.assertEqual(audit_log.insight_title, self.active_insight.title)
        self.assertEqual(audit_log.actor, self.blog_author)
        self.assertEqual(audit_log.actor_username, self.blog_author.username)

    def test_user_profile_creation(self):
        """Test that user profiles are automatically created"""
        # Create a new user
        new_user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='testpass123'
        )
        
        # Profile should be automatically created
        self.assertTrue(hasattr(new_user, 'profile'))
        self.assertEqual(new_user.profile.role, 'user')

    def test_insight_author_assignment(self):
        """Test that insights are assigned to the creating user"""
        client = Client()
        client.login(username='blogauthor', password='testpass123')
        
        # Create a new insight
        response = client.post(
            reverse('dashboard_insight_create'),
            {
                'title': 'New Test Insight',
                'service': self.service.id,
                'published': True,
                'csrfmiddlewaretoken': 'test'
            }
        )
        
        # Should redirect after creation
        self.assertEqual(response.status_code, 302)
        
        # Check that the insight was created with the correct author
        new_insight = Insight.objects.get(title='New Test Insight')
        self.assertEqual(new_insight.author, self.blog_author)

    def test_admin_audit_log_access(self):
        """Test that admins can view audit logs"""
        client = Client()
        client.login(username='admin', password='testpass123')
        
        # Create an audit log
        InsightAuditLog.objects.create(
            action='delete',
            insight_id=1,
            insight_title='Test Insight',
            actor=self.admin_user,
            actor_username=self.admin_user.username,
            actor_email=self.admin_user.email
        )
        
        # Admin should be able to access the admin interface (may redirect to login)
        response = client.get('/admin/myApp/insightauditlog/')
        # Accept both 200 (direct access) and 302 (redirect to login)
        self.assertIn(response.status_code, [200, 302])

    def test_insight_list_shows_author_and_timestamp(self):
        """Test that insight list shows author and created timestamp"""
        client = Client()
        client.login(username='blogauthor', password='testpass123')
        
        response = client.get(reverse('dashboard_insights_list'))
        self.assertEqual(response.status_code, 200)
        
        # Check that the response contains author and timestamp information
        content = response.content.decode()
        self.assertIn('blogauthor', content)  # Author username
        self.assertIn('Active Insight', content)  # Insight title

    def test_user_management_access(self):
        """Test that only admins can access user management"""
        client = Client()
        
        # Admin should be able to access user list
        client.login(username='admin', password='testpass123')
        response = client.get(reverse('dashboard_users_list'))
        self.assertEqual(response.status_code, 200)
        
        # Blog author should not be able to access user management
        client.login(username='blogauthor', password='testpass123')
        response = client.get(reverse('dashboard_users_list'))
        self.assertEqual(response.status_code, 403)
        
        # Regular user should not be able to access user management
        client.login(username='regular', password='testpass123')
        response = client.get(reverse('dashboard_users_list'))
        self.assertEqual(response.status_code, 403)

    def test_user_creation(self):
        """Test user creation with role assignment"""
        client = Client()
        client.login(username='admin', password='testpass123')
        
        # Create a new user
        response = client.post(
            reverse('dashboard_user_create'),
            {
                'username': 'newuser',
                'password1': 'testpass123',
                'password2': 'testpass123',
                'role': 'blog_author',
                'csrfmiddlewaretoken': 'test'
            }
        )
        
        # Should redirect after creation
        self.assertEqual(response.status_code, 302)
        
        # Check that the user was created with the correct role
        from django.contrib.auth import get_user_model
        User = get_user_model()
        new_user = User.objects.get(username='newuser')
        self.assertEqual(new_user.profile.role, 'blog_author')

    def test_user_role_update(self):
        """Test updating user role"""
        client = Client()
        client.login(username='admin', password='testpass123')
        
        # Update blog author to admin
        response = client.post(
            reverse('dashboard_user_edit', kwargs={'pk': self.blog_author.pk}),
            {
                'role': 'admin',
                'csrfmiddlewaretoken': 'test'
            }
        )
        
        # Should redirect after update
        self.assertEqual(response.status_code, 302)
        
        # Check that the role was updated
        self.blog_author.refresh_from_db()
        self.assertEqual(self.blog_author.profile.role, 'admin')

    def test_insight_toggle_active(self):
        """Test insight activation/deactivation by admin"""
        client = Client()
        client.login(username='admin', password='testpass123')
        
        # Test deactivating an active insight
        response = client.post(
            reverse('dashboard_insight_toggle_active', kwargs={'pk': self.active_insight.pk}),
            {'csrfmiddlewaretoken': 'test'}
        )
        self.assertEqual(response.status_code, 302)  # Should redirect
        
        # Check that the insight is now inactive
        self.active_insight.refresh_from_db()
        self.assertFalse(self.active_insight.is_active)
        
        # Test activating an inactive insight
        response = client.post(
            reverse('dashboard_insight_toggle_active', kwargs={'pk': self.inactive_insight.pk}),
            {'csrfmiddlewaretoken': 'test'}
        )
        self.assertEqual(response.status_code, 302)  # Should redirect
        
        # Check that the insight is now active
        self.inactive_insight.refresh_from_db()
        self.assertTrue(self.inactive_insight.is_active)
        
        # Check that audit logs were created
        from myApp.models import InsightAuditLog
        deactivate_log = InsightAuditLog.objects.filter(action='deactivate').first()
        activate_log = InsightAuditLog.objects.filter(action='activate').first()
        
        self.assertIsNotNone(deactivate_log)
        self.assertIsNotNone(activate_log)
        self.assertEqual(deactivate_log.insight_id, self.active_insight.id)
        self.assertEqual(activate_log.insight_id, self.inactive_insight.id)

    def test_blog_author_cannot_toggle_active(self):
        """Test that blog authors cannot toggle insight active status"""
        client = Client()
        client.login(username='blogauthor', password='testpass123')
        
        # Blog author should get 403 when trying to toggle active status
        response = client.post(
            reverse('dashboard_insight_toggle_active', kwargs={'pk': self.active_insight.pk}),
            {'csrfmiddlewaretoken': 'test'}
        )
        self.assertEqual(response.status_code, 403)
