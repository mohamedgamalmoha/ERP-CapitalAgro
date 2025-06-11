from random import choice

import faker
import factory

from inventory.enums import Unit, Status, PackageType
from inventory.models import Supplier, Category, RawMaterial, ReadyMaterial, PackagedMaterial


fake = factory.Faker('faker', locale='en_US')


_FOOD_CATEGORIES = {
    "proteins": [
        "chicken breast", "chicken thighs", "ground beef", "beef tenderloin",
        "pork chops", "salmon", "tuna", "shrimp", "eggs", "tofu",
        "lamb", "duck", "cod", "turkey", "bacon"
    ],
    "vegetables": [
        "onions", "garlic", "tomatoes", "bell peppers", "carrots", "celery",
        "potatoes", "broccoli", "spinach", "lettuce", "mushrooms", "zucchini",
        "eggplant", "asparagus", "corn", "peas", "cabbage", "cauliflower"
    ],
    "fruits": [
        "lemons", "limes", "oranges", "apples", "bananas", "berries",
        "avocados", "grapes", "pineapple", "mango", "strawberries",
        "cherries", "peaches", "pears"
    ],
    "grains_starches": [
        "rice", "pasta", "bread", "flour", "quinoa", "oats",
        "barley", "couscous", "noodles", "tortillas", "potatoes"
    ],
    "dairy": [
        "milk", "butter", "cheese", "cream", "yogurt", "sour cream",
        "mozzarella", "parmesan", "cheddar", "heavy cream"
    ],
    "herbs_spices": [
        "basil", "oregano", "thyme", "rosemary", "parsley", "cilantro",
        "salt", "black pepper", "paprika", "cumin", "garlic powder",
        "onion powder", "bay leaves", "sage", "dill"
    ],
    "oils_fats": [
        "olive oil", "vegetable oil", "canola oil", "coconut oil",
        "sesame oil", "butter", "lard", "cooking spray"
    ],
    "condiments_sauces": [
        "soy sauce", "hot sauce", "ketchup", "mustard", "mayonnaise",
        "vinegar", "worcestershire sauce", "bbq sauce", "teriyaki sauce",
        "ranch dressing", "balsamic vinegar"
    ],
    "beverages": [
        "water", "coffee", "tea", "wine", "beer", "soft drinks",
        "juices", "milk", "sparkling water"
    ],
    "baking_ingredients": [
        "flour", "sugar", "baking powder", "baking soda", "vanilla extract",
        "cocoa powder", "chocolate chips", "yeast", "honey", "maple syrup"
    ],
    "frozen_items": [
        "frozen vegetables", "frozen fruits", "ice cream", "frozen fish",
        "frozen chicken", "frozen fries", "ice"
    ],
    "canned_preserved": [
        "canned tomatoes", "canned beans", "canned corn", "pickles",
        "olives", "capers", "tomato paste", "coconut milk", "broth"
    ]
}


