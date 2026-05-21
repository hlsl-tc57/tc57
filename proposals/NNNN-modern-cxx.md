---
title: NNNN - Modern C++ Features
params:
  authors:
  - llvm-beanz: Chris Bieneman
  status: Under Consideration
---

## Introduction

In DXC HLSL is a set of feature extensions on top of a subset of C++98. C++98
is now over 20 years old and most modern C++ users have adopted newer language
constructs. This proposal suggests integrating high-impact modern C++ features
that should be low-cost to implement.

## Motivation

HLSL's C++ base is over a decade old. Modern C++ features have been frequently
requested additions for HLSL. Features introduced in C++11 and C++14 have been
in use for over a decade and are widely adopted. C++17 is nearly a decade old
now as well, and also has many widely adopted features. Conversely C++98 has
some oddities that are unusual and unexpected to developers who may have started
their career after modern C++ was widely adopted.

## Proposed solution

### C++11

HLSL should integrate the following C++11 features ([Source](https://en.cppreference.com/cpp/11)):

* auto
* decltype
* constexpr
* C++11 scoped enumerations
* variadic templates
* user-defined literals
* Static assert
* Template parsing rules (no required space in `>>`)

#### C++11 Excluded Features

* Range-based for loops (grammar ambiguity with HLSL annotations)
* C++11 attributes (will be a separate larger proposal)
* Defaulted and deleted functions (requires constructors)
* C++ list initialization (requires revamping HLSL initialization)
* type aliases (already in HLSL 2021)
* `alignof` and `alignas` (requires target bytecode changes)
* Lambda expressions (will require a separate larger proposal due to type system
  changes)

### C++14

C++14 features that we could consider ([Source](https://en.cppreference.com/cpp/14)):

* variable templates
* relaxed restrictions on constexpr functions
* binary literals
* digit separators
* return type deduction for functions

#### C++14 Excluded features

* generic lambdas (requires lambdas)
* lambda init-capture (requires lambdas)
* new/delete elision (requires new/delete)
* aggregate classes with default non-static member initializers (requires constructors)

### C++17

C++17 features that we could consider ([Source](https://en.cppreference.com/cpp/17)):

* compile-time `if constexpr`
* initializers for if and switch
* [temporary materialization](https://en.cppreference.com/cpp/language/implicit_conversion#Temporary_materialization)
* structured bindings (assignment decomposition)
* Templates
  * fold-expressions ( ... )
  * class template argument deduction tuple t(4, 3, 2.5)
  * non-type template parameters declared with auto
* Namespaces
  * simplified nested namespaces
  * using-declaration declaring multiple names
  * attribute namespaces don't have to repeat
* new attributes:
  * [[fallthrough]]
  * [[maybe_unused]]
  * [[nodiscard]]
* __has_include

#### C++17 Excluded Features

* u8 character literal (HLSL does not have 8-bit types)
* made noexcept part of type system (HLSL does not have exceptions)
* new order of evaluation rules (these changes don't apply to HLSL)
* lambda capture of *this (requires lambdas)
* constexpr lambda (requires lambdas)
* inline variables (requires linkage model changes)
* guaranteed copy elision (requires construction & rvalue references)

### C++20 and later

Adopting C++ 20 and later features is explicitly rejected due to feasibility in
existing implementations.
