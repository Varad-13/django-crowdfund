from django.shortcuts import get_object_or_404, render, redirect
from django.http import Http404
import razorpay
from .models import Post, Transaction
from .forms import PostForm
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from django.core.mail import send_mail
from django.contrib import messages
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator
from django.views.generic import View
from django.db.models import Sum, Count

razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

def detail(request, author, url):
    post = get_object_or_404(Post, author=author, url=url)
    number_of_donations = Transaction.objects.filter(post_id = post.url).count()
    post.total_amount = number_of_donations*post.contribution_amount/100
    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(dict(amount=post.contribution_amount,
                                                       currency= 'INR',
                                                       payment_capture='0'))
    
    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    callback_url = 'paymenthandler/' + url

    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = post.contribution_amount
    context['amount'] = int(post.contribution_amount)//100
    context['currency'] = 'INR'
    context['callback_url'] = callback_url
    context['title'] = post.title
    context['intro'] = post.intro
    context['body'] = post.body
    context['created_at'] = post.created_at
    context['post'] = post

    return render(request, 'crowdfunding/detail.html', context=context)

def post_detail(request, url):
    post = get_object_or_404(Post, url=url)
    number_of_donations = Transaction.objects.filter(post_id = post.url).count()
    post.total_amount = number_of_donations*post.contribution_amount/100
    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(dict(amount=post.contribution_amount,
                                                       currency= 'INR',
                                                       payment_capture='0'))
    
    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    callback_url = 'paymenthandler/' + url

    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = post.contribution_amount
    context['amount'] = int(post.contribution_amount)//100
    context['currency'] = 'INR'
    context['callback_url'] = callback_url
    context['title'] = post.title
    context['intro'] = post.intro
    context['body'] = post.body
    context['created_at'] = post.created_at
    context['post'] = post

    return render(request, 'crowdfunding/detail.html', context=context)

def create_post(request):
    error = None
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if not request.FILES.get('thumbnail'):
            error = "Thumbnail is a required field!"
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user.username # Assuming user is logged in
            post.url = slugify(post.title.replace(" ", "-")) # Generate URL from title
            post.contribution_amount *= 100 #Multiply by 100 to convert to paise from rupees            
            post.save()
            subject = 'Your post '+ post.title + " has been added on Django-Crowdfunding"
            message = 'Hello '+request.user.username+". Thank you for using django-crowdfunding. Make sure to share your post."
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [request.user.email]  # List of recipient email addresses

            send_mail(subject, message, from_email, recipient_list)
            return redirect('post_detail', author=post.author, url=post.url) # Redirect to post detail page
    else:
        form = PostForm()
    return render(request, 'crowdfunding/create_post.html', {'form': form, 'error':error})

def edit_post(request, author, url):
    post = get_object_or_404(Post, author=author, url=url)
    if request.user.username != author:
        raise Http404
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        post.contribution_amount /= 100
        if form.is_valid():
            post = form.save(commit=False)
            post.contribution_amount *= 100 # Multiply by 100 to convert to paise from rupees
            post.save()
            return redirect('post_detail', author=post.author, url=post.url)
    else:
        form = PostForm(instance=post)
        post.contribution_amount /= 100
    return render(request, 'crowdfunding/edit_post.html', {'form': form, 'post': post})

def delete_post(request, url):
    post = get_object_or_404(Post, url=url)
    # Check if the logged-in user is the author of the post
    if post.author == request.user.username:
        post.delete()
        subject = 'Your post '+ post.title + " has been deleted from Django-Crowdfunding"
        message = 'Hello '+request.user.username+". Thank you for using django-crowdfunding. This email is to inform you that your post has been recently deleted from Django-Crowdfunding. If this was not done by you, please reply to this email and we will try to help you as best as we can"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [request.user.email]  # List of recipient email addresses
        send_mail(subject, message, from_email, recipient_list)
        return redirect('index')
    else:
        messages.error(request, 'You are not authorized to delete this post.')
        return redirect('index')

def user_dashboard(request):
    # Posts User donated to
    donations = Transaction.objects.filter(donor=request.user.username)
    post_ids = donations.values_list('post_id')
    posts_donated = Post.objects.filter(url__in=post_ids)
    for i in posts_donated:
        x = Transaction.objects.filter(post_id=i.url).count()
        i.total_amount = x*i.contribution_amount/100

    # Amount donated by User
    for j in posts_donated:
        x = Transaction.objects.filter(donor=request.user.username).count()
        j.user_donated = x*j.contribution_amount/100

    # Posts made by User
    user_posts = Post.objects.filter(author=request.user.username)
    post_ids = user_posts.values_list('url')
    for y in user_posts:
        x = Transaction.objects.filter(post_id=y.url).count()
        y.total_amount = x*y.contribution_amount/100
    return render(request, 'core/user_dashboard.html', {'posts_donated':posts_donated, 'user_posts':user_posts})

@csrf_exempt
def paymenthandler(request, author, url):
    post = get_object_or_404(Post, author=author, url=url)
    referer = request.META.get('HTTP_REFERER')
    # only accept POST request.
    if request.method == "POST":
        try:
           
            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
 
            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(
                params_dict)
            if result is not None:
                amount = post.contribution_amount 
                try:
                    # capture the payment
                    razorpay_client.payment.capture(payment_id, amount)

                    # create a Transaction instance and save it to the database
                    transaction = Transaction(
                        payment_id=payment_id,
                        razorpay_order_id=razorpay_order_id,
                        razorpay_signature=signature,
                        amount=amount,
                        post_id=post.url,
                        donor=request.user.username,
                    )
                    transaction.save()
                    donated_amount = int(post.contribution_amount)//100
                    subject = 'Successful donation to '+ post.title
                    message = 'Hello '+request.user.username+". Thank you for making a contribution of Rs." + str(donated_amount) + " for " + post.title + "." + "Your payment id is: " + payment_id
                    from_email = settings.DEFAULT_FROM_EMAIL
                    recipient_list = [request.user.email]  # List of recipient email addresses

                    send_mail(subject, message, from_email, recipient_list)
 
                    # render success page on successful caputre of payment
                    return redirect(referer)
                except:
                    # if there is an error while capturing payment.
                    return redirect(referer)
            else:
                # if signature verification fails.
                return redirect(referer)
        except:
 
            # if we don't find the required parameters in POST data
            return HttpResponseBadRequest()
    else:
       # if other than POST request is made.
        return HttpResponseBadRequest()
