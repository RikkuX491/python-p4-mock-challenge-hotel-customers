#!/usr/bin/env python3

import ipdb

from models import db, Hotel, HotelCustomer, Customer
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class AllHotels(Resource):

    def get(self):
        hotels = Hotel.query.all()
        response_body = [hotel.to_dict(rules=('-hotel_customers',)) for hotel in hotels]
        return make_response(response_body, 200)

api.add_resource(AllHotels, "/hotels")

class HotelById(Resource):

    def get(self, id):
        hotel = Hotel.query.filter(Hotel.id == id).first()

        if hotel:
            # response_body = {
            #     "id": hotel.id,
            #     "name": hotel.name
            # }
            # hotel_customers_list = []
            # for hc in hotel.hotel_customers:
            #     hotel_customers_list.append({
            #         "id": hc.id,
            #         "rating": hc.rating,
            #         "hotel_id": hc.hotel_id,
            #         "customer_id": hc.customer_id,
            #         "customer": {
            #             "id": hc.customer.id,
            #             "first_name": hc.customer.first_name,
            #             "last_name": hc.customer.last_name
            #         }
            #     })
            # response_body['hotel_customers'] = hotel_customers_list

            response_body = hotel.to_dict(rules=('-hotel_customers.hotel', '-hotel_customers.customer.hotel_customers'))

            return make_response(response_body, 200)
        else:
            response_body = {
                "error": "Hotel not found"
            }
            return make_response(response_body, 404)
        
    def delete(self, id):
        hotel = Hotel.query.filter(Hotel.id == id).first()

        if hotel:
            db.session.delete(hotel)
            db.session.commit()
            response_body = {}
            return make_response(response_body, 204)
        else:
            response_body = {
                "error": "Hotel not found"
            }
            return make_response(response_body, 404)

api.add_resource(HotelById, '/hotels/<int:id>')

class AllCustomers(Resource):

    def get(self):
        customers = Customer.query.all()

        response_body = [customer.to_dict(rules=('-hotel_customers',)) for customer in customers]

        # response_body = [customer.to_dict(only=('id', 'first_name', 'last_name')) for customer in customers]

        # response_body = []
        # for customer in customers:
        #     customer_dictionary = {
        #         "id": customer.id,
        #         "first_name": customer.first_name,
        #         "last_name": customer.last_name
        #     }
        #     response_body.append(customer_dictionary)

        return make_response(response_body, 200)

api.add_resource(AllCustomers, '/customers')

class AllHotelCustomers(Resource):

    def post(self):
        try:
            new_hotel_customer = HotelCustomer(rating=request.json.get('rating'), hotel_id=request.json.get('hotel_id'), customer_id=request.json.get('customer_id'))
            db.session.add(new_hotel_customer)
            db.session.commit()
            response_body = new_hotel_customer.to_dict(rules=('-hotel.hotel_customers', '-customer.hotel_customers'))

            # response_body = {
            #     "id": new_hotel_customer.id,
            #     "rating": new_hotel_customer.rating,
            #     "hotel_id": new_hotel_customer.hotel_id,
            #     "customer_id": new_hotel_customer.customer_id,
            #     "hotel": {
            #         "id": new_hotel_customer.hotel.id,
            #         "name": new_hotel_customer.hotel.name
            #     },
            #     "customer": {
            #         "id": new_hotel_customer.customer.id,
            #         "first_name": new_hotel_customer.customer.first_name,
            #         "last_name": new_hotel_customer.customer.last_name
            #     }
            # }

            return make_response(response_body, 201)
        except:
            response_body = {
                "errors": ["validation errors"]
            }
            return make_response(response_body, 400)

api.add_resource(AllHotelCustomers, '/hotel_customers')

@app.route('/')
def index():
    return '<h1>Mock Code challenge</h1>'


if __name__ == '__main__':
    app.run(port=5555, debug=True)