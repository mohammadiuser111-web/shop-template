#!/usr/bin/env python
"""
Import demo data
Shop Template - Django E-commerce Template
"""

import os
import sys
import json
from pathlib import Path

# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Add project directory to path
sys.path.insert(0, str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_template.settings')
import django
django.setup()

from django.core.management import call_command
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction

# Import models
from core.models import (
    Setting,
    SiteSetting,
    SocialLink,
    ContactInfo,
    Menu,
    MenuItem,
    Page,
    Advertisement,
    AdvertisementPlacement,
)
from users.models import User, UserProfile, Address
from products.models import (
    Category,
    Brand,
    Product,
    ProductImage,
    ProductVariant,
    ProductAttribute,
    ProductAttributeValue,
    Tag,
)
from blog.models import (
    BlogCategory,
    BlogTag,
    BlogPost,
    BlogPostImage,
    Comment,
)
from orders.models import Order, OrderItem, Payment, ShippingAddress, BillingAddress
from reviews.models import Review, Rating
from wishlist.models import Wishlist, WishlistItem
from compare.models import Compare, CompareItem
from coupons.models import Coupon, CouponUsage
from newsletter.models import NewsletterSubscription, NewsletterCampaign

# Faker for generating fake data
try:
    from faker import Faker
    fake = Faker()
    FAKER_AVAILABLE = True
except ImportError:
    FAKER_AVAILABLE = False
    print("Warning: Faker library not installed. Using default data.")


UserModel = get_user_model()


def create_superuser():
    """Create a superuser"""
    print("Creating superuser...")
    
    UserModel.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
        }
    )
    
    print("Superuser created: admin/admin@example.com")


def create_users(count=10):
    """Create demo users"""
    print(f"Creating {count} demo users...")
    
    users = []
    for i in range(count):
        if FAKER_AVAILABLE:
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{first_name.lower()}_{last_name.lower()}"[:30]
            email = fake.email()
        else:
            first_name = f"User{i+1}"
            last_name = "Demo"
            username = f"user{i+1}"
            email = f"user{i+1}@example.com"
        
        user = UserModel.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'is_active': True,
            }
        )[0]
        users.append(user)
        
        # Create user profile
        UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'phone': fake.phone_number() if FAKER_AVAILABLE else f"+123456789{i}",
                'bio': fake.text(100) if FAKER_AVAILABLE else f"Bio for user {i+1}",
                'birth_date': fake.date_of_birth() if FAKER_AVAILABLE else timezone.now().date(),
                'gender': 'male' if i % 2 == 0 else 'female',
                'newsletter_subscribed': True,
            }
        )
        
        # Create address
        Address.objects.get_or_create(
            user=user,
            defaults={
                'address_type': 'billing',
                'first_name': first_name,
                'last_name': last_name,
                'address_line_1': fake.street_address() if FAKER_AVAILABLE else f"{i+1} Main St",
                'address_line_2': fake.secondary_address() if FAKER_AVAILABLE else "",
                'city': fake.city() if FAKER_AVAILABLE else "New York",
                'state': fake.state_abbr() if FAKER_AVAILABLE else "NY",
                'postal_code': fake.zipcode() if FAKER_AVAILABLE else "10001",
                'country': 'US',
                'phone': fake.phone_number() if FAKER_AVAILABLE else f"+123456789{i}",
                'is_default': True,
            }
        )
    
    print(f"Created {count} demo users")
    return users


