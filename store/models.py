from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Kategoriya nomi")
    description = models.TextField(blank=True, null=True, verbose_name="Tavsif")

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"

    def __str__(self):
        return self.name
class Product(models.Model):
  name = models.CharField(max_length=255)
  category = models.ForeignKey(Category, on_delete=models.CASCADE)
  price = models.DecimalField(max_digits=10, decimal_places=2)
  stock = models.IntegerField(default=0)
  barcode = models.CharField(
      max_length=100, unique=True, null=True, blank=True
  )

class Product(models.Model):
    UNIT_CHOICES = (
        ('dona', 'Dona'),
        ('kg', 'Kilogramm'),
        ('metr', 'Metr'),
        ('m2', 'Kvadrat metr'),
        ('qop', 'Qop'),
    )

    name = models.CharField(max_length=255, verbose_name="Mahsulot nomi")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Kategoriya")
    sku = models.CharField(max_length=100, unique=True, verbose_name="Artikul / Shtrix-kod")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Sotish narxi")
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Tan narxi")
    stock = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Ombordagi qoldiq")
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='dona', verbose_name="O'lchov birligi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Qo'shilgan vaqt")

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"

    def __str__(self):
        return f"{self.name} ({self.stock} {self.get_unit_display()})"


class Order(models.Model):
    PAYMENT_TYPES = (
        ('cash', 'Naqd pul'),
        ('card', 'Plastik karta'),
        ('transfer', 'Pul o‘tkazma'),
    )

    cashier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Kassir")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Umumiy summa")
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, default='cash', verbose_name="To'lov turi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Sotilgan vaqt")
    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"

    def __str__(self):
        return f"Chek #{self.id} - {self.total_price} so'm"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Buyurtma")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Mahsulot")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Miqdori")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Sotish paytidagi narxi")

    class Meta:
        verbose_name = "Buyurtma elementi"
        verbose_name_plural = "Buyurtma elementlari"

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"