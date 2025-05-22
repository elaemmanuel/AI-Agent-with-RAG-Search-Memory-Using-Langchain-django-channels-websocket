from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
import asyncio
from asgiref.sync import sync_to_async
from chat_app.consumers import ChatConsumer 
 


def chat_view(request, room_name='general'):
    return render(request, 'chat_app/chat.html', {'room_name': room_name})



@csrf_exempt
def upload_document(request):
    if request.method == 'POST' and request.FILES.get('document'):
        uploaded_file = request.FILES['document']
        file_name = uploaded_file.name

        # Ensure the media directory exists
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

        # Save the file
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        try:
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            # Trigger RAG update (async task using sync_to_async to call class method)
            # This calls the class method directly, which updates the global vector store
            asyncio.run(ChatConsumer.trigger_rag_update_with_new_file(file_path))


            return JsonResponse({'message': 'File uploaded successfully!', 'file_path': file_path}, status=200)
        except Exception as e:
            return JsonResponse({'error': f'Failed to save file: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Invalid request or no document provided.'}, status=400)
