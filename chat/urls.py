from django.urls import path
from .views import MessageListAPIView, UploadMessageView

urlpatterns = [
    path('messages/<int:match_id>/', MessageListAPIView.as_view(), name='message-list'),
    path('messages/upload/', UploadMessageView.as_view(), name='file-upload'),
]

# const fileInput = document.querySelector('input[type=file]');
# const file = fileInput.files[0];

# const formData = new FormData();
# formData.append("file", file);
# formData.append("text", "Here’s an image!");
# formData.append("match_id", matchId);

# fetch("/api/messages/upload/", {
#     method: "POST",
#     body: formData,
#     headers: {
#         "Authorization": "Bearer " + token
#     }
# })
# .then(res => res.json())
# .then(data => console.log("Uploaded:", data.media_url));
