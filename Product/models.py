from django.conf import settings  # ✅ Import the User model
from django.db import models

class Product(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ✅ Links product to a user
    CATEGORY = (
        ('Appliance', 'APPLIANCE'),
        ('Clothing', 'CLOTHING'),
        ('Gadget', 'GADGET'),
        ('Others', 'OTHERS'),
    )
    image = models.ImageField(upload_to='images/', null=True, blank=True) 
    productname = models.CharField(max_length=500, blank=True)
    description = models.CharField(max_length=10000, blank=True)
    category = models.CharField(choices=CATEGORY, max_length=500, blank=True, default=CATEGORY[-1])
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # ✅ Use DecimalField for prices
    gender = models.CharField(max_length=100, blank=True)  # ✅ lowercase for field names
    colour = models.CharField(max_length=100, blank=True)
    condition = models.CharField(max_length=300, blank=True)
    location = models.CharField(max_length=500, blank=True)
    is_sold = models.BooleanField(default=False)
    

    def __str__(self):
        return f"{self.productname} ({self.user.email})"  # ✅ Shows user who created it
