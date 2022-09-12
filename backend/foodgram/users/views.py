from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.viewsets import CreateReadViewSet, ReadListViewSet

from .models import CustomUser, Subscription
from .serializers import (ChangePasswordSerializer, CustomUserSerializer,
                          SignUpSerializer, SubscriptionSerializer,
                          TokenSerializer)


class CustomUserViewSet(CreateReadViewSet):
    """Вьюсет данных пользователей"""
    queryset = CustomUser.objects.all().order_by('id')
    permission_classes = (AllowAny, )

    def get_serializer_class(self):
        if self.request.method in ('POST', ):
            return SignUpSerializer
        return CustomUserSerializer

    @action(methods=['get', ], detail=False,
            permission_classes=(IsAuthenticated, ))
    def me(self, request):
        """Метод, отвечающий за чтение пользователем
        собственных учетных данных"""
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post', ], detail=False,
            permission_classes=(IsAuthenticated, ))
    def set_password(self, request):
        """Метод, отвечающий за изменение пароля пользователем"""
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        old_password = serializer.validated_data.get('current_password')
        new_password = serializer.validated_data.get('new_password')
        user = request.user
        if user.password == old_password:
            user.password = new_password
            user.save()
            return Response(
                {"Пароль успешно изменен"},
                status=status.HTTP_200_OK
            )
        return Response(
            {"current_password": "Введен неверный текущий пароль"},
            status=status.HTTP_400_BAD_REQUEST
        )


class SubscriptionViewSet(ReadListViewSet):
    """Вьюсет для подписок на авторов"""
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        user = self.request.user
        return Subscription.objects.filter(user=user)

    def retrieve(self, request, pk=None):
        return Response(
            {"detail": "Страница не найдена."},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST', ])
@permission_classes((AllowAny, ))
def get_token(request):
    """Вью-функция, отвечающая за получение зарегистрированным
    пользователем токена для доступа к сайту"""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data.get('email')
    password = serializer.validated_data.get('password')
    new_user = get_object_or_404(CustomUser, email=email)

    if CustomUser.objects.filter(email=email, password=password).exists():
        if Token.objects.filter(user=new_user).exists():
            Token.objects.filter(user=new_user).delete()
        token = Token.objects.create(user=new_user)
        return Response({"auth_token": str(token)}, status=status.HTTP_200_OK)
    return Response(
        {"password": "Введен неверный пароль"},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST', ])
def delete_token(request):
    """Вью-функция, отвечающая за удаление токена"""
    request.auth.delete()


@api_view(['POST', 'DELETE', ])
def subscribe(request, user_id):
    """Вью-функция, отвечающая за подписку на авторов"""
    user = request.user
    author = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        if user == author:
            return Response(
                {"Нельзя подписаться на себя"},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif Subscription.objects.filter(user=user, author=author).exists():
            return Response(
                {"Вы уже подписаны"},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscription.objects.get_or_create(user=user, author=author)
        serializer = SubscriptionSerializer(
            get_object_or_404(Subscription, user=user, author=author)
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
    if Subscription.objects.filter(user=user, author=author).exists():
        Subscription.objects.filter(user=user, author=author).delete()
        return Response({"Успешная отписка"}, status=status.HTTP_200_OK)
    return Response(
        {"Вы не подписаны на данного пользователя"},
        status=status.HTTP_200_OK
    )
