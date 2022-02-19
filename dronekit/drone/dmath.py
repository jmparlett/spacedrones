#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math

# we're in degrees only because were dumb

# sin and cosine for degrees
def dsin(n):
    '''take a angle in degrees n and return cosine of the angle'''
    return round(math.sin(math.radians(n)),5)

def dcos(n):
    '''take a angle in degrees n and return sine of the angle'''
    return round(math.cos(math.radians(n)),5)

def dtan(n):
    '''take a angle in degrees n and return tan of the angle'''
    return dsin(n)/dcos(n)

def datan(n):
    '''take a angle in degrees n and return atan of the angle'''
    return round(math.atan(math.radians(n)),5)
def dacos(n):
    '''take a angle in degrees n and return atan of the angle'''
    return round(math.acos(math.radians(n)),5)

##### Coordinate Translation #####
# C to R (r, θ, z) → (x, y, z) x = rcosθ, y = rsinθ, z = z
def cTor(r, theta, z):
    '''Cylindrical to Rectangular'''
    return (r * dcos(theta), r * dsin(theta), z)

# R to C (x, y, z) → (r, θ, z) r =  √(x^2 + y^2) , tanθ = x/y , z = z
def rToc(x, y, z):
    '''Rectangular to Cylindrical'''
    return (math.sqrt(x**2 + y**2), dtan(x/y), z)

# S to C (p, θ, φ) → (r, θ, z). r = psinφ, θ = θ, z = pcosφ
def sToc(p, theta, phi):
    '''Sphereical to Cylindrical'''
    return (p * dsin(phi), theta, p * dcos(phi))

# C to S (r, θ, z) → (p, θ, φ) p =√(r^2 + z^2) , θ = θ, tanφ = r/z
def cTos(r, theta, z):
    '''Cylindrical to Sphereical'''
    return (math.sqrt(r**2 + z**2), theta, datan(r/z))

# S to R (p, θ, φ) → (x, y, z), x = psinφ ∗ cosθ, y = psinφsinθ, z = pcosφ
def sTor(p, theta, phi):
    '''Sphereical to Rectangular'''
    return (p * dsin(phi) * dcos(theta), p * dsin(phi) * dsin(theta), p * dcos(phi))

# R to S (x, y, z) → (p, θ, φ) p = √(x^2, y^2, z^2), tanθ = y/x, cosφ = z√(x^2 + y^2 + z^2)
def rTos(x,y,z):
    return (math.sqrt(x**2 + y**2 + z**2), datan(y/x) if x != 0 else 0 , dacos(z * math.sqrt(x**2 + y**2 + z**2)))


def magnitude(x,y,z):
    return math.sqrt(x**2 + y**2 + z**2)

def invert(x,y,z):
    return (-x, -y, -z)


