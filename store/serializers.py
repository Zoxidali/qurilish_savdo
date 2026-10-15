from rest_framework import serializers
from .models import Category, Product, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'quantity', 'price')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    cashier_name = serializers.CharField(source='cashier.username', read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'cashier', 'cashier_name', 'total_price', 'payment_type', 'created_at', 'items')
        read_only_fields = ('total_price', 'created_at')

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        total_price = 0

        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']

            # Omborda mahsulot yetarliligini tekshirish
            if product.stock < quantity:
                raise serializers.ValidationError(
                    f"'{product.name}' uchun omborda yetarli miqdor yo'q. Qoldiq: {product.stock} {product.get_unit_display()}"
                )

            # Ombordan miqdorni ayirish
            product.stock -= quantity
            product.save()

            price = product.price
            line_total = price * quantity
            total_price += line_total

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price
            )

        order.total_price = total_price
        order.save()
        return order