from django.test import TestCase, Client
from django.urls import reverse
from django.utils.formats import date_format 
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Note
from .serializers import NoteSerializer
import json
from django.conf import settings
from datetime import datetime

User = get_user_model()

class NoteModelTestCase(TestCase):
    """Test suite for the Note model"""
    
    @classmethod
    def setUpTestData(cls):
        """Set up non-modified data for all test methods"""
        cls.note = Note.objects.create(body="Initial test note content")

    def test_model_fields(self):
        """Test all model fields and their attributes"""
        field_label = self.note._meta.get_field('body').verbose_name
        self.assertEqual(field_label, 'body')
        
        max_length = self.note._meta.get_field('body').max_length
        self.assertIsNone(max_length)  # TextField has no max_length
        
        auto_now = self.note._meta.get_field('updated').auto_now
        self.assertTrue(auto_now)
        
        auto_now_add = self.note._meta.get_field('created').auto_now_add
        self.assertTrue(auto_now_add)

    def test_string_representation(self):
        """Test the string representation of the model"""
        self.assertEqual(str(self.note), self.note.body[:50] + '...' 
                         if len(self.note.body) > 50 else self.note.body)

    def test_verbose_names(self):
        """Test model's verbose names"""
        self.assertEqual(Note._meta.verbose_name, 'Note')
        self.assertEqual(Note._meta.verbose_name_plural, 'Notes')

    def test_default_ordering(self):
        """Test model's default ordering"""
        self.assertEqual(Note._meta.ordering, ['-updated'])

    def test_timestamps(self):
        """Test automatic timestamp fields"""
        self.assertIsNotNone(self.note.created)
        self.assertIsNotNone(self.note.updated)
        # Initially created and updated should be same
        self.assertEqual(self.note.created, self.note.updated)

    def test_update_changes_timestamp(self):
        """Test that updating changes the updated timestamp"""
        original_updated = self.note.updated
        self.note.body = "Updated content"
        self.note.save()
        self.assertNotEqual(original_updated, self.note.updated)
        self.assertGreater(self.note.updated, self.note.created)


class NoteAPITestCase(APITestCase):
    """Test suite for the API endpoints"""
    
    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole TestCase"""
        cls.note1 = Note.objects.create(body="First test note")
        cls.note2 = Note.objects.create(body="Second test note")
        cls.valid_payload = {'body': 'Valid note content'}
        cls.invalid_payload = {'body': ''}
        cls.list_url = reverse('note-list-create')
        cls.detail_url = reverse('note-retrieve-update-destroy', 
                               kwargs={'pk': cls.note1.pk})

    def setUp(self):
        """Set up for individual test methods"""
        self.client = APIClient()

    def test_get_all_notes(self):
        """Test GET all notes endpoint"""
        response = self.client.get(self.list_url)
        
        notes = Note.objects.all().order_by('-updated')
        serializer = NoteSerializer(notes, many=True)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(len(response.data), 2)

    def test_get_valid_single_note(self):
        """Test GET single note with valid ID"""
        response = self.client.get(self.detail_url)
        
        note = Note.objects.get(pk=self.note1.pk)
        serializer = NoteSerializer(note)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_invalid_single_note(self):
        """Test GET single note with invalid ID"""
        invalid_url = reverse('note-retrieve-update-destroy', 
                             kwargs={'pk': 9999})
        response = self.client.get(invalid_url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_valid_note(self):
        """Test POST to create a valid note"""
        response = self.client.post(
            self.list_url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Note.objects.count(), 3)
        
        # Verify the created note
        note = Note.objects.latest('created')
        self.assertEqual(note.body, self.valid_payload['body'])

    def test_create_invalid_note(self):
        """Test POST to create an invalid note"""
        response = self.client.post(
            self.list_url,
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Note.objects.count(), 2)

    def test_valid_update_note(self):
        """Test PUT to update a note with valid data"""
        updated_data = {'body': 'Updated note content'}
        response = self.client.put(
            self.detail_url,
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.note1.refresh_from_db()
        self.assertEqual(self.note1.body, updated_data['body'])

    def test_invalid_update_note(self):
        """Test PUT to update a note with invalid data"""
        response = self.client.put(
            self.detail_url,
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_note(self):
        """Test PATCH to partially update a note"""
        partial_data = {'body': 'Partially updated content'}
        response = self.client.patch(
            self.detail_url,
            data=json.dumps(partial_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.note1.refresh_from_db()
        self.assertEqual(self.note1.body, partial_data['body'])

    def test_delete_note(self):
        """Test DELETE a note"""
        response = self.client.delete(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Note.objects.count(), 1)
        self.assertFalse(Note.objects.filter(pk=self.note1.pk).exists())

    def test_notes_ordering(self):
        """Test that notes are properly ordered by updated timestamp"""
        # Update note2 to make it the most recently updated
        self.note2.body = "Updated second note"
        self.note2.save()
        
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], self.note2.id)
        self.assertEqual(response.data[1]['id'], self.note1.id)


class NoteAdminTestCase(TestCase):
    """Test suite for the Note admin interface"""
    
    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole TestCase"""
        cls.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        # Set a predefined date
        predefined_date = datetime(2025, 5, 15, 10, 48)
        cls.note = Note.objects.create(
            body="Test note for admin",
            created=predefined_date,
            updated=predefined_date
        )

    def setUp(self):
        """Set up for individual test methods"""
        self.client = Client()
        self.client.force_login(self.superuser)

    def test_note_list_display(self):
        """Test admin list display configuration"""
        url = reverse('admin:api_note_changelist')
        response = self.client.get(url)
        
        # Get admin-formatted datetimes
        created_formatted = date_format(self.note.created, "DATETIME_FORMAT")
        updated_formatted = date_format(self.note.updated, "DATETIME_FORMAT")
        
        self.assertContains(response, created_formatted)
        self.assertContains(response, updated_formatted)
    def test_note_search(self):
        """Test admin search functionality"""
        url = reverse('admin:api_note_changelist') + '?q=Test'
        response = self.client.get(url)
        
        self.assertContains(response, self.note.body)

    def test_note_filters(self):
        """Test admin filters"""
        url = reverse('admin:api_note_changelist') + '?created__year=' + str(self.note.created.year)
        response = self.client.get(url)
        
        self.assertContains(response, self.note.body)

    def test_note_add_page(self):
        """Test note add page renders correctly"""
        url = reverse('admin:api_note_add')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_note_change_page(self):
        """Test note change page renders correctly"""
        url = reverse('admin:api_note_change', args=[self.note.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)