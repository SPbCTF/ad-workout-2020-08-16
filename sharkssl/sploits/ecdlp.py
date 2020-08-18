#!/usr/bin/env python
"""
Sagemath script calculating ECDLP for secp256k1
See https://ecc.danil.co/ for Sagemath installation instructions:
```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
sh Miniconda3-latest-Linux-x86_64.sh
conda install mamba -c conda-forge # faster dependencies resolver
mamba create -n sage sage python=3 -c conda-forge
conda activate sage
```

The better idea is to write a simple API and run it using gunicorn
with number of threads equal to core count
"""
import sys
from sage.all import EllipticCurve, GF, discrete_log_lambda

# https://www.secg.org/sec2-v2.pdf
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F

# Curve parameters for the curve equation: y^2 = x^3 + a*x +b
a = 0
b = 7

# Curve order
qq = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Create a finite field of order p
FF = GF(p)

# Define a curve over that field with specified Weierstrass a and b parameters
EC = EllipticCurve([FF(a), FF(b)])

# Since we know secp256k1's order we can skip computing it and set it explicitly
EC.set_order(qq)

# Create a variable for the base point
# G = EC.lift_x(
#     0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798)
# Wriong point above! Probably because of jsrsasign
G = EC(FF(55066263022277343669578718895168534326250603453777594175500187360389116729240), FF(
    32670510020758816978083085130507043184471273380659243275938904335757337482424))

x, y = sys.argv[1], sys.argv[2]
x, y = int(x, 16), int(y, 16)

P = EC(x, y)

# ECDLP using Pollard's lambda algorithm with bounds for 4 bytes
# About 40 seconds on cheapeast Intel Atom VPS
k = discrete_log_lambda(P, G, (1, 2**(4*8)), operation="+")
print(hex(k)[2:])
