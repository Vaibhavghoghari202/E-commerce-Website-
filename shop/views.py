from django.shortcuts import render,HttpResponse,redirect
from .models import Product,Registration,Contact,Orders,OrderUpdate
from math import ceil
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# from media.PayTm import Checksum
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password 
from paytmchecksum import PaytmChecksum
from django.http import HttpResponse
# MERCHANT_KEY = 'kbzk1DSbjiV_03p5'

#import some paypal stuff
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid # unique uesr id for duplictate orders

def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('Phone')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')

        if password == cpassword:
            hashed_password = make_password(password)
            registration = Registration(name=name, email=email, Phone=phone, address=address, gender=gender, password=hashed_password)
            registration.save()
            
            # Store user info in session
            request.session['user_email'] = registration.email

            return redirect('login')  # Redirect to the profile page
        else:
            return HttpResponse("Password and Confirm Password don't match.")

    return render(request, 'shop/Registration.html')

    
        
    


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            # Fetch the user by email
            user = Registration.objects.get(email=email)

            # Check if the password matches
            if check_password(password, user.password):
                request.session['user_email'] = user.email  # Store email in session
                # Redirect to home or success page if login is successful
                return redirect('index.html')  # Replace 'home' with your actual success URL
            else:
                return HttpResponse("Invalid password. Please try again.")
        
        except Registration.DoesNotExist:
            # Handle the case when the user is not found
            return HttpResponse("User does not exist. Please register.")

    # For GET requests, render the login form
    return render(request, 'shop/login.html')

def logout(request):
    request.session.flush()
    return redirect('login')

def index(request):
    allProds = []
    catprods=Product.objects.values('category','id')
    cats={item['category'] for item in catprods }
    for cat in cats:
        prod=Product.objects.filter(category=cat)
        n= len(prod)
        nsalides=n//4 + ceil((n/4)-(n//4))
        allProds.append([prod,range(1,nsalides),nsalides])
    params = {'allProds':allProds,
              'user': request.user,}
    return render(request, 'shop/index.html', params)

def searchMatch(query,item):
    '''return true only if query matches the item'''
    if query in item.Desc.lower() or query in item.Product_name  or query in item.category.lower():
        return True
    else:       
        return False 

def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods=Product.objects.values('category','id')
    cats={item['category'] for item in catprods }
    for cat in cats:
        prodtemp=Product.objects.filter(category=cat)
        prod= [item for item in prodtemp if searchMatch (query,item )]
        n= len(prod)
        nsalides=n//4 + ceil((n/4)-(n//4))
        if len(prod)!= 0:
           allProds.append([prod,range(1,nsalides),nsalides])
    params = {'allProds':allProds,"msg":""}
    if len(allProds) == 0 or len(query)<4:
        params = {'msg':"Please make sure to enter relevant search Query"}
    return render(request, 'shop/search.html', params)

def about(request):
    return render(request,'shop/about.html')
    # return render(request,'shop/about.html')

def contact(request):
    if request.method=="POST":
      
        name=request.POST.get('name','')
        email=request.POST.get('email','')
        Phone=request.POST.get('Phone','')
        message=request.POST.get('message','')
        print(name ,email,Phone,message)
        contact= Contact(name=name,email=email,Phone=Phone,message=message)
        contact.save()
        thank =True
        return render(request,'shop/contact.html',{'thank':thank})
    return render(request,'shop/contact.html')

@csrf_exempt
def tracker(request):
    if request.method == "POST":
        orderid = request.POST.get('orderid', '').strip()
        phone_number = request.POST.get('phone_Number', '').strip()

        try:
            print(f"Received order ID: {orderid} and phone: {phone_number}")
            order = Orders.objects.filter(order_id=orderid, phone_Number=phone_number)

            if order.exists():
                updates = OrderUpdate.objects.filter(order=order.first()).order_by('timestamp')
                update_list = [{'text': item.update_desc, 'time': item.timestamp.strftime("%d-%m-%Y %H:%M:%S")} for item in updates]

                response = {
                    "status": "success",
                    "updates": update_list,
                    "itemsJson": order.first().items_json
                }
                return HttpResponse(json.dumps(response), content_type="application/json")
            else:
                return HttpResponse(json.dumps({"status": "noitem"}), content_type="application/json")

        except Exception as e:
            print(f"Error: {e}")
            return HttpResponse(json.dumps({"status": "error", "message": str(e)}), content_type="application/json")

    return render(request, 'shop/tracker.html')
  



def productView(request ,myid):
    #Fetch the  product using the Id 
    product =Product.objects.filter(id=myid)
    return render(request,'shop/productview.html',{'product':product[0]})



# #razorpay_client = razorpay.Client(auth=("rzp_test_Jh0DY1bhNltLDf", "KODQrNB95v0aPhn3LIB6sy8C"))
def checkout(request):
    user_email = request.session.get('user_email')
    if not user_email:
        return redirect('login')

    user = Registration.objects.get(email=user_email)

    if request.method == "POST":
        amount = int(request.POST.get('amount', '0'))

        # Store the form data temporarily
        request.session['checkout_data'] = {
            'items_json': request.POST.get('itemsJson', ''),
            'fname': request.POST.get('fname', ''),
            'lname': request.POST.get('lname', ''),
            'amount': amount,
            'phone_Number': request.POST.get('phone_Number', ''),
            'gender': request.POST.get('gender', ''),
            'address': request.POST.get('address', ''),
            'city': request.POST.get('city', ''),
            'county': request.POST.get('county', ''),
            'zip_code': request.POST.get('zip_code', ''),
            
        }

        host = request.get_host()
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': str(amount),
            'item_name': 'Order from Awesome Cart',
            'invoice': str(uuid.uuid4()),  # optional
            'currency_code': 'USD',
            'notify_url': f'http://{host}{reverse("paypal-ipn")}',
            'return_url': f'http://{host}{reverse("payment_success")}',
            'cancel_return': f'http://{host}{reverse("payment_failed")}',
        }

        form = PayPalPaymentsForm(initial=paypal_dict)

        return render(request, 'shop/paytm.html', {'form': form})

    return render(request, 'shop/checkout.html')
def profile(request):
    user_email = request.session.get('user_email')

    if not user_email:
        return redirect('login')  # Redirect to login if user is not logged in

    try:
        user = Registration.objects.get(email=user_email)
    except Registration.DoesNotExist:
        return HttpResponse("User does not exist, please register again.")

    # FIX: Filter orders using phone number or another relevant field
    orders = Orders.objects.filter(phone_Number=user.Phone)  

    return render(request, 'shop/profile.html', {'user': user, 'orders': orders})

def payment_success(request):
    data = request.session.get('checkout_data')
    if data:
        order = Orders.objects.create(
            items_json=data['items_json'],
            fname=data['fname'],
            lname=data['lname'],
            amount=data['amount'],
            phone_Number=data['phone_Number'],
            gender=data['gender'],
            address=data['address'],
            city=data['city'],
            county=data['county'],
            zip_code=data['zip_code'],
            payment_status='Completed',
        )
        # ✅ Create an order update after order is saved
        OrderUpdate.objects.create(
            order=order,  # ✅ 'order' matches your model field name
            update_desc="Your order has been placed successfully!"
            )
        # Clear the session data after saving
        del request.session['checkout_data']

        return render(request, 'shop/payment_success.html', {'order_id': order.order_id})


    return HttpResponse("Something went wrong. Order not created.")

def payment_failed(request):
    return render(request, 'shop/payment_failed.html')