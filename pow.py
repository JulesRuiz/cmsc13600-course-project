import hashlib

cnet_id = "jcruiz"

nonce = 0

while True:
    test = cnet_id + str(nonce)
    h = hashlib.sha256(test.encode()).hexdigest()

    if h.startswith("0000000"):
        print("FOUND!")
        print("nonce:", nonce)
        print("hash:", h)
        break

    nonce += 1
