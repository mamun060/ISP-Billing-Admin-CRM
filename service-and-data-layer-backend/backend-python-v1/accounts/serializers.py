from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        phone = attrs.get("phone")
        email = attrs.get("email")
        password = attrs.get("password")

        if not password:
            raise serializers.ValidationError({"password": "This field is required."})

        if username:
            user = authenticate(request=self.context.get("request"), username=username, password=password)
        elif phone:
            user = authenticate(request=self.context.get("request"), phone=phone, password=password)
        elif email:
            user = authenticate(request=self.context.get("request"), email=email, password=password)
        else:
            raise serializers.ValidationError({"detail": "Provide username, phone, or email."})

        if user is None or not user.is_active:
            raise serializers.ValidationError({"detail": "Invalid credentials."})

        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "phone",
            "email",
            "first_name",
            "last_name",
            "partner",
        ]
        read_only_fields = ["id", "partner"]
