from django.urls import path
from .views import accept_friend_request, hello_world, list_friends, list_of_prnding_friends, log_in, reject_friend_request, search_result, send_friend_request, signup
urlpatterns = [
    path('hello/', hello_world, name='hello_world'),
    path('login/', log_in, name='log_in'),
    path('signup/', signup, name='signup'),
    path('search/', search_result, name='search_result'),
    path('send/', send_friend_request, name='send_friend_request'),
    path('accept/', accept_friend_request, name='accept_friend_request'),
    path('reject/', reject_friend_request, name='reject_friend_request'),
    path('listOfFriends/', list_friends, name='list_friends'),
    path('listOfPendingFriends/',list_of_prnding_friends,name='list_of_prnding_friends')

]