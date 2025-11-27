from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer, LogoutSerializer

User = get_user_model()


class RegisterView(APIView):
	def post(self, request):
		data = request.data
		serializer = RegisterSerializer(data=data)

		if serializer.is_valid(raise_exception=True):
			serializer.save()

			return Response({'message': 'Successfully registered'}, status.HTTP_200_OK)



class LogoutView(GenericAPIView):
	serializer_class = LogoutSerializer
	permission_classes = [IsAuthenticated]

	def post(self, request):
		serializer = self.serializer_class(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()

		return Response({'message': 'Successfully logged out'}, status.HTTP_200_OK)