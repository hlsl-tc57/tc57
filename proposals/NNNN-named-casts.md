---
title: "NNNN - Named Casts"
draft: true
params:
  authors:
    - llvm-beanz: Chris Bieneman
  sponsors:
    - llvm-beanz: Chris Bieneman
  status: Under Consideration
---

## Introduction

This proposal introduces C++-like named casts which perform specific defined
casts and have more strict semantics than the general C-style casting syntax.

## Motivation

Long ago C++ adopted named casts to remove ambiguity around what data
transformation a cast performs. These take the forms `static_cast`,
`reinterpret_cast`, `const_cast`, `dynamic_cast`, and most recently `bit_cast`.

This proposal introduces named casts for HLSL to allow unambiguous ways to cast
values from a source type to a destination type with tight validation.

## Proposed solution

HLSL will introduce three new named cast templates, `static_cast<T>`,
`elementwise_cast<T>` and `hlsl::bit_cast<T>`.

The `static_cast<T>(V)` will behave similar to the C++ `static_cast<T>(V)`
expression, except as changes are required due to other differences between C++
and HLSL. It will convert the expression `V` to the result type `T`. The main
difference from C++ is that HLSL's `static_cast<T>` will always produce an
rvalue since HLSL does not have spellable lvalue reference types, and may not be
used for polymorphic casts for the same reason.

The `elementwise_cast<T>(V)`, will perform an element-wise conversion
(\ref{Conv.Flat}). The type of the expression `V` and the result type `T` must
be scalar layout compatible (\ref{Basic.Types.Scalarized}).

The `hlsl::bit_cast<T>(V)` cast function template will convert the expression
`V` to type `T` without modifying the precise bit representation. The type of
the expression `V` and the result type `T` must not be intangible types
(\ref{Basic.Types.Intangible}), and must be of the same size.

> Note: the `bit_cast` template is put in the hlsl namespace since it will be a
> function template matching how C++ implemented `std::bit_cast`.
