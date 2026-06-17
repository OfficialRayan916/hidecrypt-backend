from services.db import users_collection

test_user = {
    "username": "te......1234...ser",
    "email": "test@example.com"
    
}

result = users_collection.insert_one(test_user)

print("Inserted ID:", result.inserted_id)