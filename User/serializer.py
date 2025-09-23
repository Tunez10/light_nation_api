# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password', 'first_name', 'last_name', 'phone_number', 'title', 'datejoined', 'social_links',)
    
    def create(self, validated_data):
        email = validated_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'A user with this email already exists.'})

        # Create the user and hash the password
        user = User.objects.create(
            email=email,
            username=validated_data['username'].lower(),
            first_name=validated_data.get('first_name', ''),  # Ensure it doesn't break if missing
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', None),
            title=validated_data.get('title', ''),
            social_links=validated_data.get('social_links', ''),
        )
        user.set_password(validated_data['password'])  # Ensure the password is hashed
        user.save()

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email').lower()
        password = data.get('password')

        if not email:
            raise serializers.ValidationError('email is required')

        if not password:
            raise serializers.ValidationError('Password is required')

        try:
            # Fetch the user based on the email
            user = User.objects.get(email=email)

            # Check the password using the built-in method
            if not user.check_password(password):
                raise serializers.ValidationError('Incorrect credentials')

        except User.DoesNotExist:
            raise serializers.ValidationError('Incorrect credentials')

        if user and user.is_active:
            return {'user': user}
        
        raise serializers.ValidationError('Account is not active or does not exist')   




class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
