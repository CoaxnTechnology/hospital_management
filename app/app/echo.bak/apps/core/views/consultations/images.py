import base64, secrets, io
import json
from datetime import datetime

from PIL import Image
from django.contrib.auth.decorators import login_required, permission_required
from django.core.files.base import ContentFile
from django.db.models import ImageField
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from apps.core.models import Consultation, ImageConsultation
from apps.core.serializers import ImageConsultationSerializer, ImageConsultationSerializerLight


def repertoire_images_utilisateur(consultation):
    path = f'comptes/compte_{consultation.patient.compte.pk}/patients/{consultation.patient.pk}/images/'
    print(f'Enregistrement de image dans {path}')
    return path


# https://dev.to/ageumatheus/creating-image-from-dataurl-base64-with-pyhton-django-454g
def get_image_from_data_url(root_folder, data_url, resize=True, base_width=600):
    # getting the file format and the necessary dataURl for the file
    _format, _dataurl = data_url.split(';base64,')
    # file name and extension
    _filename, _extension = secrets.token_hex(20), _format.split('/')[-1]

    # generating the contents of the file
    file = ContentFile(base64.b64decode(_dataurl), name=f"{root_folder}{_filename}.{_extension}")

    # resizing the image, reducing quality and size
    if resize:
        # opening the file with the pillow
        image = Image.open(file)
        # using BytesIO to rewrite the new content without using the filesystem
        image_io = io.BytesIO()

        # resize
        w_percent = (base_width / float(image.size[0]))
        h_size = int((float(image.size[1]) * float(w_percent)))
        image = image.resize((base_width, h_size), Image.ANTIALIAS)

        # save resized image
        image.save(image_io, format=_extension)

        # generating the content of the new image
        file = ContentFile(image_io.getvalue(), name=f"{_filename}.{_extension}")

    # file and filename
    return file, (_filename, _extension)


@login_required
@permission_required('core.change_patient', raise_exception=True)
def ajouter_image(request, pk):
    consult = get_object_or_404(Consultation, pk=pk)
    root_folder = repertoire_images_utilisateur(consult)
    image = ImageConsultation(image=get_image_from_data_url(root_folder, request.POST.get('file'))[0],
                              type=request.POST.get('type'),
                              date=datetime.now(),
                              consultation=consult)
    image.save()
    consult.imageconsultation_set.add(image)
    consult.save()
    data = {
        'image': json.dumps(ImageConsultationSerializer(image).data),
        'message': "Image ajoutée"
    }
    return JsonResponse(data)


@login_required
@permission_required('core.change_patient', raise_exception=True)
def supprimer_image(request, pk):
    image = get_object_or_404(ImageConsultation, pk=pk)
    image.delete()
    data = {
        'pk': pk,
        'message': "Image supprimée"
    }
    return JsonResponse(data)


@login_required
@permission_required('core.change_patient', raise_exception=True)
def modifier_image(request, pk):
    image = get_object_or_404(ImageConsultation, pk=pk)
    impression = request.POST.get('impression', None)
    if impression:
        if impression == 'true':
            image.impression = True
        else:
            image.impression = False
    image.save()
    data = {
        'pk': pk,
        'message': "Image modifiée"
    }
    return JsonResponse(data)


@login_required
@permission_required('core.change_patient', raise_exception=True)
def consultation_images(request, pk):
    consult = get_object_or_404(Consultation, pk=pk)
    data = {'images': json.dumps(ImageConsultationSerializerLight(consult.imageconsultation_set.all(), many=True).data)}
    return JsonResponse(data)
