---
title: "0014 - `groupshared` Arguments"
params:
  authors:
    - llvm-beanz: Chris Bieneman
    - spall: Sarah Spall
  sponsors:
    - spall: Sarah Spall
  status: Under Consideration
---

## Implementation Status

|   | DXC     | Clang    |
|---|---------|----------|
| `groupshared` arguments | Complete | Complete |

## Introduction

This proposal introduces a new use of the `groupshared` keyword for function
arguments to allow passing `groupshared` arguments by address rather than by
value or copy-in/copy-out.

## Motivation

DXC's implementation of HLSL includes a set of Interlocked functions
implementing atomic operations on `groupshared` memory. These functions are not
expressible in HLSL and rely on special case implementation in DXC.

This capability is further used in the [DirectX Linear
Algebra](https://github.com/microsoft/hlsl-specs/blob/main/proposals/0035-linalg-matrix.md)
extension, which adds functions on a class method that rely on passing in large
blocks of groupshared memory.

## Proposed solution

HLSL 202x will allow the `groupshared` type annotation keyword on function
parameter declarations. When applied to a parameter declaration of
type `T`, the keyword alters the qualified type of the parameter to a `groupshared T &`
(a reference to `groupshared` memory of type `T`).

void fn(groupshared uint4 A) {}
```

No implicit or explicit conversion can change the memory space of an object.
LValue-to-RValue conversions load a value out of its specified address space
into a temporary value in the default address space. This is an implicit copy,
not an address space conversion. To perform such a conversion, a user must
declare a new object in the destination memory space and initialize it
appropriately. For overload resolution, the parameter type must be an exact
match in order for overload resolution to succeed since no conversions will be
valid.

Allowed:
```hlsl
void doesSomething(inout uint4);
void doesNothing(uint4);

void fn(groupshared uint4 A) {
  float4 LocalA = (float4) A;
  doesSomething(LocalA);
  doesSomething(A);
  doesNothing(LocalA);
  doesNothing(A);
  A = (uint4) LocalA;
}
```

Not Allowed:
void fn(groupshared uint4 A) {}
void fn2() {
  float4 B = 1.0.xxxx;
  fn(B); // error: no matching function for call to 'fn'
  fn((uint4)B); // error: no matching function for call to 'fn'
}
```

The feature supports any type that is valid to store in groupshared memory to be
used as groupshared arguments, including user-defined data types.

## Alternatives considered

[Reference
types](https://github.com/microsoft/hlsl-specs/blob/main/proposals/0006-reference-types.md)
is an obvious alternative. This proposal introduces a slightly conflicting
syntax from what we would prefer with reference types available.

This more minimal feature has material benefit today for both DXC and Clang, and
can avoid Clang requiring special case handling for library functions that
operate on `groupshared` memory such as the `Interlocked` intrinsics for atomic
operations. As such, this proposal is preferred to waiting until references can
be finalized.

### Overloading behavior

Overload sets including value types and `groupshared` arguments of the same
underlying type are ambiguous if the call site argument is `groupshared`.

void fn(groupshared uint shared);
void fn(uint u);

groupshared uint Shared;

void caller() {
  fn(Shared); // ambiguous

  uint Local;
  fn(Local); // Not ambiguous
  fn(5); // Not ambiguous
}
```

### Limitations

A function annotated with either `export` or `[noinline]` will not be allowed to
have function parameter declarations annotated with `groupshared`.  Doing so
will produce an error.

The argument to a `groupshared` function parameter must be a `groupshared`
variable.  If it is not, an error will be produced.

The argument to a `groupshared` function parameter must be of the same exact
type as the function parameter.  No implicit or explicit conversions are
allowed.  If they are not exactly the same, an error will be produced.
