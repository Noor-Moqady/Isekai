from django.shortcuts import render,redirect,HttpResponse
from .models import *
from django.contrib import messages
import bcrypt
from django.utils import timezone
import random
import string
import paypalrestsdk
from django.conf import settings
import stripe
from .models import OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm




# Create your views here.
def index(request):
    specific_user = None
    if 'user_id' in request.session:
        specific_user = User.objects.get(id=request.session['user_id'])

    context = {
        'allitems': Item.objects.all(),
        'allorderitem': OrderItem.objects.all(),#why we add this here, we don't use it//Motaz
        'specific_user': specific_user,
    }
    return render(request, 'home.html', context)
def product(request,id):
    this_item=Item.objects.get(id=int(id))
    saving=this_item.price-this_item.discount_price
    context={
        'this_item':this_item,
        'saving': saving,
        'specific_user': User.objects.get(id=request.session['user_id'])
    }
    return render(request,'product_main_page.html',context)

def register(request):
    if request.method == "POST":
        errors = User.objects.basic_validator1(request.POST)
        if len(errors) > 0 :
            # if 'username' in errors:
            #     request.session['username']=errors['username']
            # if 'email' in errors:
            #     request.session['email']=errors['email']
            # if 'password' in errors:
            #     request.session['password']=errors['password']
            # if 'confirm' in errors:
            #     request.session['confirm']=errors['confirm']
            return redirect('/register')
        else:
            hash1= bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
            registered_user = User.objects.create(
                username=request.POST['username'],
                email=request.POST['email'],
                password=hash1,
                )
            messages.success(request, "Registered successfully")
            request.session['user_id']=registered_user.id
            request.session['username']=registered_user.username

            return redirect('/')

    else:
        return render(request,'register.html')

def login(request):
    if request.method == "POST":
        user = User.objects.filter(email=request.POST['lemail'])
        if user:
            logged_user = user[0]
            if bcrypt.checkpw(request.POST['lpassword'].encode(), logged_user.password.encode()):
                    request.session['user_id']=logged_user.id
                    request.session['username']=logged_user.username

                    return redirect('/')
            else:
                err={}
                err['authentication']= 'Invalid authentication'
                request.session['authentication']=err['authentication']
                print(request.session['authentication'])
                return redirect ('/login')

        else:
            err={}
            err['authentication']= 'Invalid authentication'
            request.session['authentication']=err['authentication']
            print(request.session['authentication'])
            return redirect ('/login')
    else:
        return render(request,'login.html')
def add_to_cart(request,id):
    if 'user_id' in request.session:
        this_user=User.objects.get(id=request.session['user_id'])
        this_item=Item.objects.get(id=int(id))
        amount=request.POST['quantity']
        order_item=OrderItem.objects.create(
            # user=this_user,
            item=this_item,
            quantity=amount
        )
        order_item.user.add(this_user)#motaz
        return redirect('/cart')
    else:
        return redirect('/login')
def cart(request):
    if 'user_id' in request.session:
        this_user=User.objects.get(id=request.session['user_id'])
        total=0
        saving = 0
        for item in this_user.order_items_for_user.all():
            print(item.item.price)
            print(item.quantity)
            total+=(item.item.price*item.quantity)
            saving += (item.item.price - item.item.discount_price) * item.quantity
            request.session['saving'] = saving
            request.session['total'] = total
        context={
            'allitems_in_order':this_user.order_items_for_user.all(),
            'total':total,
            'specific_user': User.objects.get(id=request.session['user_id'])

        }
        return render(request, 'shopping_cart.html',context)

    else:
        return redirect('/login')

def delete_order_item(request,id):
    this_order_item=OrderItem.objects.get(id=int(id))
    this_order_item.delete()

    return redirect('/cart')
def logout(request):
    if 'user_id' in request.session:
        request.session.flush()
    return redirect('/')

# /////////////////////////////////////////////////////////////////////////////////////////////////////////////
# def process_payment(request):
#     if request.method == "POST":
#         order = Order.objects.get(user=request.user, ordered=False)
#         total_amount = calculate_total_order_amount(order)