_FOOD_WORKSTATION = {
    "butcher_station": {
        "description": "Meat and protein preparation area",
        "equipment": [
            "butcher block", "meat slicer", "bone saw", "cleaver",
            "boning knife", "fillet knife", "meat grinder", "tenderizer",
            "cutting boards (color-coded)", "steel mesh gloves", "meat hooks",
            "vacuum sealer", "portion scale", "bandsaw"
        ],
        "materials_processed": [
            "beef", "pork", "lamb", "chicken", "turkey", "duck",
            "fish", "seafood", "game meats"
        ]
    },
    "garde_manger": {
        "description": "Cold food preparation station (salads, appetizers, cold dishes)",
        "equipment": [
            "refrigerated prep table", "mandoline slicer", "vegetable peeler",
            "paring knives", "salad spinner", "mixing bowls", "tongs",
            "portion cups", "squeeze bottles", "microplane grater",
            "julienne peeler", "herb scissors"
        ],
        "materials_processed": [
            "lettuce", "vegetables", "fruits", "herbs", "cheese",
            "cold cuts", "nuts", "oils", "vinegars", "condiments"
        ]
    },
    "prep_station": {
        "description": "General food preparation and vegetable prep",
        "equipment": [
            "food processor", "vegetable chopper", "prep sinks",
            "cutting boards", "chef knives", "utility knives", "peelers",
            "graters", "colanders", "mixing bowls", "measuring cups",
            "measuring spoons", "can opener", "kitchen shears"
        ],
        "materials_processed": [
            "vegetables", "fruits", "herbs", "garlic", "onions",
            "canned goods", "dried ingredients", "spices"
        ]
    },
    "hot_line": {
        "description": "Main cooking station for hot dishes",
        "equipment": [
            "gas range", "electric range", "griddle", "char-broiler",
            "deep fryer", "salamander", "heat lamps", "sauté pans",
            "stock pots", "sauce pans", "sheet pans", "tongs",
            "spatulas", "ladles", "thermometers"
        ],
        "materials_processed": [
            "proteins", "vegetables", "pasta", "rice", "oils",
            "sauces", "stocks", "spices", "herbs"
        ]
    },
    "grill_station": {
        "description": "Grilling and broiling station",
        "equipment": [
            "char-grill", "flat-top grill", "salamander broiler",
            "grill brushes", "grill tongs", "grill spatula",
            "grill thermometer", "grill press", "chimney starter"
        ],
        "materials_processed": [
            "steaks", "chicken", "fish", "vegetables", "burgers",
            "sausages", "marinades", "oils"
        ]
    },
    "fry_station": {
        "description": "Deep frying operations",
        "equipment": [
            "deep fryer", "fry baskets", "oil filter", "fry thermometer",
            "spider strainer", "paper towels", "holding bins",
            "oil disposal system", "fire suppression system"
        ],
        "materials_processed": [
            "potatoes", "chicken", "fish", "vegetables", "breading",
            "flour", "oils", "frozen items"
        ]
    },
    "saute_station": {
        "description": "Quick cooking with high heat",
        "equipment": [
            "sauté pans", "woks", "burner ranges", "tongs", "spatulas",
            "wooden spoons", "whisks", "sauce pans", "strainers"
        ],
        "materials_processed": [
            "vegetables", "proteins", "herbs", "garlic", "oils",
            "wines", "stocks", "sauces", "pasta"
        ]
    },
    "sauce_station": {
        "description": "Sauce and stock preparation",
        "equipment": [
            "stock pots", "sauce pans", "immersion blender", "whisk",
            "fine mesh strainer", "cheesecloth", "ladles", "thermometer",
            "reduction pans", "double boiler"
        ],
        "materials_processed": [
            "bones", "vegetables", "herbs", "wines", "cream",
            "butter", "stocks", "tomatoes", "spices"
        ]
    },
    "pastry_station": {
        "description": "Baking and pastry preparation",
        "equipment": [
            "stand mixer", "convection oven", "proof box", "dough sheeter",
            "rolling pins", "pastry brushes", "piping bags", "tips",
            "cake pans", "muffin tins", "cooling racks", "bench scraper",
            "digital scale", "measuring tools"
        ],
        "materials_processed": [
            "flour", "sugar", "eggs", "butter", "cream", "chocolate",
            "vanilla", "baking powder", "yeast", "fruits", "nuts"
        ]
    },
    "dishwashing_station": {
        "description": "Cleaning and sanitizing area",
        "equipment": [
            "dish machine", "pre-rinse sprayer", "dish racks",
            "bus tubs", "scrub brushes", "sanitizer dispenser",
            "drying racks", "pot washing sink", "glass washer"
        ],
        "materials_processed": [
            "dishes", "glassware", "utensils", "pots", "pans",
            "cleaning chemicals", "sanitizers"
        ]
    },
    "receiving_station": {
        "description": "Incoming inventory and inspection",
        "equipment": [
            "receiving scale", "thermometer", "clipboard", "hand truck",
            "pallet jack", "inspection table", "storage containers",
            "labels", "date gun", "first-aid kit"
        ],
        "materials_processed": [
            "all incoming raw materials", "packaged goods",
            "frozen items", "refrigerated items", "dry goods"
        ]
    },
    "storage_areas": {
        "description": "Food storage and inventory management",
        "equipment": [
            "walk-in cooler", "walk-in freezer", "dry storage shelving",
            "food containers", "labels", "thermometers", "FIFO rotation system",
            "inventory sheets", "hand scanner", "step ladder"
        ],
        "materials_processed": [
            "all raw materials", "prepared foods", "leftovers",
            "dry goods", "canned goods", "frozen items"
        ]
    }
}


_STORAGE_LOCATIONS = [
    "walk-in cooler",
    "walk-in freezer",
    "dry storage room",
    "refrigerated shelf",
    "freezer shelf",
    "dry goods shelf",
    "pantry",
    "bulk storage bin",
    "cold storage unit"
]


