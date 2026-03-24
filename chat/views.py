from google import genai
from google.genai import types
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Chat, Message

# Initialize the client
client = genai.Client(api_key=settings.GEMINI_API_KEY)

@login_required
def chat_view(request, chat_id=None):
    # Fetch previous chats for the sidebar
    chat_history_list = Chat.objects.filter(user=request.user).order_by('-created_at')

    current_chat = None
    if chat_id:
        current_chat = get_object_or_404(Chat, id=chat_id, user=request.user)

    if request.method == "POST":
        prompt_text = request.POST.get("prompt")

        # If no chat_id, create a new Chat thread
        if not current_chat:
            # Create a title from the first 30 chars of the prompt
            title = prompt_text[:30] + '...' if len(prompt_text) > 30 else prompt_text
            current_chat = Chat.objects.create(title=title, user=request.user)
        
        system_instruction = (
            "You are a Mental Health Support assistant. "
            "STRICT FORMATTING RULE: NEVER output long blocks of text or single long paragraphs. "
            "Instead, CHOP your response into clear, distinct sections. "
            "1. Use bold headings (e.g., **Heading**) for each section. "
            "2. Use bullet points for advice or steps. "
            "3. Use bold text for key terms. "
            "4. If a paragraph is longer than 2 sentences, break it into a list or multiple small sections. "
            "STRICT TOPIC RULE: If the user prompt is NOT about mental health, emotions, or psychology, "
            "you MUST ONLY output the exact phrase: 'Do you have any questions about mental health?'"
        )

        try:
            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt_text,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.1,
                )
            )
            response_text = response.text

            # Save the message to the database
            Message.objects.create(chat=current_chat, prompt=prompt_text, response=response_text)

        except Exception as e:
            response_text = f"API Error: {str(e)}"

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                "prompt": prompt_text,
                "response": response_text,
                "chat_id": current_chat.id
            })

    # For GET requests
    messages = []
    if current_chat:
        messages = current_chat.messages.all().order_by('created_at')

    return render(request, "chat/chat.html", {
        "chat_history_list": chat_history_list,
        "current_chat": current_chat,
        "messages": messages
    })

@login_required
def new_chat(request):
    """Start a fresh chat."""
    return redirect('chat')

@login_required
def delete_chat(request, chat_id):
    """Delete a chat and its messages."""
    chat = get_object_or_404(Chat, id=chat_id, user=request.user)
    chat.delete()
    return redirect('chat')
