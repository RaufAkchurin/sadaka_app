#TODO add test to expired token by time
# невалидный токен подсунуть

# async def test_jwt_tests():
#     # Test 1: Create JWT token
#     token = jwt.encode({"sub": "test_user", "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5)}, settings.SECRET_KEY, algorithm="HS256")
#
#     # Test 2: Verify JWT token
#     decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
#     assert decoded_token["sub"] == "test_user"
#     assert decoded_token["exp"] > datetime.datetime.utcnow()
#
#     # Test 3: Create JWT token with invalid secret key
#     invalid_token = jwt.encode({"sub": "test_user", "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5)}, "invalid_key", algorithm="HS256")
#     assert jwt.decode(invalid_token, "invalid_key", algorithms=["HS256"]) is None