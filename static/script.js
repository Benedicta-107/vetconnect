 // Set minimum date for booking to today
 document.addEventListener('DOMContentLoaded', function() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('bookingDate').setAttribute('min', today);
});

// Smooth scrolling
function scrollToServices() {
    document.getElementById('services').scrollIntoView({ behavior: 'smooth' });
}

// Booking Modal Functions
function openBookingModal(service = '') {
    document.getElementById('bookingModal').classList.remove('hidden');
    document.getElementById('bookingModal').classList.add('flex');
    if (service) {
        document.getElementById('bookingService').value = service;
    }
}

function closeBookingModal() {
    document.getElementById('bookingModal').classList.add('hidden');
    document.getElementById('bookingModal').classList.remove('flex');
}

function submitBooking(event) {
    event.preventDefault();

    const name = document.getElementById('bookingName').value;
    const phone = document.getElementById('bookingPhone').value;
    const service = document.getElementById('bookingService').value;
    const date = document.getElementById('bookingDate').value;

    // Simulate booking submission
    alert(`Thank you ${name}! Your appointment for ${service} on ${date} has been requested. We'll call you at ${phone} to confirm.`);

    closeBookingModal();
    event.target.reset();
}

// Contact Form Function
function submitContactForm(event) {
    event.preventDefault();

    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;

    alert(`Thank you ${name}! We've received your message and will respond to ${email} within 24 hours.`);
    event.target.reset();
}

// Chatbot Functions
function toggleChat() {
    const chatWindow = document.getElementById('chatWindow');
    const chatToggle = document.getElementById('chatToggle');

    if (chatWindow.classList.contains('hidden')) {
        chatWindow.classList.remove('hidden');
        chatToggle.innerHTML = '<span class="text-2xl">✕</span>';
    } else {
        chatWindow.classList.add('hidden');
        chatToggle.innerHTML = '<span class="text-2xl">💬</span>';
    }
}

function sendMessage(event) {
    event.preventDefault();

    const input = document.getElementById('chatInput');
    const message = input.value.trim();

    if (!message) return;

    // Add user message
    addMessage(message, 'user');
    input.value = '';

    // Show typing indicator
    showTypingIndicator();

    // Simulate AI response
    setTimeout(() => {
        hideTypingIndicator();
        const response = generateAIResponse(message);
        addMessage(response, 'bot');
    }, 1500);
}

function addMessage(message, sender) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');

    if (sender === 'user') {
        messageDiv.className = 'bg-green-600 text-white rounded-lg p-3 max-w-xs ml-auto';
    } else {
        messageDiv.className = 'bg-gray-100 rounded-lg p-3 max-w-xs';
    }

    messageDiv.innerHTML = `<p class="text-sm">${message}</p>`;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showTypingIndicator() {
    document.getElementById('typingIndicator').classList.add('show');
    const messagesContainer = document.getElementById('chatMessages');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function hideTypingIndicator() {
    document.getElementById('typingIndicator').classList.remove('show');
}

function generateAIResponse(message) {
    const lowerMessage = message.toLowerCase();

    // Booking related
    if (lowerMessage.includes('book') || lowerMessage.includes('appointment')) {
        return "I'd be happy to help you book an appointment! You can click the 'Book Appointment' button on our website, or call us at +234 XXX XXX XXXX. What service do you need?";
    }

    // Services
    if (lowerMessage.includes('service') || lowerMessage.includes('what do you')) {
        return "We offer: Veterinary Clinic, Pet Shop, Farm Consultation, Pure-bred Dog Sales & Training, Veterinary Pharmacy, and Emergency Care. Which service interests you?";
    }

    // Emergency
    if (lowerMessage.includes('emergency') || lowerMessage.includes('urgent')) {
        return "For emergencies, please call us immediately at +234 XXX XXX XXXX. We provide 24/7 emergency care. If it's life-threatening, bring your pet in right away!";
    }

    // Hours
    if (lowerMessage.includes('hour') || lowerMessage.includes('open') || lowerMessage.includes('time')) {
        return "We're open Monday-Friday 8AM-6PM, Saturday 9AM-4PM. Sunday is emergency only. Our address is St Finbars Road, Opp Abia Hotel, Umuahia.";
    }

    // Location
    if (lowerMessage.includes('where') || lowerMessage.includes('location') || lowerMessage.includes('address')) {
        return "We're located at St Finbars Road, opposite Abia Hotel in Umuahia, Abia State. Easy to find and plenty of parking available!";
    }

    // Pricing
    if (lowerMessage.includes('price') || lowerMessage.includes('cost') || lowerMessage.includes('fee')) {
        return "Our prices vary by service. Please call +234 XXX XXX XXXX for specific pricing, or visit us for a consultation. We offer competitive rates for all services.";
    }

    // Dogs
    if (lowerMessage.includes('dog') || lowerMessage.includes('puppy') || lowerMessage.includes('breed')) {
        return "We have pure-bred dogs available and offer professional training services. Each dog comes with health certificates and pedigree documentation. Would you like to schedule a visit?";
    }

    // Default response
    return "Thank you for your question! For detailed information, please call us at +234 XXX XXX XXXX or visit our clinic. Our team will be happy to help you with any concerns about your pet's health.";
}

// Close modal when clicking outside
document.getElementById('bookingModal').addEventListener('click', function(event) {
    if (event.target === this) {
        closeBookingModal();
    }
});

(function(){function c(){var b=a.contentDocument||a.contentWindow.document;if(b){var d=b.createElement('script');d.innerHTML="window.__CF$cv$params={r:'98adca23e39da2cb',t:'MTc1OTg0NDIwOS4wMDAwMDA='};var a=document.createElement('script');a.nonce='';a.src='/cdn-cgi/challenge-platform/scripts/jsd/main.js';document.getElementsByTagName('head')[0].appendChild(a);";b.getElementsByTagName('head')[0].appendChild(d)}}if(document.body){var a=document.createElement('iframe');a.height=1;a.width=1;a.style.position='absolute';a.style.top=0;a.style.left=0;a.style.border='none';a.style.visibility='hidden';document.body.appendChild(a);if('loading'!==document.readyState)c();else if(window.addEventListener)document.addEventListener('DOMContentLoaded',c);else{var e=document.onreadystatechange||function(){};document.onreadystatechange=function(b){e(b);'loading'!==document.readyState&&(document.onreadystatechange=e,c())}}}})();
