from django.shortcuts import render, redirect
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from crowdfunding.models import Post, Transaction

razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

razorpay_order = razorpay_client.order.create(dict(amount=50000,
                                                       currency='INR',
                                                       payment_capture='0'))

def index(request):
    posts_all = Post.objects.all()
    for i in posts_all:
        x = Transaction.objects.filter(post_id=i.url).count()
        i.total_amount = x*i.contribution_amount/100
    return render(request, 'core/index.html', {'posts':posts_all})

def about(request):
    # Get the Razorpay Order ID
    razorpay_order_id = razorpay_order['id']

    # Define the callback URL for handling the payment response
    callback_url = 'payment/'

    # Render the about.html template with the necessary context variables
    context = {
        'razorpay_merchant_key': settings.RAZOR_KEY_ID,  # Replace with your Razorpay merchant key
        'razorpay_amount': razorpay_order['amount'],
        'currency': razorpay_order['currency'],
        'razorpay_order_id': razorpay_order_id,
        'callback_url': callback_url
    }
    return render(request, 'core/about.html', context)

@csrf_exempt
def payment(request):
    # Retrieve the Razorpay Payment ID from the callback response
    razorpay_payment_id = request.POST.get('razorpay_payment_id')

    # Get the amount from the Razorpay order object
    amount = int(razorpay_order['amount'])

    # Verify the payment using Razorpay API
    razorpay_client.payment.capture(razorpay_payment_id, amount)

    subject = "Django-Crowdfunding donation recieved!"
    message = 'Hello '+request.user.username+". Thank you for donating to django-crowdfunding."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [request.user.email]  # List of recipient email addresses

    send_mail(subject, message, from_email, recipient_list)

    # Return a success response
    return redirect('about')

def user(request, author):
    posts_all = Post.objects.filter(author=author)
    post_ids = posts_all.values_list('url')
    posts = Post.objects.filter(url__in=post_ids)
    for j in posts:
        x = Transaction.objects.filter(donor=request.user.username).count()
        j.user_donated = x*j.contribution_amount/100
    return render(request, 'core/index.html', {'posts':posts, 'author':author})

def transactions(request):
    transactions = Transaction.objects.filter(donor=request.user.username)
    return render(request, 'core/transactions.html', {'transactions':transactions})

def login(request):
    posts_all = Post.objects.filter(author=request.user.username)
    post_ids = posts_all.values_list('url')
    posts = Post.objects.filter(url__in=post_ids)
    for i in posts:
        x = Transaction.objects.filter(post_id=i.url).count()
        i.total_amount = x*i.contribution_amount/100
    return render(request, 'core/index.html', {'posts':posts, 'author':request.user.username})
