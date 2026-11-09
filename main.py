import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request, jsonify

app = Flask(__name__)

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# Home route
@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to NBKRIST Nexus Bus Reservation System"
    })

# Book a bus seat
@app.route("/book-seat", methods=["POST"])
def book_seat():
    data = request.get_json()

    student_name = data.get("student_name")
    bus_number = data.get("bus_number")
    seat_number = data.get("seat_number")

    if not all([student_name, bus_number, seat_number]):
        return jsonify({"error": "Missing booking details"}), 400

    seat_ref = db.collection("reservations").document(
        f"{bus_number}_{seat_number}"
    )

    transaction = db.transaction()

    @firestore.transactional
    def reserve(transaction):
        seat = seat_ref.get(transaction=transaction)

        if seat.exists:
            return False

        transaction.set(seat_ref, {
            "student_name": student_name,
            "bus_number": bus_number,
            "seat_number": seat_number,
            "status": "Booked"
        })

        return True

    if reserve(transaction):
        return jsonify({"message": "Seat booked successfully"}), 201

    return jsonify({"message": "Seat is already booked"}), 409

# View all reservations
@app.route("/reservations", methods=["GET"])
def get_reservations():
    reservations = db.collection("reservations").stream()

    result = [
        reservation.to_dict()
        for reservation in reservations
    ]

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
