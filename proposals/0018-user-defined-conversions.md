---
title: "0018 - User-defined Conversion Functions"
params:
  authors:
    - llvm-beanz: Chris Bieneman
  sponsors:
    - llvm-beanz: Chris Bieneman
  status: Refinement
---

## Implementation Status

|   | DXC     | Clang    |
|---|---------|----------|
| user-defined conversions | [Prototype implementation](https://github.com/llvm-beanz/DirectXShaderCompiler/commit/7f0754e2cd8c29859807c9f0b37983ed62e67934) | Complete |


## Introduction

User defined conversion functions are an extremly useful mechanism to allow
users to define ways that their objects can be converted from one type to
another. This allows for complex data transformations as well as simplified
syntaxes for common tasks (like checking validity by casting to bool).

## Motivation

HLSL 2021 intended to support user-defined conversion functions, but it was
realized after release that the feature did not work, so they were disabled in
[DXC in April
2026](https://github.com/microsoft/DirectXShaderCompiler/pull/8206).

This was always a feature the HLSL compiler intended to support, so this
proposal codifies it as a supported feature for HLSL 202x.

## Proposed solution

HLSL will accept the syntax for defining member functions of the form `operator
T()` where `T` is any built-in or user-defined type.

User defined conversion functions will be resovled according to the rules in
[0003](0003-overload-resolution.md) in explicit cast expressions of the form
`(T)Obj` and in initialization expressions for built-in types such as `T X =
Obj` where `T` is a built-in type.

This proposal also will introduce the `explicit` keyword which may only be
applied to a user-defined conversion function. When a conversion function is
annotated with the `explicit` keyword the conversion function will be excluded
from any overload set constructed for implicit conversions, allowing the
function to only be resolved in explicit cast expressions.
