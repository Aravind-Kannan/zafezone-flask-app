from flask import Flask, request, jsonify
from flask_restx import fields, Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
api = Api(
    app,
    version="1.0",
    title="LocMVC API",
    description="A simple LocMVC API",
)
ns_loc = api.namespace("locs", description="Locational data operations")
ns_item = api.namespace("loc", description="Specific locational data operations")

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = os.environ.get('DB_URI', None)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "secret string"

db = SQLAlchemy(app)

model = api.model(
    "Loc",
    {
        "phone_number": fields.String(required=True),
        "longitude": fields.String(required=True),
        "latitude": fields.String(required=True),
        "emergency": fields.Boolean(required=True),
        "sent_at": fields.DateTime(required=True),
    },
)

parser = reqparse.RequestParser()
parser.add_argument("phone_number", type=str)
parser.add_argument("longitude", type=str)
parser.add_argument("latitude", type=str)
parser.add_argument("emergency", type=bool)
parser.add_argument("sent_at")


# Loc Model
class Loc(db.Model):
    # TODO: Create as uuid
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String, nullable=False)
    longitude = db.Column(db.String, nullable=False)
    latitude = db.Column(db.String, nullable=False)
    emergency = db.Column(db.Boolean, nullable=False)
    sent_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, phone_number, longitude, latitude, emergency, sent_at):
        self.phone_number = phone_number
        self.longitude = longitude
        self.latitude = latitude
        self.emergency = emergency
        self.sent_at = sent_at


@ns_loc.route("")
class LocList(Resource):
    @ns_loc.doc("list_loc")
    def get(self):
        all_loc = Loc.query.all()
        response = [
            {
                "id": loc.id,
                "phone_number": str(loc.phone_number),
                "longitude": str(loc.longitude),
                "latitude": str(loc.latitude),
                "emergency": loc.emergency,
                "sent_at": str(loc.sent_at),
            }
            for loc in all_loc
        ]

        return jsonify(response)

    @ns_loc.doc("create_loc")
    @ns_loc.expect(model)
    def post(self):
        print(request.get_json(force=True))
        args = parser.parse_args()
        entry = Loc(
            args["phone_number"],
            args["longitude"],
            args["latitude"],
            bool(args["emergency"]),
            args["sent_at"],
        )
        db.session.add(entry)
        db.session.commit()

        return "OK!", 201


@ns_item.route("/<phone_number>")
class LocSpecific(Resource):
    @ns_loc.doc("list_specific_loc")
    def get(self, phone_number):
        all_loc = Loc.query.filter_by(phone_number=phone_number).all()
        response = [
            {
                "id": loc.id,
                "phone_number": str(loc.phone_number),
                "longitude": str(loc.longitude),
                "latitude": str(loc.latitude),
                "emergency": loc.emergency,
                "sent_at": str(loc.sent_at),
            }
            for loc in all_loc
        ]

        return jsonify(response)


if __name__ == "__main__":
    app.run()