#         # Create a Checkout Session
#         session = stripe.checkout.Session.create(
#             payment_method_types=['card'],
#             line_items=[{
#                 'price_data': {
#                     'currency': 'usd',
#                     'product_data': {
#                         'name': 'Your Product',
#                     },
#                     'unit_amount': int(total_amount * 100),  # Amount in currentsy
#                 },
#                 'quantity': 1,
#             }],
#             mode='payment',
#             success_url=request.build_absolute_uri(reverse('order_success')),
#             cancel_url=request.build_absolute_uri(reverse('cart')),
#         )

#         return render(request, 'mock_payment_form.html', {'session_id': session.id})

#     return redirect('/cart')


# def execute_payment(request):
#     payment_id = request.GET.get('paymentId')
#     payer_id = request.GET.get('PayerID')

#     payment = paypalrestsdk.Payment.find(payment_id)
#     if payment.execute({"payer_id": payer_id}):
#         order = Order.objects.get(user=request.user, ordered=False)
#         order.ordered = True
#         order.save()
#         return render(request, 'order_success.html')
#     else:
#         messages.error(request, "Failed to execute PayPal payment. Please try again.")
#         return redirect('/cart')


# def calculate_total_order_amount(order):
#     total_amount = 0
#     for item in order.items.all():
#         total_amount += item.item.price * item.quantity
#     return total_amount


# def enter_address(request):
#     if request.method == 'POST':
#         form = OrderForm(request.POST)
#         if form.is_valid():

#             return render(request, 'processing_payment.html')
#     else:
#         form = OrderForm()

#     return render(request, 'address_form.html', {'form': form})

# def process_address_selection(request):
#     if request.method == 'POST':
#         selected_address = request.POST.get('address')
#         if selected_address:
#             # Process the selected address as needed
#             this_user = User.objects.get(id=request.session['user_id'])
#             this_user.order_items_for_user.all().delete()

#             return redirect('credit_card_form')


#     return HttpResponse("Invalid request or address selection")
# def process_order(request):

#     if 'user_id' in request.session:
#         this_user = User.objects.get(id=request.session['user_id'])
#         this_user.order_items_for_user.all().delete()

#     return redirect('main_page')
# def main_page(request):

#     return render(request, 'home.html')

# def credit_card_form(request):
#     return render(request, 'credit_card_form.html')

# def process_credit_card(request):

#     if 'user_id' in request.session:
#         this_user = User.objects.get(id=request.session['user_id'])
#         this_user.order_items_for_user.all().delete()

#     return redirect('main_page')

# def main_page(request):
#     cart_item_count = 0

#     if 'user_id' in request.session:
#         this_user = User.objects.get(id=request.session['user_id'])
#         if Order.objects.filter(user=this_user, ordered=False):
#             cart_item_count = this_user.order_items_for_user.filter(ordered=False).count()

#     context = {
#         'cart_item_count': cart_item_count,
#     }

#     return render(request, 'home.html', context)


def search_results(request):

    # query = request.GET.get('query', '')
    # category = request.GET.get('category', 'all')


    # if category == 'all':
    #     results = Item.objects.filter(title__icontains=query)
    # else:
    #     results = Item.objects.filter(title__icontains=query, category=category)

    # context = {'query': query, 'category': category, 'results': results}
    print('Motaz')
    print(request.POST['search_ajax'])
    search = Item.objects.filter(title__startswith=request.POST['search_ajax'])
    if search:
        print(request.POST['search_ajax'])
        for items in  search.all():
            print(items.title)
        context={
            'search':search.all()
        }
            
    return render(request,'ajax_search.html',context)


# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def your_account(request):
    if not 'user_id' in request.session:
        return redirect('/login')
    else:    
        context = {
        'specific_user': User.objects.get(id=request.session['user_id'])
    }
        return render(request, 'your_account.html', context)

def your_addresses(request):
    if not 'user_id' in request.session:
        messages.error(request,"You have to login first")
        return redirect('/login')
    else:
        context={
            'alladdresses': Address.objects.all(),
            'specific_user': User.objects.get(id=request.session['user_id'])

        }
        return render (request, "your_addresses.html", context)


