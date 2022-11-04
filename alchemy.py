from crypt import methods
import json
from pdb import post_mortem
from sys import orig_argv
from flask import Flask, request, jsonify

from db import *
from users import Users
from organizations import Organizations

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://ian@localhost:5432/alchemy"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# conn = psycopg2.connect("dbname='usermgt' user='ian' host='localhost'")
# cursor = conn.cursor()

init_db(app,db)

def create_all():
  with app.app_context():
    print("Creating tables...")
    db.create_all()
    print("All done!")


@app.route('/org/add', methods=["POST"])
def org_add():
  post_data = request.json
  if not post_data:
    post_data = request.form
  name = post_data.get('name')
  phone = post_data.get('phone')
  city = post_data.get('city')
  state = post_data.get('state')
  active = post_data.get('active')

  add_org(name, phone, city, state, active)

  return jsonify("Org Created"), 200

def add_org(name, phone, city, state, active):
  new_org = Organizations(name, phone, city, state, active)

  db.session.add(new_org)
  db.session.commit()

@app.route('/orgs/get', methods=['GET'])
def get_all_active_orgs():
  orgs = db.session.query(Organizations).filter(Organizations.active == True).all()
  orgs_list = []

  for org in orgs:
    org = {
      'org_id': org.org_id,
      'name': org.name,
      'phone': org.phone,
      'city': org.city,
      'state': org.state,
      'active': org.active
    }

    orgs_list.append(org)
  return jsonify(orgs_list), 200

@app.route('/org/<org_id>', methods=['GET'])
def get_org_by_id(org_id):
  org_by_id = db.session.query(Organizations).filter(Organizations.org_id == org_id).one()

  if org_by_id:
    org = {
      'org_id': org_by_id.organization.org_id,
      'name': org_by_id.organization.name,
      'phone': org_by_id.organization.phone,
      'city': org_by_id.organization.city,
      'state': org_by_id.organization.state,
      'active': org_by_id.active
    }
  return jsonify(org), 200



@app.route('/org/activate/<org_id>')
def activate_org(org_id):
  org_data = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
  if org_data:
    org_data.active = True
    db.session.commit()
  return jsonify("Organization Activated"), 200

@app.route('/org/deactivate/<org_id>')
def deactivate_org(org_id):
  org_data = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
  if org_data:
    org_data.active = False
    db.session.commit()
  return jsonify("Organization Deactivated"), 200

@app.route('/org/delete/<org_id>')
def delete_org(org_id):
  delete_org = db.session.query(Organizations).filter(Organizations.org_id == org_id).delete()
  db.session.commit()
  return jsonify("Organization Deleted"), 200

@app.route('/org/update/<org_id>', methods=['POST', 'PUT'])
def org_update(org_id):
  org_to_update = (db.session.query(Organizations).filter(Organizations.org_id == org_id)).first()

  if not org_to_update:
    return jsonify("org with id not found", 404)

  post_data = request.json
  if not post_data:
    post_data = request.form

  if post_data.get('name'):
    org_to_update.name = post_data.get('name')
  if post_data.get('phone'):
    org_to_update.phone = post_data.get('phone')
  if post_data.get('city'):
    org_to_update.city = post_data.get('city')
  if post_data.get('state'):
    org_to_update.state = post_data.get('state')
  if post_data.get('active'):
    org_to_update.active = post_data.get('active')

  db.session.commit()

  return jsonify("Organization Updated"), 200 
# --------------------------------------------------------------------


@app.route('/user/add', methods=['POST'])
def user_add():
  post_data = request.json
  if not post_data:
    post_data = request.post
  
  first_name = post_data.get('first_name')
  last_name = post_data.get('last_name')
  email = post_data.get('email')
  phone = post_data.get('phone')
  city = post_data.get('city')
  state = post_data.get('state')
  org_id = post_data.get('org_id')
  active = post_data.get('active')

  add_user(first_name, last_name, email, phone, city, state, org_id, active)

  return jsonify("User Created"), 201

def add_user(first_name, last_name, email, phone, city, state, org_id, active):
  new_user = Users(first_name, last_name, email, phone, city, state, org_id, active)

  db.session.add(new_user)

  db.session.commit()


@app.route('/users/get', methods=['GET'])
def get_all_active_users():
  users = db.session.query(Users).filter(Users.active == True).all()
  users_list = []

  for user in users:
    user = {
      'user_id': user.user_id,
      'first_name': user.first_name,
      'last_name': user.last_name,
      'email': user.email,
      'phone': user.phone,
      'city': user.city,
      'state': user.state,
      'organization': {
        'org_id': user.organization.org_id,
        'name': user.organization.name,
        'phone': user.organization.phone,
        'city': user.organization.city,
        'state': user.organization.state,
      },
      'active': user.active
    }

    users_list.append(user)
  return jsonify(users_list), 200


@app.route('/user/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
  user_by_id = db.session.query(Users).filter(Users.user_id == user_id).one()

  if user_by_id:
    user = {
      'user_id': user_by_id.user_id,
      'first_name': user_by_id.first_name,
      'last_name': user_by_id.last_name,
      'email': user_by_id.email,
      'phone': user_by_id.phone,
      'city': user_by_id.city,
      'state': user_by_id.state,
      'organization': {
        'org_id': user_by_id.organization.org_id,
        'name': user_by_id.organization.name,
        'phone': user_by_id.organization.phone,
        'city': user_by_id.organization.city,
        'state': user_by_id.organization.state,
      },
      'active': user_by_id.active
    }
  return jsonify(user), 200

@app.route('/users/activate/<user_id>')
def activate_user(user_id):
  user_data = db.session.query(Users).filter(Users.user_id == user_id).first()
  if user_data:
    user_data.active = True
    db.session.commit()
    return jsonify("User Activated"), 200

@app.route('/users/deactivate/<user_id>')
def deactivate_user(user_id):
  user_data = db.session.query(Users).filter(Users.user_id == user_id).first()
  if user_data:
    user_data.active = False
    db.session.commit()
  return jsonify("User Deactivated"), 200

@app.route('/users/delete/<user_id>')
def delete_user(user_id):
  db.session.query(Users).filter(Users.user_id == user_id).delete()
  db.session.commit()
  return jsonify("User Deleted"), 200


@app.route('/users/update/<user_id>', methods=['POST', 'PUT'])
def user_update(user_id):
  user_to_update = (db.session.query(Users).filter(Users.user_id == user_id)).first()

  if not user_to_update:
    return jsonify("user with id not found", 404)

  post_data = request.json
  if not post_data:
    post_data = request.form
  
  if post_data.get('first_name'):
    user_to_update.first_name = post_data.get('first_name')
  if post_data.get('last_name'):
    user_to_update.last_name = post_data.get('last_name')
  if post_data.get('email'):
    user_to_update.email = post_data.get('email')
  if post_data.get('phone'):
    user_to_update.phone = post_data.get('phone')
  if post_data.get('city'):
    user_to_update.city = post_data.get('city')
  if post_data.get('state'):
    user_to_update.state = post_data.get('state')
  if post_data.get('org_id'):
    user_to_update.org_id = post_data.get('org_id')
  if post_data.get('active'):
    user_to_update.active = post_data.get('active')

  db.session.commit()

  return jsonify("User Updated"), 200 

if __name__ == '__main__':
  create_all()
  app.run(host='0.0.0.0', port=8089)