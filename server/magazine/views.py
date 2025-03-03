from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework import permissions
from .serializers import *
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser, FormParser



class BlogListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, *args, **kwargs):
        posts = BlogPost.objects.filter(is_published=True)
        serializer = BlogPostSerializer(posts, many = True)
        return Response(serializer.data, status = status.HTTP_200_OK)
        
class BlogCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]


    def post(self, request):
        serializer = BlogPostSerializer(data=request.data)
        if serializer.is_valid():
            # Handling Cover image
            cover_image = request.FILES.get('cover_image')
            if cover_image:
                blog = serializer.save(user=request.user, cover_image=cover_image)
            else:
                blog = serializer.save(user=request.user)
            
            # Handling Other images
            blog = serializer.save(user=request.user)
            images = request.FILES.getlist('images')
            for image in images:
                Image.objects.create(blog=blog, image=image)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BlogDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self, slug):
        try:
            return BlogPost.objects.get(slug = slug)
        except BlogPost.DoesNotExist:
            return None

    def get(self, request, slug, *args, **kwargs):

        post = self.get_object(slug)
        if post is None:
            return Response({'error': 'Post not found'}, status = status.HTTP_404_NOT_FOUND)
        serializer = BlogPostSerializer(post)
        
        return Response(serializer.data, status = status.HTTP_200_OK)

    def put(self, request, slug, *args, **kwargs):
        post = self.get_object(slug)
        if post is None:
            return Response({'error': 'Post not found'}, status = status.HTTP_404_NOT_FOUND)
        data = {
        'user': request.user.id,
        'likes_count': post.likes_count
    }

    # Update data if provided in request
        title = request.data.get('title')
        if title is not None:
            data['title'] = title

        content = request.data.get('content')
        if content is not None:
            data['content'] = content

        cover_image = request.data.get('cover_image')
        if cover_image is not None:
            data['cover_image'] = cover_image

        images = request.data.get('images')
        if images is not None:
            data['images'] = images

        
        serializer = BlogPostSerializer(post, data = data, partial = True)
        if serializer.is_valid():
            if post.user.id == request.user.id:
                serializer.save()
                return Response(serializer.data, status = status.HTTP_200_OK)
            return Response({"error": "You are not authorized to edit this post"}, status = status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug, *args, **kwargs):
        post = self.get_object(slug)
        if post is None:
            return Response({'error': 'Post not found'}, status = status.HTTP_404_NOT_FOUND)
        if post.user.id == request.user.id:
            post.delete()
            return Response({"res": "Object deleted!"}, status = status.HTTP_200_OK)
        return Response({"error": "You are not authorized to delete this post"}, status = status.HTTP_401_UNAUTHORIZED)

class UserPostAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, username, *args, **kwargs):
        user = User.objects.filter(username = username).first()
        if user is None:
            return Response({'error': 'User not found'}, status = status.HTTP_404_NOT_FOUND)
        posts = BlogPost.objects.filter(user = user)
        serializer = BlogPostSerializer(posts, many = True)
        return Response(serializer.data, status = status.HTTP_200_OK)
    
class CategoryBlogView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, category):
        if category.lower() == 'all':
            blogs = BlogPost.objects.all()
        else:
            blogs = BlogPost.objects.filter(category__iexact=category)
        serializer = BlogPostSerializer(blogs, many=True)
        return Response(serializer.data)
    
class LikesAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]


    def post(self, request, slug):
        try:
            post = BlogPost.objects.get(slug=slug)
            user = request.user 
            
            # Check if the user has already liked the post
            if Likes.objects.filter(post=post, user=user).exists():
                return Response({'error': 'Liked!'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Increment the likes count and create a Like object
            post.likes_count = post.likes_count + 1
            post.save()
            Likes.objects.create(post=post, user=user)
            
            serializer = BlogPostSerializer(post)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BlogPost.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)


class CommentAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def get_object(self, slug):
        try:
            return BlogPost.objects.get(slug = slug)
        except BlogPost.DoesNotExist:
            return None
    
    def get(self, request, slug, *args, **kwargs):
        post = self.get_object(slug)
        if post is None:
            return Response({'error': 'Post not found'}, status = status.HTTP_404_NOT_FOUND)
        comments = Comment.objects.filter(post = post)
        serializer = CommentSerializer(comments, many = True)
        return Response(serializer.data, status = status.HTTP_200_OK)

    def post(self, request, slug, *args, **kwargs):
        post = self.get_object(slug)
        if post is None:
            return Response({'error': 'Post not found'}, status = status.HTTP_404_NOT_FOUND)
        data = request.data
        data['post'] = post.id
        data['user'] = request.user.id

        serializer = CommentSerializer(data = data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    

class ContactAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        data = request.data
        data["user"] = request.user.username
        serializer = ContactSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)