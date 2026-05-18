---
title: NNNN - Adopt C++11 Base
params:
  authors:
  - llvm-beanz: Chris Bieneman
  status: Under Consideration
---

## Introduction

In DXC HLSL is a set of feature extensions on top of a subset of C++98. C++98
is now over 20 years old and most modern C++ users have adopted newer language
constructs. This proposal suggests taking the small step of updating HLSL 202y's
base C++ language to C++11.

## Motivation

C++11 is over a decade old and introduced widely adopted features, many of which
have been frequently requested additions for HLSL. Conversely C++98 has some
oddities that are unusual and unexpected to developers who may have started
their career after C++11 was widely adopted.

## Proposed solution

Adopt a C++11 base language and include the following C++11 features in HLSL:

* auto
* decltype
* constexpr
* C++11 scoped enumerations
* variadic templates
* user-defined literals
* C++11 attributes
* Lambda expressions
* Static assert
* Range-based for loops
* Template parsing rules (no required space in `>>`)

## Alternatives considered

### C++20

We could instead adopt an even more recent C++, like C++20. The main drawback of
that is that it significantly increases the rapid divergence from DXC, and it
gives us a longer list of features that we need to rectify against HLSL's
language features. Adopting a C++11 base for 202y does not prevent later
versions from adopting newer C++ base standards, but it does allow us to phase
the changes in iteratively as HLSL evolves.
