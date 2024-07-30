import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

cred = credentials.Certificate(os.getenv(f'FIREBASE_CREDENTIALS'))
firebase_admin.initialize_app(cred)

db = firestore.client()


def is_registered(user_id):
    user_profile = db.collection('users').document(user_id).get()
    return user_profile.exists
