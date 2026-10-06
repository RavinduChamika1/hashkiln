"""Tests for HashKiln. No network is used."""
import pytest

import algorithms as alg
import attack_demo
import benchmark
import explorer
import login_sim
import salt_demo


# ---------- fast hashes ----------
def test_known_md5_and_sha256_vectors():
    assert alg.md5_hash("password") == "5f4dcc3b5aa765d61d8327deb882cf99"
    assert alg.sha256_hash("password") == "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"


def test_same_input_same_hash():
    assert alg.sha256_hash("abc") == alg.sha256_hash("abc")


def test_avalanche_effect_flips_about_half_the_bits():
    r = explorer.explore("password", "Password")["SHA-256"]
    assert 35 < r["percent"] < 65          # roughly 50%


# ---------- bcrypt ----------
def test_bcrypt_verify_right_and_wrong():
    stored = alg.bcrypt_hash("hunter2", cost=4)       # low cost = fast tests
    assert alg.bcrypt_verify("hunter2", stored)
    assert not alg.bcrypt_verify("hunter3", stored)


def test_bcrypt_salts_differ():
    a, b = alg.bcrypt_hash("same", cost=4), alg.bcrypt_hash("same", cost=4)
    assert a != b and alg.extract_bcrypt_salt(a) != alg.extract_bcrypt_salt(b)


def test_bcrypt_rejects_over_72_bytes():
    with pytest.raises(alg.PasswordTooLongError):
        alg.bcrypt_hash("x" * 73, cost=4)


# ---------- argon2 ----------
def test_argon2_verify_right_and_wrong():
    stored = alg.argon2_hash("hunter2")
    assert alg.argon2_verify("hunter2", stored)
    assert not alg.argon2_verify("nope", stored)


def test_argon2_is_argon2id_with_expected_params():
    parts = alg.extract_argon2_parts(alg.argon2_hash("x"))
    assert parts["algorithm"] == "argon2id"
    assert parts["params"] == "m=19456,t=2,p=1"


def test_argon2_salts_differ_and_not_needing_rehash():
    a, b = alg.argon2_hash("same"), alg.argon2_hash("same")
    assert a != b and not alg.argon2_needs_rehash(a)


def test_verify_handles_garbage_hashes():
    assert not alg.argon2_verify("x", "not-a-hash")
    assert not alg.bcrypt_verify("x", "not-a-hash")


# ---------- helpers ----------
def test_safe_equal():
    assert alg.safe_equal("abc", "abc") and not alg.safe_equal("abc", "abd")


# ---------- salt demo ----------
def test_unsalted_identical_but_salted_different():
    data = salt_demo.compare_unsalted_vs_salted()
    assert data["unsalted"][0] == data["unsalted"][1]
    assert data["bcrypt"][0] != data["bcrypt"][1]
    assert data["argon2"][0] != data["argon2"][1]


def test_lookup_table_cracks_unsalted_but_not_salted():
    assert salt_demo.lookup_table_attack(alg.sha256_hash("qwerty")) == "qwerty"
    assert salt_demo.lookup_table_attack(alg.bcrypt_hash("qwerty", cost=4)) is None


# ---------- attack demo ----------
def test_md5_database_fully_cracked_quickly():
    db = attack_demo.build_database("md5")
    result = attack_demo.attack("md5", db, budget_seconds=5)
    assert len(result.cracked) == result.total_users


def test_attack_respects_time_budget_on_slow_hash():
    db = attack_demo.build_database("argon2")
    result = attack_demo.attack("argon2", db, budget_seconds=0.3)
    assert result.seconds < 3 and not result.finished


# ---------- benchmark ----------
def test_slow_hashes_are_much_slower_than_md5():
    results = {r.name.split(" ")[0]: r for r in benchmark.run_benchmark(fast=True)}
    assert results["bcrypt"].slowdown > 100
    assert results["Argon2id"].slowdown > 100


# ---------- login simulator ----------
@pytest.mark.parametrize("algo", ["argon2id", "bcrypt", "md5"])
def test_signup_and_login_roundtrip(algo):
    record = login_sim.make_record("S3cret!pass", algo)
    assert login_sim.check_password("S3cret!pass", record)
    assert not login_sim.check_password("wrong", record)
    assert "S3cret!pass" not in record["stored"]          # real password never stored
