---
title: "0019 - Size type"
params:
  authors:
    - llvm-beanz: Chris Bieneman
  sponsors:
    - llvm-beanz: Chris Bieneman
  status: Under Consideration
---

## Introduction

This proposal introduces `hlsl::size_t` as a _size type_ to represent sizes of
objects and offsets into memory.

## Motivation

HLSL does not define a size type, and instead uses (generally) `uint`. This
precludes the ability of APIs to represent 64-bit offsets without redefining
APIs.

## Proposed solution

HLSL should introduce a new `hlsl::size_t` type which is an
implementation-defined "size type", which must be an unsigned integer large
enough to represent the size of any valid object or offset.

APIs in the HLSL standard library should be updated to treat `size_t` as the
type for sizes and offsets.

This change should have no behavior change _except_ in DXC where the sizes in
some template arguments were defined as `int` instead of `uint` (see:
[#67](https://github.com/hlsl-tc57/tc57/issues/67)).
