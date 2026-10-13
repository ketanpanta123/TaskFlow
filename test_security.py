from security import hash_password,verify_password

password="mypassword123"

hashed=hash_password(password)

print("password:",password)
print("hash:",hashed)

print("correct password:",verify_password(password,hashed))
print("wrong password:",verify_password("wrongpassword",hashed))