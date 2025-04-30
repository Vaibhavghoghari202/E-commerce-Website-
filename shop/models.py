from django.db import models

# Create your models here.
class Product(models.Model):
    Product_id=models.AutoField
    Product_name = models.CharField(max_length=255)
    category =models.CharField(max_length=50 , default="")
    subcategory =models.CharField(max_length=50,default="")
    price = models.IntegerField(default=0)
    image = models.ImageField(upload_to='sshop/image',default="")
    Desc= models.CharField(max_length=1000)
    pub_data=models.DateField()

    def __str__(self) :
        return self.Product_name
    
class Registration(models.Model):
    ID=models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100, default="")
    Phone = models.CharField(max_length=100, default="")
    address = models.CharField(max_length=500, default="")
    password=models.CharField(max_length=100,default="")
    cpassword = models.CharField(max_length=100,default="")
    gender = models.CharField(max_length=500, default="")

    def __str__(self) :
        return self.name
    
class Contact(models.Model):
    mess_id=models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100, default="")
    Phone = models.CharField(max_length=100, default="")
    message = models.CharField(max_length=500, default="")

    def __str__(self) :
        return self.name
    

class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    items_json = models.CharField(max_length=5000)
    amount = models.IntegerField(default=0)
    fname= models.CharField(max_length=111)
    lname = models.CharField(max_length=111)
    phone_Number = models.CharField(max_length=99)
    gender = models.CharField(max_length=111)
    address= models.CharField(max_length=111)
    city = models.CharField(max_length=111)
    county = models.CharField(max_length=111)
    zip_code = models.CharField(max_length=111)
    paypal_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    paypal_payer_email = models.CharField(max_length=100, null=True, blank=True)
    payment_status = models.CharField(max_length=50, default="Pending")
    
    def __str__(self) :
        return self.fname
    
class OrderUpdate(models.Model):
    update_id = models.AutoField(primary_key=True)
    order = models.ForeignKey('Orders', on_delete=models.CASCADE)
    update_desc = models.CharField(max_length=5000)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.update_desc[:30] + "..."