from pymongo import MongoClient
from dotenv import load_dotenv
import os

class UserService:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        self.client = MongoClient(os.getenv('MONGODB_URL'))
        self.db = self.client[os.getenv('DB_NAME')]
        self.collection = self.db[os.getenv('USER_COLLECTION')]

    def register_user(self, username, google_id, email):
        """
        Register a new user using Google Sign-In.

        Parameters:
        - username (str): The username of the user.
        - google_id (str): The Google user ID.
        - email (str): The email address of the user.

        Returns:
        - The object ID of the inserted user.
        """
        user_data = {'username': username, 'google_id': google_id, 'email': email}
        result = self.collection.insert_one(user_data)
        return result.inserted_id

    def find_user_by_google_id(self, google_id):
        """
        Find a user by their Google ID.

        Parameters:
        - google_id (str): The Google ID of the user to find.

        Returns:
        - A dictionary representing the user if found, otherwise None.
        """
        user = self.collection.find_one({'google_id': google_id})
        return user

    def verify_google_id(self, google_id):
        """
        Verify the Google ID for a user.

        Parameters:
        - google_id (str): The Google ID to verify.

        Returns:
        - True if the Google ID is correct, False otherwise.
        """
        user = self.find_user_by_google_id(google_id)
        return user is not None

# Example usage:
if __name__ == "__main__":
    # Initialize the UserService
    user_service = UserService()

    # Register a new user using Google Sign-In
    username = "testuser"
    google_id = "google_user_id"
    email = "testuser@example.com"
    user_id = user_service.register_user(username, google_id, email)
    print("Registered user with ID:", user_id)

    # Find a user by their Google ID
    found_user = user_service.find_user_by_google_id(google_id)
    print("Found user:", found_user)

    # Verify Google ID for the user
    verified = user_service.verify_google_id(google_id)
    print("Google ID verified:", verified)