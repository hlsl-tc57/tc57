---
title: "NNNN - User-defined Conversion Functions"
params:
  authors:
    - llvm-beanz: Chris Bieneman
  sponsors:
    - llvm-beanz: Chris Bieneman
  status: Under Consideration
---

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
