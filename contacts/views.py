from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Contact
from .serializers import ContactSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

class ContactCreateView(APIView):
    http_method_names = ['post']  # только POST

    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            contact = serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class ContactFilteredListView(APIView):
    http_method_names = ['get']  # только GET
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['last_name', 'first_name', 'email']
    filterset_fields = ['city']

    def get(self, request):
        queryset = Contact.objects.all()

        city = request.query_params.get('city')
        if city:
            queryset = queryset.filter(address__city=city)

        search = request.query_params.get('search')
        if search:
            queryset = (
                queryset.filter(last_name__icontains=search) |
                queryset.filter(first_name__icontains=search) |
                queryset.filter(email__icontains=search)
            )

        serializer = ContactSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)