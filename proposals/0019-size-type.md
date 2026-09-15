---
title: "0019 - Size type"
slug: "0019"
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

## Detailed design

### Types [Math.Types]

The HLSL standard library includes a set of type aliases. The declarations for
the aliases shall appear both in the `hlsl` namespace and in the global
namespace.

```hlsl
namespace hlsl {
  typedef _16-bit signed integer type_ int16_t;  // optional
  typedef _32-bit signed integer type_ int32_t;
  typedef _64-bit signed integer_ int64_t;

  typedef _16-bit unsigned integer type_ uint16_t;  // optional
  typedef _32-bit unsigned integer type_ uint32_t;
  typedef _32-bit unsigned integer type_ uint;
  typedef _64-bit unsigned integer type_ uint64_t;

  typedef _16-bit floating point type_ float16_t; // optional
  typedef _32-bit floating point type_ float32_t;
  typedef _64-bit floating point type_ float64_t;

  typedef _unsigned integer type_ size_t;
}
```

The signed integer data types defined as `intN_t` and unsigned integer data
types defined as `uintN_t` specify the specific bit-width of the object and
value representation of the object. The data type `uint` will be a 32-bit
unsigned integer type.

The floating point data types defined as `floatN_t` specify the specific
bit-width of the object and value representation of the object, and shall use
the corresponding binary formats defined by \gls{IEEE754} (i.e. binary16,
binary32, binary64).

The data type `size_t` will be an implementation-defined unsigned integer type
that is large enough to contain the size in bytes of any object.
