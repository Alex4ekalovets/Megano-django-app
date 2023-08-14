import json
import shutil
from datetime import datetime
from pathlib import Path, PurePath

from api.models import Category, Product, ProductImage, Specification
from django.core.management import BaseCommand

from megano.settings import MEDIA_ROOT


class Command(BaseCommand):
    """
    Creates products
    """

    def handle(self, *args, **options):
        self.stdout.write("Create products")
        path = Path("/Users/MacAlex/WorkFolder/Python/Projects/MV-parser")
        data = PurePath(path, "laptops.json")
        with open(data, "r") as file:
            items = json.load(file)

        for item in items:
            product, created = Product.objects.get_or_create(
                category=Category.objects.get(title="Laptops"),
                price=item["price"],
                count=item["count"],
                date=datetime.fromtimestamp(item["date"]),
                title=item["title"],
                description=item["description"],
                fullDescription=item["fullDescription"],
                freeDelivery=item["freeDelivery"],
            )
            product_images = []
            for image in item["images"]:
                source_path = Path(PurePath(path, image["src"]))
                item_image_path = "products/product_{pk}/images/".format(
                    pk=product.pk,
                    filename=image["src"],
                )
                image_path = f"{item_image_path}/{image['src']}"
                destination_path = Path(PurePath(MEDIA_ROOT, item_image_path))
                destination_path.mkdir(parents=True, exist_ok=True)
                product_images.append(
                    ProductImage(product=product, src=image_path, alt=image["alt"])
                )
                shutil.copy(source_path, destination_path)
            ProductImage.objects.bulk_create(product_images)
            Specification.objects.bulk_create(
                [
                    Specification(
                        product=product,
                        name=parameter["name"],
                        value=parameter["value"],
                    )
                    for parameter in item["specifications"]
                ]
            )
            self.stdout.write(f"Created product {product.title}")

        self.stdout.write(self.style.SUCCESS("Products created"))
