import yaml
from django.core.management.base import BaseCommand
from ...models import Category, Product, ProductParameter

class Command(BaseCommand):
    help = 'Импорт товаров из YAML-файла'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Путь к YAML-файлу')

    def handle(self, *args, **options):
        file_path = options['file_path']

        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)

        self.import_categories(data.get('categories', []))
        self.import_products(data.get('goods', []))

        self.stdout.write(
            self.style.SUCCESS('Импорт успешно завершён!')
        )

    def import_categories(self, categories_data):
        """Импорт категорий"""
        for cat_data in categories_data:
            Category.objects.update_or_create(
                id=cat_data['id'],
                defaults={'name': cat_data['name']}
            )
        self.stdout.write(f'Импортировано {len(categories_data)} категорий')

    def import_products(self, products_data):
        """Импорт товаров и их параметров"""
        imported_count = 0

        for prod_data in products_data:
            # Создаём/обновляем товар
            category = Category.objects.get(id=prod_data['category'])
            product, created = Product.objects.update_or_create(
                id=prod_data['id'],
                defaults={
                    'category': category,
                    'model': prod_data.get('model', ''),
                    'name': prod_data['name'],
                    'price': prod_data['price'],
                    'price_rrc': prod_data.get('price_rrc'),
                    'quantity': prod_data['quantity'],
                    'shop': 'Связной'
                }
            )

            # Обрабатываем параметры товара
            self.import_product_parameters(product, prod_data.get('parameters', {}))

            imported_count += 1

        self.stdout.write(f'Импортировано {imported_count} товаров')

    def import_product_parameters(self, product, parameters_data):
        """Импорт характеристик товара"""
        # Удаляем старые параметры для этого товара (чтобы обновить при повторном импорте)
        product.parameters.all().delete()

        for key, value in parameters_data.items():
            ProductParameter.objects.create(
                product=product,
                key=key,
                value=str(value)  # преобразуем всё в строку для универсальности
            )