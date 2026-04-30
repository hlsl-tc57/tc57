---
title: "NNNN - Simplified Overload Resolution"
draft: true
params:
  authors:
    - llvm-beanz: Chris Bieneman
  sponsors:
    - llvm-beanz: Chris Bieneman
  status: Under Consideration
---

## Introduction

This proposal suggests adopting an overload resolution algorithm that aligns
with C++'s approach to overload resolution. This algorithm will provide more
intuitive behavior for users and will bias toward erroring instead of choosing
an overload from ambiguous candidate sets.

## Motivation

DXC's overload resolution is near impossible to match completely without
inheriting significant implementation details of the compiler. Notabily, the way
DXC selects possible overload candidates is different for built-in functions
than for user-defined functions, which means that a calls to user-defined
functions can resolve differently than calls to built-in functions even if the
two functions have identical sets of possible overloads.

This situation is made more complicated by HLSL 2021's introduction of operator
overloading which expands the context in which overloads need to be resolved.
DXC's approach to overload resolution has unresolved bugs some of which cannot
be fixed without changing the behavior of existing code.

Aligning HLSL's overload resolution with C++ aids in addressing these issues as
well as making our language more future-resistant, and simplifying the
implementation in compilers already designed to mimic or support C++. The
C++-aligned specification language is also dramatically simplified specification
language which will be easier to test for conformance.

## Proposed solution

### Implicit conversions

This proposal suggests introducing new implicit conversions and conversion ranks
to classify conversions involving matrix and vector types as source and/or
destination arguments. The table below is the full list of proposed implicit
conversions and their ranks. The **bolded** are unique to HLSL and introduced by
this proposal, the remaining elements are inherited from C++. The table below is
sorted by the ranks in increasing order such that the conversion of the _lowest_
rank is preferred.

| Conversion  | Rank |
|-------------|------|
| No conversion (Identity) | Exact Match |
| Lvalue-to-rvalue | Exact Match |
| Array-to-pointer | Exact Match |
| Qualification | Exact Match |
| **Single Element to Scalar** | Exact Match |
| **Vector Scalar splat conversion** | **Extension** |
| **Matrix Scalar splat conversion** | **Extension** |
| Integral promotion | Promotion |
| Floating point promotion | Promotion |
| **Component-wise promotion** | Promotion |
| **Scalar splat promotion** | **Promotion Extension** |
| Integral conversion | Conversion |
| Floating point conversion | Conversion |
| Floating-integral conversion | Conversion |
| Boolean conversion | Conversion |
| **Component-wise conversion** | Conversion |
| **Scalar splat conversion** | **Conversion Extension** |
| **Vector truncation (without conversion)** | Truncation |
| **Matrix truncation (without conversion)** | Truncation |
| **Vector truncation promotion** | **Promotion Truncation** |
| **Matrix truncation promotion** | **Promotion Truncation** |
| **Vector truncation conversion** | **Conversion Truncation** |
| **Matrix truncation conversion** | **Conversion Truncation** |

The new conversions allow combining element type conversions with dimension
conversions. Supported implicit dimension conversions are either reductions in
row or column counts by discarding elements, or scalar extensions by
broadcasting a value to fill a matrix or vector.

Additionally a vector or matrix containing only one element may be implicitly
converted to a scalar of the element type, _and_ an additional conversion
sequence may be aplied from that scalar type.

### Overload resolution contexts

In HLSL 2021 as implemented by DXC overload resolution only occurs on the
invocation of a function named in a function call expression or for an operator
referenced when the argument to the left hand side is a class object.

This proposal extends the contexts that overload resolution occurs in to include
the function call operator on a class object, all operators referenced in
expressions, and invocations of conversion functions for initialization of an
object of non-class type.

### Overload candidate selection

DXC has different approaches for identification of overload candidates for
built-in functions and user-defined functions. This proposal suggests aligning
with the C++ candidate selection rules which are currently used for user-defined
functions.

### Overload resolution algorithm

DXC uses a scoring algorithm where each conversion is assigned a rank, the
number of conversions of each rank are summed, and the overload with the fewest
conversions of the worst rank is selected. This algorithm disambiguates some
cases that would be ambiguous in C++, but matches C++ overload resolution in all
non-ambiguous cases.

This proposal adopts a modified overload resolution algorithm from C++ which is
updated to account for the new conversions and conversion ranks defined in the
[implicit conversions](#implicit-conversions) section of this document.
