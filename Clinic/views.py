from datetime import time, timedelta, datetime

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from Clinic.models import DoctorDb, AppointmentDb
from Clinic.serializer import Doctor_Serializer, Appoinment_Serializer


class DoctorListCreateView(APIView):
    def get(self, request):
        qs = DoctorDb.objects.all()
        serialiser_instance = Doctor_Serializer(qs, many=True)
        return Response(data=serialiser_instance.data)

    def post(self, request):
        serialiser_instance = Doctor_Serializer(data=request.data)
        if serialiser_instance.is_valid():
            serialiser_instance.save()
            return Response(data=serialiser_instance.data,
                            status=status.HTTP_201_CREATED)
        return Response(data=serialiser_instance.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class DoctorRetrieveUpdateDeleteView(APIView):
    def get(self, request, pk):
        doctor_object = get_object_or_404(DoctorDb, id=pk)
        serialiser_instance = Doctor_Serializer(doctor_object)
        return Response(data=serialiser_instance.data)

    def put(self, request, pk):
        doctor_object = get_object_or_404(DoctorDb, id=pk)
        serialiser_instance = Doctor_Serializer(data=request.data, instance=doctor_object)
        if serialiser_instance.is_valid():
            serialiser_instance.save()
            return Response(data=serialiser_instance.data)
        return Response(data=serialiser_instance.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        doctor_object = get_object_or_404(DoctorDb, id=pk)
        serialiser_instance = Doctor_Serializer(data=request.data, instance=doctor_object,
                                                partial=True)
        if serialiser_instance.is_valid():
            serialiser_instance.save()
            return Response(data=serialiser_instance.data)
        return Response(data=serialiser_instance.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        doctor_object = get_object_or_404(DoctorDb, id=pk)
        doctor_object.delete()
        return Response(data={"Message": "deleted"})


class AppointmentListCreateView(APIView):
    def get(self, request):
        qs = AppointmentDb.objects.all()
        serialiser_instance = Appoinment_Serializer(qs, many=True)
        return Response(data=serialiser_instance.data)

    def post(self, request):
        serialiser_instance = Appoinment_Serializer(data=request.data)
        if serialiser_instance.is_valid():
            data = dict(serialiser_instance.validated_data)
            appointment_date = data["appointment_date"]
            doctor_id = data["doctor_id"]

            # The doctor must exist
            if not DoctorDb.objects.filter(id=doctor_id).exists():
                return Response(data={"error": "Doctor not found"},
                                status=status.HTTP_404_NOT_FOUND)

            # Latest booking for this doctor on this date
            last_appointment = AppointmentDb.objects.filter(
                appointment_date=appointment_date,
                doctor_id=doctor_id
            ).order_by("-token_number").first()

            if last_appointment is None:
                data["token_number"] = 1
                data["appointment_time"] = time(10, 0)
            else:
                next_token = last_appointment.token_number + 1
                current_time = datetime.combine(appointment_date,
                                                last_appointment.appointment_time)
                next_time = current_time + timedelta(minutes=15)
                data["token_number"] = next_token
                data["appointment_time"] = next_time.time()
                
            AppointmentDb.objects.create(**data)
            return Response(data={
                "status": "booked successfully",
                "token_number": data["token_number"],
                "appointment_time": data["appointment_time"].strftime("%H:%M")
            }, status=status.HTTP_201_CREATED)

        return Response(data=serialiser_instance.errors,
                        status=status.HTTP_400_BAD_REQUEST)