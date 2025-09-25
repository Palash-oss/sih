import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise Exception("MONGO_URI not found in environment variables.")

# Specify the database name you want to use (e.g., 'healthcare')
client = MongoClient(MONGO_URI)
db = client['healthcare']

doctors = [
    {"name": "Dr. Asha Singh", "specialty": "General Physician", "location": "Village Clinic", "phone": "9876543210"},
    {"name": "Dr. Ramesh Kumar", "specialty": "Pediatrician", "location": "District Hospital", "phone": "9123456780"},
    {"name": "Dr. Priya Patel", "specialty": "Gynecologist", "location": "Community Health Center", "phone": "9988776655"}
]

if db.doctors.count_documents({}) == 0:
    db.doctors.insert_many(doctors)
    print("Sample doctors seeded.")
else:
    print("Doctors already exist.")