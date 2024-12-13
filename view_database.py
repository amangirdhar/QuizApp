import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('C:/PROJECTS/Quiz App/quizapp-7bc35-firebase-adminsdk-4denh-cb7f1c9dab.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

def view_collection(collection_name):
    try:
        collection_ref = db.collection(collection_name)
        docs = collection_ref.stream()
        
        for doc in docs:
            print(f'Document ID: {doc.id}')
            print(f'Document Data: {doc.to_dict()}')
            print('---')
    
    except Exception as e:
        print(f'Error: {e}')

def view_leaderboard(collection_name, topic_name=None):
    try:
        collection_ref = db.collection(collection_name)
        
        if topic_name:
            docs = collection_ref.where("responses", "array_contains_any", [{"topic": topic_name}]).stream()
        else:
            docs = collection_ref.stream()

        leaderboard = []

        for doc in docs:
            user_data = doc.to_dict()
            user_name = user_data.get("name", "Unknown")
            user_email = user_data.get("email", "Unknown")
            user_score = user_data.get("score", 0)
            
            if topic_name:
                topic_score = sum(
                    res['score'] for res in user_data.get("responses", []) if res.get("topic") == topic_name
                )
                leaderboard.append({
                    "name": user_name,
                    "email": user_email,
                    "score": topic_score
                })
            else:
                leaderboard.append({
                    "name": user_name,
                    "email": user_email,
                    "score": user_score
                })

        leaderboard = sorted(leaderboard, key=lambda x: x["score"], reverse=True)
        for entry in leaderboard:
            print(f"Name: {entry['name']}, Email: {entry['email']}, Score: {entry['score']}")
            print('---')

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    view_collection('user_responses')
    #view_leaderboard('user_responses', 'Math')

