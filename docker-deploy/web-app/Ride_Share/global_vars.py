# Ride_Share/global
# Global Variables

# MAX_INIT_RIDE_CAPACITY = 4  # 5 total cap
MAX_RIDE_CAPACITY = 20  # 7 total cap
VEHICLE_TYPE_ = (
        ("con", 'Convertible'),
        ("cou", 'Coupe'),
        ("sed", 'Sedan'),
        ("suv", 'SUV'),
        ("tru", 'Truck'),
    )
CHOCICE_FIELD_VEHICLE_TYPE_ = (
        ("", '----'),
        ("con", 'Convertible'),
        ("cou", 'Coupe'),
        ("sed", 'Sedan'),
        ("suv", 'SUV'),
        ("tru", 'Truck'),
    )
RIDE_STATUS_ = (
    ('opn', 'Open'),
    ('con', 'Confirmed'),
    ('cop', 'Completed'),
)
REVERSE_RIDE_STATUS_ = {'opn':'Open', 'con': 'Confirmed', 'cop': 'Completed'}
# VT2CAP = {'con': 5, 'cou': 4, 'sed': 4, 'suv': 7, 'tru': 4} 