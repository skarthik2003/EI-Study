from abc import ABC, abstractmethod
from copy import deepcopy

# Product Prototype
class Product(ABC):
    def __init__(self, name, price, available=True):
        self.name = name
        self.price = price
        self.available = available

    @abstractmethod
    def clone(self):
        pass

# Concrete Product
class ConcreteProduct(Product):
    def clone(self):
        return deepcopy(self)

# Discount Strategy
class DiscountStrategy(ABC):
    @abstractmethod
    def apply_discount(self, total):
        pass

# Concrete Discount Strategies
class PercentageOffStrategy(DiscountStrategy):
    def __init__(self, percentage):
        self.percentage = percentage

    def apply_discount(self, total):
        return total * (1 - self.percentage / 100)

class BuyOneGetOneFreeStrategy(DiscountStrategy):
    def apply_discount(self, total):
        return total

# Cart
class Cart:
    def __init__(self):
        self.items = []

    def add_item(self, product, quantity=1):
        for _ in range(quantity):
            self.items.append(product.clone())

    def update_quantity(self, product_name, new_quantity):
        for item in self.items:
            if item.name == product_name:
                item.quantity = new_quantity

    def remove_item(self, product_name):
        self.items = [item for item in self.items if item.name != product_name]

    def view_cart(self):
        item_counts = {}
        for item in self.items:
            item_counts[item.name] = item_counts.get(item.name, 0) + 1

        cart_summary = ", ".join([f"{count} {name}" for name, count in item_counts.items()])
        print(f"You have {cart_summary} in your cart.")

    def calculate_total(self, discount_strategy=None):
        total = sum(item.price for item in self.items)
        if discount_strategy:
            total = discount_strategy.apply_discount(total)
        return total

# Example Usage
product1 = ConcreteProduct("Laptop", 1000)
product2 = ConcreteProduct("Headphones", 50)

cart = Cart()
cart.add_item(product1)
cart.add_item(product2)

cart.view_cart()

cart.update_quantity("Laptop", 2)

cart.view_cart()

cart.remove_item("Headphones")

cart.view_cart()

total_bill = cart.calculate_total(PercentageOffStrategy(10))
print(f"Your total bill is ${total_bill}.")