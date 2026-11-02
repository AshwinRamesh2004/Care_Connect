from rest_framework import serializers
from Clinic.models import DoctorDb, AppointmentDb


class Doctor_Serializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorDb
        fields = "__all__"
        read_only_fields = ["id"]


class Appoinment_Serializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentDb
        fields = "__all__"
        read_only_fields = ["id"]

    def validate(self,validated_data):
        phone=validated_data.get("phone")
        appointment_date=validated_data.get("appointment_date")
        if AppointmentDb.objects.filter(
            phone=phone,
            appointment_date=appointment_date).exists():
            raise serializers.ValidationError("already booked")
        else:
            return validated_data