def add_new_address(request):
    if not 'user_id' in request.session:
        messages.error(request,"You have to login first")
        return redirect('/login')
    else:

        if request.method == 'GET':
            context = {
                'specific_user': User.objects.get(id=request.session['user_id'])
            }
            return render(request, 'add_new_address.html',context)
        if request.method == 'POST':
            errors = Address.objects.basic_validator(request.POST)
            if len(errors) > 0:
                for key, value in errors.items():
                    messages.error(request, value)
                return redirect('/your_addresses')
            else:
                address=Address.objects.create(uploaded_by=User.objects.get(id=request.session['user_id']), country=request.POST['country'],full_name=request.POST['full_name'], mobile_number=request.POST['mobile_number'],PIN_code=request.POST['PIN_code'], Apartment=request.POST['Apartment'],street=request.POST['street'],landmark=request.POST['landmark'], town=request.POST['town'])
            return redirect('/your_addresses')

def select_address(request):
    # //////////noor
    # if not 'user_id' in request.session:
    #     messages.error(request,"You have to login first")
    #     return redirect('/login')
    # else:
    #     if request.method == 'GET':
    #         context = {
    #         'alladdresses': Address.objects.all(),
    #         'specific_user': User.objects.get(id=request.session['user_id'])
    #         }
    #         return render(request, 'select_address.html' ,context)
    #     if request.method == 'POST':
    #             request.session['shipping_address_name'] = request.POST['shipping_address_name']
    #             request.session['shipping_address_country'] = request.POST['shipping_address_country']
    #             request.session['shipping_address_town'] = request.POST['shipping_address_town']
    #             request.session['shipping_address_apartment'] = request.POST['shipping_address_apartment']
    #             request.session['shipping_address_street'] = request.POST['shipping_address_street']
    #             request.session['shipping_address_landmark'] = request.POST['shipping_address_landmark']
    #             request.session['shipping_address_pincode'] = request.POST['shipping_address_pincode']
    #             request.session['shipping_address_mobile'] = request.POST['shipping_address_mobile']
    #             request.session['shipping_address_id'] = request.POST['shipping_address_id']

                # return redirect('/select_payment_method/' + request.POST['shipping_address'])
                # return redirect('/select_payment_method')
    # //////////motaz
        if not 'user_id' in request.session:
            messages.error(request,"You have to login first")
            return redirect('/login')
        else:
            if request.method == 'GET':
                context = {
                'alladdresses': Address.objects.all(),
                'specific_user': User.objects.get(id=request.session['user_id'])
                }
                return render(request, 'select_address_motaz.html' ,context)
        
    
        # return redirect('/select_payment_method')



def select_payment_method(request,id):
    if not 'user_id' in request.session:
        messages.error(request,"You have to login first")
        return redirect('/login')
    else:
        this_address=Address.objects.get(id=int(id))#motaz
        request.session['user_address_id']=this_address.id
        if request.method == 'GET':
            context={
            'specific_user': User.objects.get(id=request.session['user_id'])

        }
            return render (request, "select_payment_method.html", context)
        if request.method == 'POST':
            if 'paymentMethod' in request.POST:
                request.session['paymentMethod'] = request.POST['paymentMethod']
                return redirect('/review_order')


def review_order(request):
    if not 'user_id' in request.session:
        messages.error(request,"You have to login first")
        return redirect('/login')
    else:
        this_address=Address.objects.get(id=request.session['user_address_id'])
        context = {
            # 'alladdresses': Address.objects.all(),
            'specific_user': User.objects.get(id=request.session['user_id']),
            'this_address':this_address#motaz
        }
        return render(request, "review_order.html", context)

def create_order(request):
    if 'user_id' in request.session:
        specific_user=User.objects.get(id=request.session['user_id'])
        def create_ref_code():
            return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))
        ref=create_ref_code()
        this_address=Address.objects.get(id=request.session['user_address_id'])
        specific_order = Order.objects.create(user=specific_user,
                                            ref_code=ref,
                                            payment=request.session.get('paymentMethod'),
                                            ordered=True,
                                            shipping_address=this_address,
                                            total_payed_amount=float(request.session['total'])
                                            )#motaz
        request.session['order_id']=specific_order.id#motaz
        all_item_order=specific_user.order_items_for_user.all()
        for item in all_item_order:
            specific_order.items.add(item)
    return redirect('/complete_payment')

