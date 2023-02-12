print('Start #################################################################');

db = db.getSiblingDB('api_prod_db');
db.createUser(
  {
    user: 'api_user',
    pwd: 'foodPasswrd177',
    roles: [{ role: 'readWrite', db: 'api_prod_db' }],
  },
);
db.createCollection('recipes');

db = db.getSiblingDB('api_dev_db');
db.createUser(
  {
    user: 'api_user',
    pwd: 'foodPasswrd177',
    roles: [{ role: 'readWrite', db: 'api_dev_db' }],
  },
);
db.createCollection('recipes');

db = db.getSiblingDB('api_test_db');
db.createUser(
  {
    user: 'api_user',
    pwd: 'foodPasswrd177',
    roles: [{ role: 'readWrite', db: 'api_test_db' }],
  },
);
db.createCollection('recipes');
db = db.getSiblingDB('user_info');
db.createUser(
  {
    user: 'api_user',
    pwd: 'foodPasswrd177',
    roles: [{ role: 'readWrite', db: 'user_info' }],
  },
);
db.createCollection('user_info');
db = db.getSiblingDB('user_security');
db.createUser(
  {
    user: 'api_admin',
    pwd: 'foodPasswrd177SUPERSECURE',
    roles: [{ role: 'readWrite', db: 'user_security' }],
  },
);
db.createCollection('user_security');

print('END #################################################################');