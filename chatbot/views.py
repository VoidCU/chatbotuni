# views.py

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import spacy
from .models import Intent, Example,Conversation
from django.contrib.auth.decorators import login_required
import datetime

# nlp = spacy.load("en_core_web_sm")
nlp = spacy.load('en_core_web_lg')
# Temporary in-memory store for user states
user_states = {}

@csrf_exempt
def chat(request):
    if request.method == "POST":
        user_id = request.session.session_key or request.session.create()
        message = request.POST.get("message")
        response, user_states[user_id] = handle_message(message, user_states.get(user_id, {}))
        
        session_id = request.session.session_key
        
        conversation, created = Conversation.objects.get_or_create(session_id=session_id)
        conversation.user_id = user_id
        conversation.messages += f"{message}<sep>{response}<sep>"
        conversation.save()

        return JsonResponse({"response": response})


def handle_message(message, state):
    doc = nlp(message)
    intent = get_intent(doc)
    
    if state.get("intent") == "make_appointment":
        if "stop" in [token.lemma_ for token in doc] or "cancel" in [token.lemma_ for token in doc]:
            return "Appointment scheduling cancelled.", {}
        if "name" not in state:
            state["name"] = message
            return "Please provide your email address.", state
        elif "email" not in state:
            state["email"] = message
            return schedule_appointment(state["name"], state["email"]), {}
    elif intent == "make_appointment":
        state["intent"] = "make_appointment"
        return "Sure, I can help you with that. What's your name?", state
    else:
        response = get_simple_response(intent)
        if response:
            return response, state
        else:
            return "I'm sorry, I didn't understand that. Can you please rephrase?", state

def get_intent(doc):
    # Define specific keywords for the 'make_appointment' intent
    appointment_keywords = ["schedule", "book", "make", "appointment", "meeting"]

    # Check for specific keywords
    for token in doc:
        if token.lemma_ in appointment_keywords:
            return "make_appointment"

    # Check for similarity with examples in the Example model
    max_similarity = 0
    most_similar_intent = "unknown"
    
    for example in Example.objects.all():
        example_doc = nlp(example.text)
        similarity = doc.similarity(example_doc)
        
        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_intent = example.intent.name

    return most_similar_intent

def get_simple_response(intent):
    try:
        intent_obj = Intent.objects.get(name=intent)
        return intent_obj.response
    except Intent.DoesNotExist:
        return None

def schedule_appointment(name, email):
    # Simple scheduling logic (for demonstration purposes)
    import datetime
    today = datetime.date.today()
    appointment_date = today + datetime.timedelta(days=1)
    return f"Thank you, {name}. Your appointment is scheduled for {appointment_date} at 10:00 AM. A confirmation email will be sent to {email}."

def index(request):
    return render(request, "chat.html")

@login_required
def admin_dashboard(request):
    conversations = Conversation.objects.all().order_by('-date')
    intents = Intent.objects.all()
    return render(request, "admin_dashboard.html", {"conversations": conversations,'intents': intents})

@login_required
def get_conversation(request, conversation_id):
    try:
        conversation = Conversation.objects.get(id=conversation_id)
        return JsonResponse({
            'messages': conversation.messages
        })
    except Conversation.DoesNotExist:
        return JsonResponse({'messages': 'Conversation not found.'}, status=404)


@csrf_exempt
def add_example(request):
    if request.method == 'POST':
        intent_id = request.POST.get('intent')
        text = request.POST.get('text')

        try:
            intent = Intent.objects.get(id=intent_id)
            Example.objects.create(intent=intent, text=text)
            return JsonResponse({'success': True})
        except Intent.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Intent not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})