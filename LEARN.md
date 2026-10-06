# What you learn in Week 2

1. **Hash function** - one-way scrambler. Same input, same output; cannot be reversed. A tiny change flips about half the bits (avalanche effect).
2. **Fast vs slow hashes** - MD5/SHA are built for speed, which helps attackers. bcrypt and Argon2id are slow on purpose.
3. **Salt** - a random, unique value per password, stored with the hash. It is not secret. It stops hash-sharing and pre-computed lookup tables.
4. **Work factor** - bcrypt's cost (2^cost rounds) or Argon2's memory/iterations/threads. Tune it so one hash takes a noticeable fraction of a second, and raise it over time.
5. **How login really works** - hash the typed password with the stored salt and compare. Compare in constant time (`hmac.compare_digest`).
6. **Upgrading hashes** - re-hash with stronger settings the next time the user logs in (`check_needs_rehash`).

## Common mistakes
- Using MD5/SHA-256 directly for passwords
- Writing your own salting or "secret sauce" crypto
- Ignoring bcrypt's 72-byte limit
- Comparing hashes with `==`
- Using the same low cost forever

## Further reading
- OWASP Password Storage Cheat Sheet
- NIST SP 800-63B (digital identity guidelines)
- Argon2 specification and the Password Hashing Competition
- Python docs: `hashlib`, `hmac`
