from posts.models import Post
from django.db.models import Q
import json
from rest_framework.generics import (
    ListAPIView,RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
    CreateAPIView,
    RetrieveUpdateAPIView
)

from .serializers import (
    PostListSerializer,
    PostUpdateSerializer,
    PostCreateSerializer,
    PostLikeSerializer,
    UsersLikedPostSerializer
)
from accounts.api.serializers import UserListSerializer
from rest_framework.permissions import (
    AllowAny,   
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework import status
from .permissions import  IsOwnerOrReadOnly
from .pagination import PostLimitPagination,PostPageNumberPagination
from posts.models import Like
from accounts.models import Follower
# This view lists all the post 
class PostListView(ListAPIView):
    serializer_class = PostListSerializer
    permisson_classes = [AllowAny]
    pagination_class = PostPageNumberPagination
    def get_queryset(self, *args,**kwargs):
        queryset_list = Post.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(caption__icontains=query)|
                Q(user__username__icontains=query)
            ).distinct()

        return queryset_list

class PostDetailView(RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class= PostListSerializer    
# View for creating new post
class PostCreateView(CreateAPIView):
    queryset = Post.objects.all()
    serializer_class= PostCreateSerializer
    permission_classes = [IsAuthenticated]
    def perform_create(self,serializer):
        serializer.save(user=self.request.user) 

#This view is used to update the post 
class PostUpdateView(RetrieveUpdateAPIView):
    queryset = Post.objects.all()
    serializer_class= PostUpdateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly]

# This view is used to delete the post
class PostDeleteView(DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class= PostUpdateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

# This View is used to like the post
class PostLikeCreateView(CreateAPIView):
    serializer_class = PostLikeSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request, pk,format=None):
        user = self.request.user
        post_ = Post.objects.get(id=self.kwargs['pk'])
        try:
            like = Like.objects.get(account=user.account,post=post_)
        except:
            like = None
        if not like:
            serializer = PostLikeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(account=user.account,post=post_)
                return Response('LIKED', status = status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            like.delete()
            return Response('DISLIKED')
        


# This view is used to get all the users who like the post         
class PostLikeListView(ListAPIView):
    serializer_class = UsersLikedPostSerializer
    def get_queryset(self, *args, **kwargs):
        post = Post.objects.get(id=self.kwargs['pk'])
        queryset = post.like_set.all()
        return queryset
        
from datetime import date
today = date.today()
class HomeView(ListAPIView):
    serializer_class = PostListSerializer
    def get(self,request,*args,**kwargs):
        if request.user.is_authenticated:
            user = request.user
            account = user.account
            following = Follower.objects.filter(following_user=user)
            if len(following)>0:
                posts = list()
                for u in following:
                    print(u.following_user)
                    u_posts = u.followed_user.post_set.all()
                    print(u_posts)
                    for post in u_posts:
                        posts.append(post)
                data = {
                    "posts":posts
                }
                json.dumps(data)
                print(data)
                return Response(data,status.HTTP_200_OK)
            else:
                return Response('You do not following any one',status.HTTP_204_NO_CONTENT)
        else:
            return Response('Not Authenticated',status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