def create_categories():
    """Create demo categories"""
    print("Creating categories...")
    
    categories = [
        {
            'name': 'Electronics',
            'slug': 'electronics',
            'description': 'Electronic devices and gadgets',
            'icon': 'electronics',
            'is_featured': True,
            'children': [
                {'name': 'Smartphones', 'slug': 'smartphones', 'description': 'Mobile phones and accessories'},
                {'name': 'Laptops', 'slug': 'laptops', 'description': 'Laptops and notebooks'},
                {'name': 'Tablets', 'slug': 'tablets', 'description': 'Tablet computers'},
                {'name': 'Audio', 'slug': 'audio', 'description': 'Headphones, speakers, and audio equipment'},
                {'name': 'Cameras', 'slug': 'cameras', 'description': 'Digital cameras and accessories'},
            ]
        },
        {
            'name': 'Clothing',
            'slug': 'clothing',
            'description': 'Clothing and apparel',
            'icon': 'clothing',
            'is_featured': True,
            'children': [
                {'name': "Men's Clothing", 'slug': 'mens-clothing', 'description': "Men's clothing"},
                {'name': "Women's Clothing", 'slug': 'womens-clothing', 'description': "Women's clothing"},
                {'name': 'Kids Clothing', 'slug': 'kids-clothing', 'description': 'Children clothing'},
                {'name': 'Accessories', 'slug': 'accessories', 'description': 'Fashion accessories'},
            ]
        },
        {
            'name': 'Home & Garden',
            'slug': 'home-garden',
            'description': 'Home and garden products',
            'icon': 'home',
            'is_featured': True,
            'children': [
                {'name': 'Furniture', 'slug': 'furniture', 'description': 'Home furniture'},
                {'name': 'Decor', 'slug': 'decor', 'description': 'Home decoration'},
                {'name': 'Kitchen', 'slug': 'kitchen', 'description': 'Kitchen appliances and tools'},
                {'name': 'Bedding', 'slug': 'bedding', 'description': 'Bedding and linens'},
            ]
        },
        {
            'name': 'Books & Media',
            'slug': 'books-media',
            'description': 'Books, movies, and music',
            'icon': 'books',
            'is_featured': False,
            'children': [
                {'name': 'Books', 'slug': 'books', 'description': 'Printed books'},
                {'name': 'E-books', 'slug': 'ebooks', 'description': 'Electronic books'},
                {'name': 'Movies', 'slug': 'movies', 'description': 'DVDs and Blu-rays'},
                {'name': 'Music', 'slug': 'music', 'description': 'CDs and vinyl records'},
            ]
        },
        {
            'name': 'Sports & Outdoors',
            'slug': 'sports-outdoors',
            'description': 'Sports equipment and outdoor gear',
            'icon': 'sports',
            'is_featured': False,
            'children': [
                {'name': 'Fitness', 'slug': 'fitness', 'description': 'Fitness equipment'},
                {'name': 'Camping', 'slug': 'camping', 'description': 'Camping gear'},
                {'name': 'Sports', 'slug': 'sports', 'description': 'Sports equipment'},
                {'name': 'Outdoors', 'slug': 'outdoors', 'description': 'Outdoor activities gear'},
            ]
        },
    ]
    
    created_categories = []
    for category_data in categories:
        category = Category.objects.get_or_create(
            slug=category_data['slug'],
            defaults={
                'name': category_data['name'],
                'description': category_data['description'],
                'icon': category_data.get('icon', ''),
                'is_featured': category_data.get('is_featured', False),
                'is_active': True,
                'sort_order': 0,
            }
        )[0]
        created_categories.append(category)
        
        # Create child categories
        for child_data in category_data.get('children', []):
            Category.objects.get_or_create(
                slug=child_data['slug'],
                defaults={
                    'name': child_data['name'],
                    'description': child_data['description'],
                    'parent': category,
                    'is_active': True,
                    'sort_order': 0,
                }
            )
    
    print(f"Created {len(created_categories)} main categories")
    return created_categories


def create_brands():
    """Create demo brands"""
    print("Creating brands...")
    
    brands = [
        {'name': 'Apple', 'slug': 'apple', 'description': 'Innovative technology company', 'logo': None, 'is_featured': True},
        {'name': 'Samsung', 'slug': 'samsung', 'description': 'Global technology leader', 'logo': None, 'is_featured': True},
        {'name': 'Sony', 'slug': 'sony', 'description': 'Electronics and entertainment', 'logo': None, 'is_featured': True},
        {'name': 'Nike', 'slug': 'nike', 'description': 'Athletic footwear and apparel', 'logo': None, 'is_featured': True},
        {'name': 'Adidas', 'slug': 'adidas', 'description': 'Sports clothing and shoes', 'logo': None, 'is_featured': True},
        {'name': 'LG', 'slug': 'lg', 'description': 'Electronics and appliances', 'logo': None, 'is_featured': False},
        {'name': 'Dell', 'slug': 'dell', 'description': 'Computer technology', 'logo': None, 'is_featured': False},
        {'name': 'HP', 'slug': 'hp', 'description': 'Hewlett Packard', 'logo': None, 'is_featured': False},
        {'name': 'Canon', 'slug': 'canon', 'description': 'Imaging and optical products', 'logo': None, 'is_featured': False},
        {'name': 'Panasonic', 'slug': 'panasonic', 'description': 'Electronics manufacturer', 'logo': None, 'is_featured': False},
    ]
    
    created_brands = []
    for brand_data in brands:
        brand = Brand.objects.get_or_create(
            slug=brand_data['slug'],
            defaults={
                'name': brand_data['name'],
                'description': brand_data['description'],
                'is_featured': brand_data.get('is_featured', False),
                'is_active': True,
                'sort_order': 0,
            }
        )[0]
        created_brands.append(brand)
    
    print(f"Created {len(created_brands)} brands")
    return created_brands


def create_tags():
    """Create demo tags"""
    print("Creating tags...")
    
    tags = [
        'new', 'sale', 'popular', 'featured', 'bestseller',
        'discount', 'limited', 'exclusive', 'premium', 'budget',
        'wireless', 'smart', '4k', 'hd', 'bluetooth',
        'waterproof', 'durable', 'lightweight', 'portable', 'eco-friendly',
    ]
    
    created_tags = []
    for tag_name in tags:
        tag = Tag.objects.get_or_create(
            name=tag_name,
            defaults={
                'slug': tag_name,
                'description': f"{tag_name.replace('-', ' ').title()} products",
            }
        )[0]
        created_tags.append(tag)
    
    print(f"Created {len(created_tags)} tags")
    return created_tags


def create_attributes():
    """Create demo product attributes"""
    print("Creating product attributes...")
    
    attributes = [
        {
            'name': 'Color',
            'slug': 'color',
            'type': 'color',
            'is_filterable': True,
            'is_variant': True,
            'values': [
                {'name': 'Black', 'slug': 'black', 'color_code': '#000000'},
                {'name': 'White', 'slug': 'white', 'color_code': '#ffffff'},
                {'name': 'Red', 'slug': 'red', 'color_code': '#ff0000'},
                {'name': 'Blue', 'slug': 'blue', 'color_code': '#0000ff'},
                {'name': 'Green', 'slug': 'green', 'color_code': '#00ff00'},
                {'name': 'Silver', 'slug': 'silver', 'color_code': '#c0c0c0'},
                {'name': 'Gold', 'slug': 'gold', 'color_code': '#ffd700'},
            ]
        },
        {
            'name': 'Size',
            'slug': 'size',
            'type': 'size',
            'is_filterable': True,
            'is_variant': True,
            'values': [
                {'name': 'XS', 'slug': 'xs'},
                {'name': 'S', 'slug': 's'},
                {'name': 'M', 'slug': 'm'},
                {'name': 'L', 'slug': 'l'},
                {'name': 'XL', 'slug': 'xl'},
                {'name': 'XXL', 'slug': 'xxl'},
            ]
        },
        {
            'name': 'Storage',
            'slug': 'storage',
            'type': 'text',
            'is_filterable': True,
            'is_variant': True,
            'values': [
                {'name': '16GB', 'slug': '16gb'},
                {'name': '32GB', 'slug': '32gb'},
                {'name': '64GB', 'slug': '64gb'},
                {'name': '128GB', 'slug': '128gb'},
                {'name': '256GB', 'slug': '256gb'},
                {'name': '512GB', 'slug': '512gb'},
                {'name': '1TB', 'slug': '1tb'},
            ]
        },
        {
            'name': 'Material',
            'slug': 'material',
            'type': 'text',
            'is_filterable': True,
            'is_variant': False,
            'values': [
                {'name': 'Plastic', 'slug': 'plastic'},
                {'name': 'Metal', 'slug': 'metal'},
                {'name': 'Glass', 'slug': 'glass'},
                {'name': 'Wood', 'slug': 'wood'},
                {'name': 'Fabric', 'slug': 'fabric'},
                {'name': 'Leather', 'slug': 'leather'},
            ]
        },
        {
            'name': 'Resolution',
            'slug': 'resolution',
            'type': 'text',
            'is_filterable': True,
            'is_variant': False,
            'values': [
                {'name': 'HD', 'slug': 'hd'},
                {'name': 'Full HD', 'slug': 'full-hd'},
                {'name': '4K UHD', 'slug': '4k-uhd'},
                {'name': '8K UHD', 'slug': '8k-uhd'},
            ]
        },
    ]
    
    created_attributes = []
    for attr_data in attributes:
        attribute = ProductAttribute.objects.get_or_create(
            slug=attr_data['slug'],
            defaults={
                'name': attr_data['name'],
                'type': attr_data['type'],
                'is_filterable': attr_data.get('is_filterable', False),
                'is_variant': attr_data.get('is_variant', False),
                'is_active': True,
                'sort_order': 0,
            }
        )[0]
        created_attributes.append(attribute)
        
        # Create attribute values
        for value_data in attr_data.get('values', []):
            ProductAttributeValue.objects.get_or_create(
                attribute=attribute,
                slug=value_data['slug'],
                defaults={
                    'name': value_data['name'],
                    'color_code': value_data.get('color_code', ''),
                    'sort_order': 0,
                }
            )
    
    print(f"Created {len(created_attributes)} product attributes")
    return created_attributes


def create_products(count=50):
    """Create demo products"""
    print(f"Creating {count} demo products...")
    
    # Get categories
    categories = Category.objects.all()
    if not categories.exists():
        create_categories()
        categories = Category.objects.all()
    
    # Get brands
    brands = Brand.objects.all()
    if not brands.exists():
        create_brands()
        brands = Brand.objects.all()
    
    # Get tags
    tags = Tag.objects.all()
    if not tags.exists():
        create_tags()
        tags = Tag.objects.all()
    
    # Get attributes
    attributes = ProductAttribute.objects.all()
    if not attributes.exists():
        create_attributes()
        attributes = ProductAttribute.objects.all()
    
    products = []
    for i in range(count):
        if FAKER_AVAILABLE:
            name = fake.catch_phrase()[:50]
            description = fake.text(500)
            short_description = fake.text(100)
        else:
            name = f"Product {i+1}"
            description = f"Description for product {i+1}"
            short_description = f"Short description for product {i+1}"
        
        category = categories.order_by('?').first()
        brand = brands.order_by('?').first()
        
        # Calculate prices
        base_price = fake.random_int(10, 500) if FAKER_AVAILABLE else (i % 10 + 1) * 50
        sale_price = base_price - (base_price * 0.2) if i % 5 == 0 else None
        
        product = Product.objects.get_or_create(
            slug=f"product-{i+1}",
            defaults={
                'name': name,
                'description': description,
                'short_description': short_description,
                'sku': f"SKU{i+1:05d}",
                'category': category,
                'brand': brand,
                'regular_price': base_price,
                'sale_price': sale_price,
                'cost_price': base_price * 0.7,
                'weight': fake.random_int(100, 5000) if FAKER_AVAILABLE else 1000,
                'weight_unit': 'g',
                'length': fake.random_int(1, 100) if FAKER_AVAILABLE else 10,
                'width': fake.random_int(1, 100) if FAKER_AVAILABLE else 10,
                'height': fake.random_int(1, 100) if FAKER_AVAILABLE else 10,
                'dimension_unit': 'cm',
                'stock_quantity': fake.random_int(1, 1000) if FAKER_AVAILABLE else 100,
                'low_stock_threshold': 10,
                'is_in_stock': True,
                'is_featured': i < 10,
                'is_popular': i < 20,
                'is_new': i < 5,
                'is_bestseller': i < 15,
                'is_active': True,
                'is_digital': False,
                'is_shippable': True,
                'is_taxable': True,
                'tax_rate': 0.1,
                'sort_order': i,
                'meta_title': name,
                'meta_description': short_description,
                'meta_keywords': ', '.join([name, category.name if category else '', brand.name if brand else '']),
                'tags': ', '.join([tag.name for tag in tags.order_by('?')[:3]]),
            }
        )[0]
        products.append(product)
        
        # Add tags
        product.tags.set(tags.order_by('?')[:3])
        
        # Add product attributes
        for attr in attributes[:3]:
            value = attr.values.order_by('?').first()
            if value:
                product.attributes.create(
                    attribute=attr,
                    value=value,
                )
        
        # Create product variants
        if i % 2 == 0:
            color_attr = attributes.filter(slug='color').first()
            size_attr = attributes.filter(slug='size').first()
            
            if color_attr and size_attr:
                color_values = color_attr.values.all()[:3]
                size_values = size_attr.values.all()[:2]
                
                for color in color_values:
                    for size in size_values:
                        variant_price = base_price + (color.id * 5) + (size.id * 10)
                        ProductVariant.objects.get_or_create(
                            product=product,
                            sku=f"SKU{i+1:05d}-{color.slug}-{size.slug}",
                            defaults={
                                'name': f"{name} - {color.name} / {size.name}",
                                'regular_price': variant_price,
                                'sale_price': variant_price * 0.8 if i % 5 == 0 else None,
                                'stock_quantity': fake.random_int(1, 100) if FAKER_AVAILABLE else 50,
                                'is_default': False,
                                'is_active': True,
                            }
                        )
        
        # Create default variant
        ProductVariant.objects.get_or_create(
            product=product,
            sku=f"SKU{i+1:05d}-DEFAULT",
            defaults={
                'name': name,
                'regular_price': base_price,
                'sale_price': sale_price,
                'stock_quantity': product.stock_quantity,
                'is_default': True,
                'is_active': True,
            }
        )
    
    print(f"Created {len(products)} products")
    return products


def create_blog_categories():
    """Create demo blog categories"""
    print("Creating blog categories...")
    
    categories = [
        {
            'name': 'Technology',
            'slug': 'technology',
            'description': 'Latest technology news and trends',
            'is_featured': True,
            'children': [
                {'name': 'Gadgets', 'slug': 'gadgets', 'description': 'Latest gadgets and devices'},
                {'name': 'Software', 'slug': 'software', 'description': 'Software and applications'},
                {'name': 'Hardware', 'slug': 'hardware', 'description': 'Hardware reviews and news'},
            ]
        },
        {
            'name': 'Fashion',
            'slug': 'fashion',
            'description': 'Fashion trends and styles',
            'is_featured': True,
            'children': [
                {'name': "Men's Fashion", 'slug': 'mens-fashion', 'description': "Men's fashion trends"},
                {'name': "Women's Fashion", 'slug': 'womens-fashion', 'description': "Women's fashion trends"},
                {'name': 'Accessories', 'slug': 'accessories', 'description': 'Fashion accessories'},
            ]
        },
        {
            'name': 'Lifestyle',
            'slug': 'lifestyle',
            'description': 'Lifestyle articles and tips',
            'is_featured': True,
            'children': [
                {'name': 'Travel', 'slug': 'travel', 'description': 'Travel guides and tips'},
                {'name': 'Food', 'slug': 'food', 'description': 'Recipes and food trends'},
                {'name': 'Health', 'slug': 'health', 'description': 'Health and wellness'},
            ]
        },
        {
            'name': 'Business',
            'slug': 'business',
            'description': 'Business news and advice',
            'is_featured': False,
            'children': [
                {'name': 'Startups', 'slug': 'startups', 'description': 'Startup news and advice'},
                {'name': 'Finance', 'slug': 'finance', 'description': 'Financial news and tips'},
                {'name': 'Marketing', 'slug': 'marketing', 'description': 'Marketing strategies'},
            ]
        },
    ]
    
    created_categories = []
    for category_data in categories:
        category = BlogCategory.objects.get_or_create(
            slug=category_data['slug'],
            defaults={
                'name': category_data['name'],
                'description': category_data['description'],
                'is_featured': category_data.get('is_featured', False),
                'is_active': True,
                'sort_order': 0,
            }
        )[0]
        created_categories.append(category)
        
        # Create child categories
        for child_data in category_data.get('children', []):
            BlogCategory.objects.get_or_create(
                slug=child_data['slug'],
                defaults={
                    'name': child_data['name'],
                    'description': child_data['description'],
                    'parent': category,
                    'is_active': True,
                    'sort_order': 0,
                }
            )
    
    print(f"Created {len(created_categories)} blog categories")
    return created_categories


def create_blog_tags():
    """Create demo blog tags"""
    print("Creating blog tags...")
    
    tags = [
        'technology', 'fashion', 'lifestyle', 'business', 'news',
        'tips', 'trends', 'reviews', 'guide', 'tutorial',
        'diy', 'inspiration', 'health', 'travel', 'food',
        'startups', 'finance', 'marketing', 'gadgets', 'software',
    ]
    
    created_tags = []
    for tag_name in tags:
        tag = BlogTag.objects.get_or_create(
            name=tag_name,
            defaults={
                'slug': tag_name,
                'description': f"{tag_name.replace('-', ' ').title()} blog posts",
            }
        )[0]
        created_tags.append(tag)
    
    print(f"Created {len(created_tags)} blog tags")
    return created_tags


def create_blog_posts(count=20):
    """Create demo blog posts"""
    print(f"Creating {count} demo blog posts...")
    
    # Get users
    users = UserModel.objects.all()
    if not users.exists():
        create_users(5)
        users = UserModel.objects.all()
    
    # Get blog categories
    categories = BlogCategory.objects.all()
    if not categories.exists():
        create_blog_categories()
        categories = BlogCategory.objects.all()
    
    # Get blog tags
    tags = BlogTag.objects.all()
    if not tags.exists():
        create_blog_tags()
        tags = BlogTag.objects.all()
    
    posts = []
    for i in range(count):
        if FAKER_AVAILABLE:
            title = fake.catch_phrase()[:100]
            excerpt = fake.text(200)
            content = '<p>' + '</p><p>'.join(fake.paragraphs(5)) + '</p>'
        else:
            title = f"Blog Post {i+1}"
            excerpt = f"Excerpt for blog post {i+1}"
            content = f"<p>Content for blog post {i+1}</p>" * 5
        
        category = categories.order_by('?').first()
        author = users.order_by('?').first()
        
        post = BlogPost.objects.get_or_create(
            slug=f"blog-post-{i+1}",
            defaults={
                'title': title,
                'excerpt': excerpt,
                'content': content,
                'category': category,
                'author': author,
                'featured_image': None,
                'is_featured': i < 5,
                'is_popular': i < 10,
                'is_published': True,
                'published_at': timezone.now() - timezone.timedelta(days=i),
                'is_comment_enabled': True,
                'comment_count': fake.random_int(0, 50) if FAKER_AVAILABLE else i % 10,
                'view_count': fake.random_int(100, 10000) if FAKER_AVAILABLE else i * 100,
                'like_count': fake.random_int(0, 500) if FAKER_AVAILABLE else i * 10,
                'reading_time': fake.random_int(1, 20) if FAKER_AVAILABLE else (i % 10) + 1,
                'is_active': True,
                'sort_order': i,
                'meta_title': title,
                'meta_description': excerpt,
                'meta_keywords': ', '.join([title, category.name if category else '']),
            }
        )[0]
        posts.append(post)
        
        # Add tags
        post.tags.set(tags.order_by('?')[:3])
        
        # Create comments
        for j in range(i % 5):
            comment_author = users.order_by('?').first()
            Comment.objects.get_or_create(
                post=post,
                author=comment_author,
                defaults={
                    'content': fake.text(200) if FAKER_AVAILABLE else f"Comment {j+1}",
                    'is_approved': True,
                    'is_spam': False,
                    'parent': None,
                    'created_at': timezone.now() - timezone.timedelta(days=i, hours=j),
                }
            )
    
    print(f"Created {len(posts)} blog posts")
    return posts


def create_settings():
    """Create demo settings"""
    print("Creating settings...")
    
    # Site settings
    SiteSetting.objects.get_or_create(
        key='site_name',
        defaults={'value': 'Shop Template'}
    )
    SiteSetting.objects.get_or_create(
        key='site_description',
        defaults={'value': 'A complete e-commerce solution built with Django'}
    )
    SiteSetting.objects.get_or_create(
        key='site_keywords',
        defaults={'value': 'e-commerce, django, shop, store, online shopping'}
    )
    SiteSetting.objects.get_or_create(
        key='site_author',
        defaults={'value': 'Shop Template Team'}
    )
    SiteSetting.objects.get_or_create(
        key='site_email',
        defaults={'value': 'info@shoptemplate.com'}
    )
    SiteSetting.objects.get_or_create(
        key='site_phone',
        defaults={'value': '+1 234 567 890'}
    )
    SiteSetting.objects.get_or_create(
        key='site_address',
        defaults={'value': '123 Main Street, City, Country'}
    )
    SiteSetting.objects.get_or_create(
        key='site_favicon',
        defaults={'value': ''}
    )
    SiteSetting.objects.get_or_create(
        key='site_logo',
        defaults={'value': ''}
    )
    SiteSetting.objects.get_or_create(
        key='default_currency',
        defaults={'value': 'USD'}
    )
    SiteSetting.objects.get_or_create(
        key='default_language',
        defaults={'value': 'en'}
    )
    SiteSetting.objects.get_or_create(
        key='timezone',
        defaults={'value': 'UTC'}
    )
    SiteSetting.objects.get_or_create(
        key='date_format',
        defaults={'value': 'F j, Y'}
    )
    SiteSetting.objects.get_or_create(
        key='time_format',
        defaults={'value': 'g:i a'}
    )
    SiteSetting.objects.get_or_create(
        key='datetime_format',
        defaults={'value': 'F j, Y g:i a'}
    )
    
    # Store settings
    SiteSetting.objects.get_or_create(
        key='items_per_page',
        defaults={'value': '12'}
    )
    SiteSetting.objects.get_or_create(
        key='blog_posts_per_page',
        defaults={'value': '10'}
    )
    SiteSetting.objects.get_or_create(
        key='product_reviews_enabled',
        defaults={'value': 'True'}
    )
    SiteSetting.objects.get_or_create(
        key='product_reviews_approval',
        defaults={'value': 'True'}
    )
    SiteSetting.objects.get_or_create(
        key='product_ratings_enabled',
        defaults={'value': 'True'}
    )
    SiteSetting.objects.get_or_create(
        key='wishlist_enabled',
        defaults={'value': 'True'}
    )
    SiteSetting.objects.get_or_create(
        key='compare_enabled',
        defaults={'value': 'True'}
    )
    SiteSetting.objects.get_or_create(
        key='newsletter_enabled',
        defaults={'value': 'True'}
    )
    SiteSetting.objects.get_or_create(
        key='social_login_enabled',
        defaults={'value': 'True'}
    )
    
    # SEO settings
    SiteSetting.objects.get_or_create(
        key='meta_title_suffix',
        defaults={'value': '| Shop Template'}
    )
    SiteSetting.objects.get_or_create(
        key='meta_description_default',
        defaults={'value': 'A complete e-commerce solution built with Django'}
    )
    SiteSetting.objects.get_or_create(
        key='meta_keywords_default',
        defaults={'value': 'e-commerce, django, shop, store, online shopping'}
    )
    
    # Social links
    SocialLink.objects.get_or_create(
        platform='facebook',
        defaults={'url': 'https://facebook.com/shoptemplate', 'is_active': True, 'sort_order': 1}
    )
    SocialLink.objects.get_or_create(
        platform='twitter',
        defaults={'url': 'https://twitter.com/shoptemplate', 'is_active': True, 'sort_order': 2}
    )
    SocialLink.objects.get_or_create(
        platform='instagram',
        defaults={'url': 'https://instagram.com/shoptemplate', 'is_active': True, 'sort_order': 3}
    )
    SocialLink.objects.get_or_create(
        platform='linkedin',
        defaults={'url': 'https://linkedin.com/company/shoptemplate', 'is_active': True, 'sort_order': 4}
    )
    SocialLink.objects.get_or_create(
        platform='youtube',
        defaults={'url': 'https://youtube.com/shoptemplate', 'is_active': True, 'sort_order': 5}
    )
    
    # Contact info
    ContactInfo.objects.get_or_create(
        type='email',
        defaults={'value': 'info@shoptemplate.com', 'is_active': True, 'sort_order': 1}
    )
    ContactInfo.objects.get_or_create(
        type='phone',
        defaults={'value': '+1 234 567 890', 'is_active': True, 'sort_order': 2}
    )
    ContactInfo.objects.get_or_create(
        type='address',
        defaults={'value': '123 Main Street, City, Country', 'is_active': True, 'sort_order': 3}
    )
    
    # Menu
    main_menu = Menu.objects.get_or_create(
        name='Main Menu',
        defaults={'slug': 'main-menu', 'description': 'Main navigation menu', 'is_active': True, 'sort_order': 1}
    )[0]
    
    MenuItem.objects.get_or_create(
        menu=main_menu,
        title='Home',
        defaults={
            'url': '/',
            'parent': None,
            'is_active': True,
            'sort_order': 1,
            'target_blank': False,
            'icon': 'home',
        }
    )
    
    MenuItem.objects.get_or_create(
        menu=main_menu,
        title='Store',
        defaults={
            'url': '/store/',
            'parent': None,
            'is_active': True,
            'sort_order': 2,
            'target_blank': False,
            'icon': 'store',
        }
    )
    
    MenuItem.objects.get_or_create(
        menu=main_menu,
        title='Blog',
        defaults={
            'url': '/blog/',
            'parent': None,
            'is_active': True,
            'sort_order': 3,
            'target_blank': False,
            'icon': 'blog',
        }
    )
    
    MenuItem.objects.get_or_create(
        menu=main_menu,
        title='Contact',
        defaults={
            'url': '/contact/',
            'parent': None,
            'is_active': True,
            'sort_order': 4,
            'target_blank': False,
            'icon': 'contact',
        }
    )
    
    print("Settings created!")


def create_advertisements():
    """Create demo advertisements"""
    print("Creating advertisements...")
    
    placements = [
        'home_hero',
        'home_featured',
        'home_sidebar',
        'product_detail',
        'category_page',
        'blog_sidebar',
    ]
    
    for placement in placements:
        AdvertisementPlacement.objects.get_or_create(
            name=placement,
            defaults={
                'description': f'{placement.replace("_", " ").title()} advertisement placement',
                'is_active': True,
            }
        )
    
    placements = AdvertisementPlacement.objects.all()
    
    for i, placement in enumerate(placements):
        Advertisement.objects.get_or_create(
            title=f"Advertisement {i+1}",
            defaults={
                'placement': placement,
                'content': f"<div class='advertisement'><h3>Advertisement {i+1}</h3><p>This is a demo advertisement.</p></div>",
                'image': None,
                'url': f"https://example.com/ad/{i+1}",
                'is_active': True,
                'start_date': timezone.now() - timezone.timedelta(days=7),
                'end_date': timezone.now() + timezone.timedelta(days=30),
                'impressions': fake.random_int(100, 10000) if FAKER_AVAILABLE else i * 100,
                'clicks': fake.random_int(10, 1000) if FAKER_AVAILABLE else i * 10,
                'sort_order': i,
            }
        )
    
    print(f"Created {placements.count()} advertisement placements and {placements.count()} advertisements")


def create_coupons():
    """Create demo coupons"""
    print("Creating coupons...")
    
    coupons = [
        {
            'code': 'WELCOME10',
            'name': 'Welcome Discount',
            'description': '10% off for new customers',
            'discount_type': 'percentage',
            'discount_value': 10.0,
            'min_order_amount': 0.0,
            'max_order_amount': None,
            'usage_limit': 100,
            'per_user_limit': 1,
            'start_date': timezone.now() - timezone.timedelta(days=7),
            'end_date': timezone.now() + timezone.timedelta(days=30),
            'is_active': True,
            'applies_to': 'all',
        },
        {
            'code': 'SUMMER20',
            'name': 'Summer Sale',
            'description': '20% off on all products',
            'discount_type': 'percentage',
            'discount_value': 20.0,
            'min_order_amount': 50.0,
            'max_order_amount': None,
            'usage_limit': 50,
            'per_user_limit': 1,
            'start_date': timezone.now() - timezone.timedelta(days=7),
            'end_date': timezone.now() + timezone.timedelta(days=15),
            'is_active': True,
            'applies_to': 'all',
        },
        {
            'code': 'FREESHIP',
            'name': 'Free Shipping',
            'description': 'Free shipping on orders over $100',
            'discount_type': 'free_shipping',
            'discount_value': 0.0,
            'min_order_amount': 100.0,
            'max_order_amount': None,
            'usage_limit': None,
            'per_user_limit': None,
            'start_date': timezone.now() - timezone.timedelta(days=7),
            'end_date': None,
            'is_active': True,
            'applies_to': 'all',
        },
        {
            'code': 'FIXED50',
            'name': 'Fixed Discount',
            'description': '$50 off on orders over $200',
            'discount_type': 'fixed',
            'discount_value': 50.0,
            'min_order_amount': 200.0,
            'max_order_amount': None,
            'usage_limit': 20,
            'per_user_limit': 1,
            'start_date': timezone.now() - timezone.timedelta(days=7),
            'end_date': timezone.now() + timezone.timedelta(days=30),
            'is_active': True,
            'applies_to': 'all',
        },
    ]
    
    for coupon_data in coupons:
        Coupon.objects.get_or_create(
            code=coupon_data['code'],
            defaults=coupon_data
        )
    
    print(f"Created {len(coupons)} coupons")


def create_newsletter_subscriptions():
    """Create demo newsletter subscriptions"""
    print("Creating newsletter subscriptions...")
    
    subscriptions = []
    for i in range(20):
        if FAKER_AVAILABLE:
            email = fake.email()
        else:
            email = f"subscriber{i+1}@example.com"
        
        subscription = NewsletterSubscription.objects.get_or_create(
            email=email,
            defaults={
                'first_name': fake.first_name() if FAKER_AVAILABLE else f"Subscriber{i+1}",
                'last_name': fake.last_name() if FAKER_AVAILABLE else "Demo",
                'is_active': True,
                'is_verified': True,
                'verify_token': None,
                'subscribed_at': timezone.now() - timezone.timedelta(days=i),
            }
        )[0]
        subscriptions.append(subscription)
    
    print(f"Created {len(subscriptions)} newsletter subscriptions")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import demo data for Shop Template')
    parser.add_argument('--all', action='store_true', help='Import all demo data')
    parser.add_argument('--users', action='store_true', help='Import demo users')
    parser.add_argument('--categories', action='store_true', help='Import demo categories')
    parser.add_argument('--brands', action='store_true', help='Import demo brands')
    parser.add_argument('--tags', action='store_true', help='Import demo tags')
    parser.add_argument('--attributes', action='store_true', help='Import demo attributes')
    parser.add_argument('--products', action='store_true', help='Import demo products')
    parser.add_argument('--blog-categories', action='store_true', help='Import demo blog categories')
    parser.add_argument('--blog-tags', action='store_true', help='Import demo blog tags')
    parser.add_argument('--blog-posts', action='store_true', help='Import demo blog posts')
    parser.add_argument('--settings', action='store_true', help='Import demo settings')
    parser.add_argument('--advertisements', action='store_true', help='Import demo advertisements')
    parser.add_argument('--coupons', action='store_true', help='Import demo coupons')
    parser.add_argument('--newsletter', action='store_true', help='Import demo newsletter subscriptions')
    parser.add_argument('--count', type=int, default=50, metavar='N', help='Number of items to create (default: 50)')
    parser.add_argument('--clear', action='store_true', help='Clear existing data before importing')
    
    args = parser.parse_args()
    
    # Clear existing data if requested
    if args.clear:
        print("Clearing existing data...")
        # Note: Be careful with this in production!
        # This is just for demo purposes
        pass
    
    # Import data based on arguments
    if args.all:
        create_superuser()
        create_settings()
        create_users(args.count)
        create_categories()
        create_brands()
        create_tags()
        create_attributes()
        create_products(args.count)
        create_blog_categories()
        create_blog_tags()
        create_blog_posts(args.count // 3)
        create_advertisements()
        create_coupons()
        create_newsletter_subscriptions()
    else:
        if args.settings:
            create_settings()
        if args.users:
            create_users(args.count)
        if args.categories:
            create_categories()
        if args.brands:
            create_brands()
        if args.tags:
            create_tags()
        if args.attributes:
            create_attributes()
        if args.products:
            create_products(args.count)
        if args.blog_categories:
            create_blog_categories()
        if args.blog_tags:
            create_blog_tags()
        if args.blog_posts:
            create_blog_posts(args.count)
        if args.advertisements:
            create_advertisements()
        if args.coupons:
            create_coupons()
        if args.newsletter:
            create_newsletter_subscriptions()
        
        if not any([
            args.settings, args.users, args.categories, args.brands, args.tags,
            args.attributes, args.products, args.blog_categories, args.blog_tags,
            args.blog_posts, args.advertisements, args.coupons, args.newsletter
        ]):
            parser.print_help()


if __name__ == '__main__':
    print("=" * 60)
    print("Shop Template - Demo Data Importer")
    print("=" * 60)
    print()
    
    main()
    
    print()
    print("=" * 60)
    print("Demo data import completed!")
    print("=" * 60)
