import sys
import os

# Add the project path to sys.path
project_root = "/Users/vishnu/Documents/Tracxn/Discovery/Ghost/Ghost P1"
sys.path.append(project_root)

from utils.scraper import is_parked

def test_parking_detection():
    # Normal content
    text_normal = "Welcome to our company. We provide high-quality services and products to our customers across the globe. Contact us for more info."
    print(f"Normal: {is_parked(text_normal)}")
    
    # Parked content (high link density)
    text_parked = "http://example.com http://buy.com http://sale.com http://parked.com http://domain.com http://offer.com http://contact.com"
    print(f"Parked (High Links): {is_parked(text_parked)}")
    
    # Keyword parked
    text_keyword = "This domain is for sale by its owner. Make an offer today."
    print(f"Parked (Keywords): {is_parked(text_keyword)}")

if __name__ == "__main__":
    test_parking_detection()