def complete_payment(request):
    if not 'user_id' in request.session:
        messages.error(request,"You have to login first")
        return redirect('/login')
    else:
        if request.method == 'POST':
            errors = payment_info.objects.basic_validator_payment(request.POST)
            if len(errors) > 0 :
                print('not')
                return redirect('/complete_payment')
            else:
                specific_user= User.objects.get(id=request.session['user_id'])
                specific_order=Order.objects.get(id=request.session['order_id'])
                payment_info.objects.create(
                    order=specific_order,
                    card_number=request.POST['cardNumber'],
                    expiry_date=request.POST['expiryDate'],
                    cvc=request.POST['cvc'],
                    card_holder_name=request.POST['cardHolderName']
                    )
                print('done')
                return redirect('/complete')
        else:
            specific_user= User.objects.get(id=request.session['user_id'])#motaz
            all_user_items=specific_user.order_items_for_user.all()#motaz
            
            print('notdone')
            context = {
            'all_user_items':all_user_items,
            'specific_user': specific_user
            }
            return render(request, "complete_payment.html", context)

#///////////////////////////////////////////////////////////////////motaz
def complete(request):
    if not 'user_id' in request.session:
        messages.error(request,"You have to login first")
        return redirect('/login')
    else:
        specific_user= User.objects.get(id=request.session['user_id'])
        all_user_items=specific_user.order_items_for_user.all()
        for item in all_user_items:
            item.user.remove(specific_user)
        
        return redirect('/invoice')
    

def cancel_order_items(request):
    if not 'user_id' in request.session:
        messages.error(request,"You have to login first")
        return redirect('/login')
    else:
        specific_user= User.objects.get(id=request.session['user_id'])
        all_user_items=specific_user.order_items_for_user.all()
        for item in all_user_items:
            item.delete()
        return redirect('/')

def cancel_order(request):
    if not 'user_id' in request.session:
        messages.error(request,"You have to login first")
        return redirect('/login')
    else:
        specific_user= User.objects.get(id=request.session['user_id'])
        all_user_items=specific_user.order_items_for_user.all()
        for item in all_user_items:
            item.delete()
        specific_order=Order.objects.get(id=request.session['order_id'])
        specific_order.delete()
        return redirect('/')

def user_orders(request):
    if not 'user_id' in request.session:
        messages.error(request,"You have to login first")
        return redirect('/login')
    else:
        specific_user= User.objects.get(id=request.session['user_id'])
        all_orders=Order.objects.filter(user=specific_user).order_by("-id")
        context = {
            'specific_user': specific_user,
            'all_orders':all_orders,
            
        }
        return render(request, "your_orders.html", context)
# /////////////////////motaz 
def change_password(request):
    if request.method == 'POST':
        errors= User.objects.basic_validator2(request.POST)
        if len(errors) > 0 :
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/change-password')
        else:
            this_user_email=User.objects.filter(email=request.POST['email'])
            if this_user_email:
                this_user=this_user_email[0]
                if bcrypt.checkpw(request.POST['currentPassword'].encode(), this_user.password.encode()):
                    hash1= bcrypt.hashpw(request.POST['newpassword'].encode(), bcrypt.gensalt()).decode()
                    if request.POST['newpassword']==request.POST['password_confirm']:
                        this_user.password=hash1
                        this_user.save()
                        messages.success(request, "Password Changed successfully")
                        return redirect('/')
                    else:
                        messages.error(request, "new password don't match confirm password")
                        return render(request, 'change_password.html')
                else:
                        messages.error(request, "Wrong Password")
                        return render(request, 'change_password.html')    
            else:
                messages.error(request, "Invalid authentifications")
                return render(request, 'change_password.html')
        # form = PasswordChangeForm(request.user, request.POST)
        # if form.is_valid():
        #     user = form.save()
        #     update_session_auth_hash(request, user)
        #     messages.success(request, 'Your password was successfully updated!')
        #     return redirect('your_account.html')
        # else:
        #     messages.error(request, 'Please correct the error below.')
    else:
        
        return render(request, 'change_password.html')
    
    
def search_order(request):
    
    search = Order.objects.filter(ref_code__startswith=request.POST['search_order_ajax'])
    if search:
        
        for items in  search.all():
            
            context={
                'search':search.all()
            }
            
    return render(request,'ajax_search_order.html',context)

def invoice(request):
    context={
                'specific_order': Order.objects.get(id=request.session['order_id'])
            }
    return render(request,'index.html', context)