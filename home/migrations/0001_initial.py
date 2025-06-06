# Generated by Django 4.1.13 on 2025-04-16 06:00

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street', models.CharField(max_length=255)),
                ('ward', models.CharField(max_length=100)),
                ('district', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('is_default', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('visible', 'Hiển thị'), ('hidden', 'Ẩn')], default='visible', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'address',
            },
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'cart',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'category',
            },
        ),
        migrations.CreateModel(
            name='discount_percentage',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('percent', models.DecimalField(decimal_places=2, max_digits=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'discount_percentage',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('discount_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('payment_method', models.CharField(max_length=20)),
                ('status', models.CharField(choices=[('pending', 'Đang xử lý'), ('accept', 'Đang giao hàng'), ('done', 'Đã hoàn thành'), ('cancelled', 'Đã hủy')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer_phone', models.CharField(max_length=15)),
                ('payment_status', models.BooleanField(default=False)),
                ('re_pay', models.CharField(blank=True, max_length=20, null=True)),
                ('stk', models.IntegerField(blank=True, null=True)),
                ('address', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.address')),
            ],
            options={
                'db_table': 'orders',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('description2', models.TextField()),
                ('base_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id_discount_percentage', models.ForeignKey(db_column='id_discount_percentage', on_delete=django.db.models.deletion.CASCADE, related_name='discount_percentage', to='home.discount_percentage')),
            ],
            options={
                'db_table': 'product',
            },
        ),
        migrations.CreateModel(
            name='Productvariant',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('size', models.CharField(max_length=20)),
                ('color', models.CharField(max_length=50)),
                ('image', models.ImageField(upload_to='products/%Y/%m/%d')),
                ('stock', models.IntegerField(max_length=11)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='home.product')),
            ],
            options={
                'db_table': 'productvariant',
            },
        ),
        migrations.CreateModel(
            name='UserClient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255, unique=True)),
                ('first_name', models.CharField(max_length=150)),
                ('last_name', models.CharField(max_length=150)),
                ('email', models.EmailField(max_length=254)),
                ('phone_number', models.IntegerField(blank=True, null=True)),
                ('password', models.CharField(max_length=255)),
                ('auth_type', models.CharField(choices=[('email', 'Email'), ('facebook', 'Facebook'), ('tranditional', 'Tranditional'), ('google', 'Google')], max_length=20, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_login', models.DateField(blank=True)),
            ],
            options={
                'db_table': 'users',
            },
        ),
        migrations.CreateModel(
            name='Voucher',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=20, unique=True)),
                ('discount_amount', models.DecimalField(decimal_places=2, max_digits=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'voucher',
            },
        ),
        migrations.CreateModel(
            name='UserRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField()),
                ('comment', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='home.order')),
                ('product_variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='home.productvariant')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='home.userclient')),
            ],
            options={
                'verbose_name': 'User Rating',
                'verbose_name_plural': 'User Ratings',
                'db_table': 'userrating',
            },
        ),
        migrations.CreateModel(
            name='Producttype',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('category_id', models.ForeignKey(db_column='category_id', on_delete=django.db.models.deletion.CASCADE, to='home.category')),
            ],
            options={
                'db_table': 'producttype',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='type',
            field=models.ForeignKey(db_column='type', on_delete=django.db.models.deletion.CASCADE, to='home.producttype'),
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='home.order')),
                ('product_variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.productvariant')),
            ],
            options={
                'db_table': 'orderitem',
            },
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.userclient'),
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='home.order')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.userclient')),
            ],
            options={
                'db_table': 'feedback',
            },
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('cart_id', models.ForeignKey(db_column='cart_id', on_delete=django.db.models.deletion.CASCADE, related_name='items', to='home.cart')),
                ('product_variant_id', models.ForeignKey(db_column='product_variant_id', on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='home.productvariant')),
            ],
            options={
                'db_table': 'cartitem',
            },
        ),
        migrations.AddField(
            model_name='cart',
            name='user_id',
            field=models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, to='home.userclient'),
        ),
        migrations.AddField(
            model_name='address',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.userclient'),
        ),
        migrations.CreateModel(
            name='UsedVoucher',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('used_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='home.order')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='used_vouchers', to='home.userclient')),
                ('voucher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='used_by_users', to='home.voucher')),
            ],
            options={
                'db_table': 'used_voucher',
                'unique_together': {('user', 'voucher')},
            },
        ),
    ]
