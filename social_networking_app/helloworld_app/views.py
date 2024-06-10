import bcrypt
from django.shortcuts import render
from .models import User
from .serializers import FriendRequestSerializer, LoginSerializer, UserSerializer
from rest_framework import status
from mongoengine.queryset.visitor import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

# Create your views here.
# helloworld_app/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
class UserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hello_world(request):
    return Response({"message": "Hello, World!"})

@api_view(['POST'])
def log_in(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        try:
             user = User.objects.get(email=email)
             if check_password(password, user.password):
            #  if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'message':'Login successfully'
                }, status=status.HTTP_200_OK)
                # Generate token or any other login success logic
                return Response({'message': 'Login successful!'}, status=status.HTTP_200_OK)
             else:
                return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def check_password(pass1,pass2):
    if pass1==pass2:
        return True
    else:
        return False


        
    




@api_view(['POST'])
def signup(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def search_result(request):
    keyword = request.GET.get('keyword', '')
    if '@' in keyword:
        # Exact email match
        users = User.objects.filter(email=keyword)
    else:
        users = User.objects.filter(Q(name__icontains=keyword))
    paginator = UserPagination()
    paginated_users = paginator.paginate_queryset(users, request)
    serializer = UserSerializer(paginated_users, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
def send_friend_request(request):
    from_user_id = request.data.get('from_user_id')
    to_user_id = request.data.get('to_user_id')

    if not to_user_id:
        return Response({'detail': 'Recipient user ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        to_user = User.objects.get(id=to_user_id)
    except User.DoesNotExist:
        return Response({'detail': 'Recipient user not found.'}, status=status.HTTP_404_NOT_FOUND)

    if not from_user_id:
        return Response({'detail': 'Sender user ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        from_user = User.objects.get(id=from_user_id)
    except User.DoesNotExist:
        return Response({'detail': 'Sender user not found.'}, status=status.HTTP_404_NOT_FOUND)

    if from_user_id == to_user_id:
        return Response({'detail': 'You cannot send a friend request to yourself.'}, status=status.HTTP_400_BAD_REQUEST)

    if FriendRequest.objects(from_user=from_user, to_user=to_user).first():
        return Response({'detail': 'Friend request already sent.'}, status=status.HTTP_400_BAD_REQUEST)

    friend_request = FriendRequest(from_user=from_user, to_user=to_user)
    friend_request.save()

    return Response({'detail': 'Friend request sent.'}, status=status.HTTP_201_CREATED)




@api_view(['POST'])
def accept_friend_request(request):
    try:
        request_id=request.data.get('request_id')
        friend_request = FriendRequest.objects.get(id=request_id)
    except FriendRequest.DoesNotExist:
        return Response({'detail': 'Friend request not found.'}, status=status.HTTP_404_NOT_FOUND)

    friend_request.accepted = True
    friend_request.save()
    return Response({'detail': 'Friend request accepted.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def reject_friend_request(request):
    try:
        request_id=request.data.get('request_id')
        friend_request = FriendRequest.objects.get(id=request_id)
    except FriendRequest.DoesNotExist:
        return Response({'detail': 'Friend request not found.'}, status=status.HTTP_404_NOT_FOUND)

    friend_request.delete()
    return Response({'detail': 'Friend request rejected.'}, status=status.HTTP_200_OK)

# @api_view(['GET'])
# def list_friends(request):
#     user_id = request.query_params.get('user_id')
    
#     if not user_id:
#         return Response({'detail': 'User ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         user = User.objects.get(id=user_id)
#     except User.DoesNotExist:
#         return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

#     friends = User.objects.filter(friends__from_user=user, friends__accepted=True)
#     serializer = UserSerializer(friends, many=True)
#     return Response(serializer.data)

@api_view(['GET'])
def list_friends(request):
    to_user_id = request.query_params.get('to_user_id')
    
    if not to_user_id:
        return Response({'detail': 'User ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        to_user = User.objects.get(id=to_user_id)
    except User.DoesNotExist:
        return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    accepted_requests = FriendRequest.objects.filter(to_user=to_user, accepted=True)
    # print("line137"+accepted_requests)
    # try:
    #     print("line137"+accepted_requests)
    # except FriendRequest.DoesNotExist:
    #     print("not expenct")
    # Print each accepted request
    for request in accepted_requests:
        print(f'From: {request.from_user}, To: {request.to_user}, Accepted: {request.accepted}, Timestamp: {request.timestamp}')



    serializer = FriendRequestSerializer(accepted_requests, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def list_of_prnding_friends(request):
    to_user_id = request.query_params.get('to_user_id')
    
    if not to_user_id:
        return Response({'detail': 'User ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        to_user = User.objects.get(id=to_user_id)
    except User.DoesNotExist:
        return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    accepted_requests = FriendRequest.objects.filter(to_user=to_user, accepted=False)
    # print("line137"+accepted_requests)
    # try:
    #     print("line137"+accepted_requests)
    # except FriendRequest.DoesNotExist:
    #     print("not expenct")
    # Print each accepted request
    for request in accepted_requests:
        print(f'From: {request.from_user}, To: {request.to_user}, Accepted: {request.accepted}, Timestamp: {request.timestamp}')



    serializer = FriendRequestSerializer(accepted_requests, many=True)
    return Response(serializer.data)

