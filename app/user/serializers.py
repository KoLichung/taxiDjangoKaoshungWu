from django.contrib.auth import get_user_model, authenticate

from rest_framework import serializers
from modelCore.models import User

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object"""

    class Meta:
        model = get_user_model()
        fields = ('phone', 'password', 'line_id', 'name', 'vehicalLicence', 'userId', 'idNumber', 'gender', 'type', 'category', 'car_model', 'car_color', 'number_sites', 'is_online', 'left_money', 'is_passed')
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 5},
            'line_id': {'write_only': True},
            }
        read_only_fields = ('is_passed',)

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

class UpdateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('phone','name', 'vehicalLicence', 'userId', 'idNumber', 'gender', 'type', 'category', 'car_model', 'car_color', 'number_sites', 'is_online', 'left_money', 'is_passed')
        read_only_fields = ('left_money', 'is_passed',)

class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""
    phone = serializers.CharField(allow_null=True)

    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        allow_null=True,
    )

    line_id = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        allow_null=True,
        required=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        phone = attrs.get('phone')
        password = attrs.get('password')
        line_id = attrs.get('line_id')
        
        user = None

        if password and password != '00000':
            user = authenticate(
                request=self.context.get('request'),
                username=phone,
                password=password
            )
        
        if (line_id and line_id != ''):
            try:
                print('here')
                user = User.objects.get(line_id=line_id)
            except Exception as e:
                print('')
            
        # if not user:
        #     msg = _('Unable to authenticate with provided credentials')
        #     raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs
