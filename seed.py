"""
FREKS — Database Seeder
Run: python seed.py
Creates admin user, categories, and sample products.
"""
from app import create_app, db
from app.models import User, Category, Product, ProductVariant

app = create_app('development')

def seed():
    with app.app_context():
        db.create_all()

        # ── ADMIN USER ──────────────────────────────
        if not User.query.filter_by(username='freks_admin').first():
            admin = User(
                username='freks_admin',
                phone='01000000000',
                first_name='FREKS',
                last_name='Admin',
                is_admin=True
            )
            admin.set_password('Freks@2025!')
            db.session.add(admin)
            print('✓ Admin created — username: freks_admin  password: Freks@2025!')
        else:
            print('· Admin already exists')

        # ── DEMO USER ───────────────────────────────
        if not User.query.filter_by(username='jungle_user').first():
            demo = User(
            username='jungle_user',
            phone='01011111111',
            first_name='Amr',
            last_name='Cairo',
        )
            demo.set_password('Demo@2025!')
            db.session.add(demo)
            print('✓ Demo user created — username: jungle_user  password: Demo@2025!')
        else:
            print('· Demo user already exists')

        db.session.commit()

        # ── CATEGORIES ──────────────────────────────
        categories_data = [
            ('T-Shirts', 'tees'),
            ('Hoodies', 'hoodies'),
            ('Accessories', 'accessories'),
        ]
        cats = {}
        for name, slug in categories_data:
            cat = Category.query.filter_by(slug=slug).first()
            if not cat:
                cat = Category(name=name, slug=slug)
                db.session.add(cat)
                print(f'✓ Category: {name}')
            cats[slug] = cat

        db.session.commit()

        # ── PRODUCTS ────────────────────────────────
        sizes = ['XS', 'S', 'M', 'L', 'XL', 'XXL']

        products_data = [
            {
                'name': 'FREKS Void Tee',
                'description': 'The signature oversized tee. Pitch black. Heavyweight 300gsm cotton. Screen-printed FREKS glyph on the chest. Dropped shoulders, extended hem — built for the rave and the morning after.',
                'price': 850,
                'category': 'tees',
                'is_featured': True,
                'stock': {'XS': 5, 'S': 12, 'M': 20, 'L': 18, 'XL': 10, 'XXL': 6},
            },
            {
                'name': 'Jungle System Vol.1',
                'description': 'Lime acid on black. The Jungle System colorway in oversized tee form. Bold FREKS wordmark across the back. Egyptian cotton blend, pre-washed for softness.',
                'price': 950,
                'category': 'tees',
                'is_featured': True,
                'stock': {'XS': 3, 'S': 8, 'M': 15, 'L': 12, 'XL': 7, 'XXL': 4},
            },
            {
                'name': 'Afterlife Archive Tee',
                'description': 'Inspired by the iconic Afterlife visuals. Dark matter aesthetics printed on 280gsm premium cotton. Oversized boxy cut with raw hem finish.',
                'price': 800,
                'category': 'tees',
                'is_featured': True,
                'stock': {'XS': 0, 'S': 5, 'M': 10, 'L': 8, 'XL': 3, 'XXL': 0},
            },
            {
                'name': 'Cairo Underground Tee',
                'description': 'A love letter to Cairo\'s underground scene. Minimal front, chaotic back print. Heavyweight oversized silhouette.',
                'price': 780,
                'category': 'tees',
                'is_featured': False,
                'stock': {'XS': 6, 'S': 10, 'M': 14, 'L': 10, 'XL': 5, 'XXL': 2},
            },
            {
                'name': 'System Error Tee',
                'description': 'Glitched typography. Corrupted data aesthetic. 100% Egyptian cotton. Oversized unisex fit.',
                'price': 820,
                'category': 'tees',
                'is_featured': False,
                'stock': {'XS': 4, 'S': 9, 'M': 16, 'L': 11, 'XL': 6, 'XXL': 3},
            },
            {
                'name': 'FREKS Jungle Hoodie',
                'description': 'The Jungle System in hoodie form. 400gsm heavyweight fleece. Boxy oversized fit, kangaroo pocket, embroidered FREKS on chest.',
                'price': 1350,
                'category': 'hoodies',
                'is_featured': True,
                'stock': {'XS': 2, 'S': 5, 'M': 10, 'L': 8, 'XL': 4, 'XXL': 2},
            },
        ]

        for p_data in products_data:
            if not Product.query.filter_by(name=p_data['name']).first():
                cat = cats.get(p_data['category'])
                product = Product(
                    name=p_data['name'],
                    description=p_data['description'],
                    price=p_data['price'],
                    category_id=cat.id if cat else None,
                    is_featured=p_data.get('is_featured', False),
                    is_active=True,
                )
                db.session.add(product)
                db.session.flush()

                for size in sizes:
                    stock_count = p_data['stock'].get(size, 0)
                    variant = ProductVariant(
                        product_id=product.id,
                        size=size,
                        stock=stock_count
                    )
                    db.session.add(variant)

                print(f'✓ Product: {p_data["name"]}')
            else:
                print(f'· Product already exists: {p_data["name"]}')

        db.session.commit()
        print('\n✅ FREKS database seeded successfully!')
        print('\nAdmin login:')
        print('✓ Admin created — username: freks_admin  password: Freks@2025!')
        print('\nDemo user login:')
        print('✓ Demo user created — username: jungle_user  password: Demo@2025!')

if __name__ == '__main__':
    seed()
