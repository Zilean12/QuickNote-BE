from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from .models import Note
from .serializers import NoteSerializer
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache

class NoteListCreateView(generics.ListCreateAPIView):

    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    throttle_scope = 'notes'

    def get_queryset(self):
        cache_key = 'notes_all'
        queryset = cache.get(cache_key)
        if not queryset:
            queryset = Note.objects.all().order_by('-updated')
            cache.set(cache_key, queryset, timeout=60*15)
        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'status': 'success',
            'count': len(response.data),
            'results': response.data
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            cache.delete('notes_all')
            return Response({
                'status': 'success',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({
                'status': 'error',
                'errors': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)


class NoteRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
 
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'pk'
    throttle_scope = 'notes'

    def get_object(self):
        pk = self.kwargs.get('pk')
        cache_key = f'note_{pk}'
        note = cache.get(cache_key)
        if not note:
            try:
                note = Note.objects.get(pk=pk)
                cache.set(cache_key, note, timeout=60*15)
            except Note.DoesNotExist:
                raise NotFound(_('Note not found'))
        return note

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({
                'status': 'success',
                'data': serializer.data
            })
        except NotFound as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        """
        PUT handler - full update (all fields required)
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            cache.delete('notes_all')
            cache.delete(f'note_{instance.pk}')
            
            return Response({
                'status': 'success',
                'data': serializer.data
            })
        except ValidationError as e:
            return Response({
                'status': 'error',
                'errors': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)
        except NotFound as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            
            cache.delete('notes_all')
            cache.delete(f'note_{instance.pk}')
            
            return Response({
                'status': 'success',
                'message': _('Note deleted successfully')
            }, status=status.HTTP_204_NO_CONTENT)
        except NotFound as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_404_NOT_FOUND)