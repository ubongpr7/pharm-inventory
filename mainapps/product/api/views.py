from mainapps.permit.permit import HasModelRequestPermission
from ..models import Product, ProductCategory, ProductVariant
from .serializers import ProductCategorySerializer, ProductSerializer, ProductVariantSerializer
from rest_framework import viewsets,permissions,status
from mainapps.management.models_activity.activity_logger import log_user_activity
from rest_framework.decorators import action
from rest_framework.response import Response


class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class=ProductCategorySerializer
    permission_classes = [permissions.IsAuthenticated,HasModelRequestPermission]
    

    def perform_create(self, serializer):
        user = self.request.user
        company=user.profile
        serializer.save(
            profile=company

        )
        
    def get_queryset(self):
        return super().get_queryset().filter(profile=self.request.user.profile)
            
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        instance = serializer.instance
        log_user_activity(
            user=request.user,
            action='CREATE',
            instance=instance,
            details={
                'initial_data': request.data,
                'created_data': serializer.data,
                'ip_address': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT')
            },
            async_log=True
        )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated,HasModelRequestPermission]  

    def perform_create(self, serializer):
        user = self.request.user
        company=user.profile
        serializer.save(
            created_by=user, 
            profile=company

        )
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        instance = serializer.instance
        log_user_activity(
            user=request.user,
            action='CREATE',
            instance=instance,
            details={
                'initial_data': request.data,
                'created_data': serializer.data,
                'ip_address': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT')
            },
            async_log=True
        )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    
    
    def get_queryset(self):
        return super().get_queryset().filter(profile=self.request.user.profile)
    
class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer

    @action(detail=True, methods=['post'])
    def upload_attachment(self, request, pk=None):
        variant = self.get_object()
        serializer = VariantAttachmentSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        attachment = serializer.save(
            content_object=variant,
            uploaded_by=request.user,
            file_type='IMAGE' if 'image' in request.data['file'].content_type else 'DOC'
        )
        
        return Response(VariantAttachmentSerializer(attachment).data, status=201)

    @action(detail=True, methods=['patch'])
    def set_primary_image(self, request, pk=None):
        variant = self.get_object()
        attachment = variant.attachments.get(id=request.data['attachment_id'])
        
        # Clear existing primary
        variant.attachments.filter(purpose='MAIN_IMAGE').update(is_primary=False)
        attachment.is_primary = True
        attachment.save()
        
        return Response({'status': 'primary image updated'})