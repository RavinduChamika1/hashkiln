# Lab: Try it yourself

**Exercise 1 (Demo 2):** Run the benchmark. How many times slower is bcrypt than MD5? Why does that help a defender?

**Exercise 2 (Demo 1):** Hash `hello` and `hellp`. How many bits changed? Is it close to 50%?

**Exercise 3:** In `src/algorithms.py`, change `BCRYPT_COST` from 12 to 13. Re-run the benchmark. What happens to the time, and why?

**Exercise 4:** In `src/algorithms.py`, change `ARGON2_MEMORY_KIB` to 65536. What changes in the speed and in the stored string?

**Exercise 5 (Demo 5):** Sign up two users with the same password using MD5, then with Argon2id. View the stored database. What do you notice?

**Exercise 6 (hard):** Add PBKDF2 (`hashlib.pbkdf2_hmac`, SHA-256, 600,000 iterations) to the benchmark and compare it with bcrypt and Argon2id.

Put your answers in `labs/solutions/`.