class FoodProvider(faker.providers.BaseProvider):

    def food_category(self) -> str:
        categories = list(_FOOD_CATEGORIES.keys())
        return choice(categories)

    def food_material(self, category: str = None) -> str:
        if category is None:
            category = self.food_category()
        if category not in _FOOD_CATEGORIES:
            raise ValueError(
                f"Invalid food category: {category}"
            )
        return choice(_FOOD_CATEGORIES[category])

    def food_workstation(self, material: str = None) -> str:
        if material is None:
            material = self.food_material()
        for workstation, details in _FOOD_WORKSTATION.items():
            if material in details["materials_processed"]:
                return workstation
        raise ValueError(
            f"No workstation found for material: {material}"
        )

    def food_workstation_description(self, workstation: str = None) -> str:
        if workstation is None:
            workstation = self.food_workstation()
        if workstation not in _FOOD_WORKSTATION:
            raise ValueError(
                f"Invalid food workstation: {workstation}"
            )
        return _FOOD_WORKSTATION[workstation]["description"]

    def food_workstation_equipment(self, workstation: str = None) -> list:
        if workstation is None:
            workstation = self.food_workstation()
        if workstation not in _FOOD_WORKSTATION:
            raise ValueError(
                f"Invalid food workstation: {workstation}"
            )
        return _FOOD_WORKSTATION[workstation]["equipment"]

    def food_workstation_materials(self, workstation: str = None) -> list:
        if workstation is None:
            workstation = self.food_workstation()
        if workstation not in _FOOD_WORKSTATION:
            raise ValueError(
                f"Invalid food workstation: {workstation}"
            )
        return _FOOD_WORKSTATION[workstation]["materials_processed"]

    def food_storage_location(self) -> str:
        return choice(_STORAGE_LOCATIONS)

    def food_storage_temperature(self) -> int:
        return choice([0, 4, 20])  # Typical storage temperatures in Celsius


fake.add_provider(FoodProvider)


class SupplierFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('company')
    contact_info = factory.Faker('text', max_nb_chars=100)

    class Meta:
        model = Supplier
        django_get_or_create = ('name',)


class CategoryFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('food_category')
    description = factory.Faker('text', max_nb_chars=200)
    requires_temperature_control = factory.Faker('boolean')
    max_processing_time_hours = factory.Faker('random_int', min=1, max=48, step=1)

    class Meta:
        model = Category
        django_get_or_create = ('name',)


class RawMaterialFactory(factory.django.DjangoModelFactory):
    supplier = factory.SubFactory(SupplierFactory)
    category = factory.SubFactory(CategoryFactory)

    material_name = factory.LazyAttribute(
        lambda obj: factory.Faker('food_material', category=obj.category.name)
    )
    initial_quantity = factory.Faker('random_int', min=1, max=1000, step=1)
    current_quantity = factory.SelfAttribute('initial_quantity')
    unit = factory.Faker('random_element', elements=Unit.choices)

    production_date = factory.Faker('date')
    expiration_date = factory.Faker('date_between', start_date='today', end_date='+2y')

    inventory_coordinator = factory.SubFactory('accounts.factories.InventoryCoordinatorUserFactory')
    quality_score = factory.Faker('random_int', min=1, max=100, step=1)
    status = factory.Faker('random_element', elements=Status.choices)
    received_date = factory.Faker('date_time_this_year', before_now=False, after_now=True)
    note = factory.Faker('text', max_nb_chars=200)

    storage_location = factory.Faker('food_storage_location')
    storage_temperature = factory.Faker('food_storage_temperature')

    class Meta:
        model = RawMaterial
        django_get_or_create = ('material_name',)


class ReadyMaterialFactory(factory.django.DjangoModelFactory):
    workstation_raw_material = factory.SubFactory('workstation.factories.WorkstationPreparedMaterialFactory')
    inventory_coordinator = factory.SubFactory('accounts.factories.InventoryCoordinatorUserFactory')
    quality_score = factory.Faker('random_int', min=1, max=10, step=1)
    quantity = factory.Faker('random_int', min=1, max=1000, step=1)
    unit = factory.Faker('random_element', elements=Unit.choices)
    note = factory.Faker('text', max_nb_chars=200)

    storage_location = factory.Faker('food_storage_location')
    storage_temperature= factory.Faker('food_storage_temperature')

    transporter = factory.SubFactory('accounts.factories.TransporterUserFactory')
    delivery_date = factory.Faker('date_time_this_year', before_now=False, after_now=True)

    class Meta:
        model = ReadyMaterial
        django_get_or_create = ('workstation_raw_material',)


class PackagedMaterialFactory(factory.django.DjangoModelFactory):
    ready_material = factory.SubFactory(ReadyMaterialFactory)

    worker = factory.SubFactory('accounts.factories.WorkerUserFactory')
    quantity = factory.Faker('random_int', min=1, max=1000, step=1)
    unit = factory.Faker('random_element', elements=Unit.choices)
    package_date = factory.Faker('date_time_this_year', before_now=False, after_now=True)
    package_type = factory.Faker('random_element', elements=PackageType.choices)
    note = factory.Faker('text', max_nb_chars=200)

    storage_location = factory.Faker('food_storage_location')
    storage_temperature = factory.Faker('food_storage_temperature')

    class Meta:
        model = PackagedMaterial
        django_get_or_create = ('ready_material',)
