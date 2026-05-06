import json
import requests
import vegetable_data
import herb_data
import flower_data

# --- CONFIGURATION & PERSISTENCE ---
GARDEN_FILE = "my_garden.json"

def load_garden():
    try:
        with open(GARDEN_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_garden(garden_list):
    with open(GARDEN_FILE, "w") as f:
        json.dump(garden_list, f, indent=4)

# --- WEATHER INTEGRATION ---
def get_weather():
    # Defaulting to Paducah, KY coordinates
    url = "https://api.open-meteo.com/v1/forecast?latitude=37.0834&longitude=-88.6001&current_weather=true&temperature_unit=fahrenheit"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        current = data["current_weather"]
        return f"{current['temperature']}°F | Wind: {current['windspeed']} mph"
    except:
        return "Weather currently unavailable."

# --- UI COMPONENTS ---
def display_header(title):
    weather = get_weather()
    print("\n" + "="*60)
    print(f" {title.upper()} ".center(60, " "))
    print(f" Local Weather: {weather} ".center(60, "-"))
    print("="*60)

def add_plant_workflow(data_module, category_name):
    display_header(f"Add {category_name}")
    for i, plant in enumerate(data_module.plants, 1):
        print(f"{i}. {plant['name']} ({plant['cultivar']}) - {plant['type']}")
    
    choice = input(f"\nEnter number to add to your garden (or 'b' for back): ")
    if choice.isdigit() and 1 <= int(choice) <= len(data_module.plants):
        selected = data_module.plants[int(choice)-1]
        garden = load_garden()
        garden.append(selected)
        save_garden(garden)
        print(f"\nSUCCESS: Added {selected['cultivar']} {selected['name']} to your garden!")
    elif choice.lower() != 'b':
        print("\nInvalid selection.")

def view_my_garden():
    display_header("In My Garden")
    garden = load_garden()
    if not garden:
        print("Your garden is currently empty. Go to a tab to add plants!")
    else:
        print(f"{'PLANT':<15} | {'CULTIVAR':<20} | {'ORIGIN/USE':<15}")
        print("-" * 60)
        for item in garden:
            # Flexible display logic for different data formats
            extra = item.get('origin') or item.get('primary_use') or item.get('flower_type')
            print(f"{item['name']:<15} | {item['cultivar']:<20} | {extra:<15}")
    input("\nPress Enter to return...")

# --- MAIN APP LOOP ---
def main():
    while True:
        display_header("Liz's Homestead Planner")
        print("1. [TAB] Add Vegetables")
        print("2. [TAB] Add Herbs")
        print("3. [TAB] Add Flowers")
        print("4. [VIEW] In My Garden")
        print("5. Exit")
        
        choice = input("\nSelect an option: ")

        if choice == '1':
            add_plant_workflow(vegetable_data, "Vegetables")
        elif choice == '2':
            add_plant_workflow(herb_data, "Herbs")
        elif choice == '3':
            add_plant_workflow(flower_data, "Flowers")
        elif choice == '4':
            view_my_garden()
        elif choice == '5':
            print("Closing App. Happy Gardening!")
            break

if __name__ == "__main__":
    main()
