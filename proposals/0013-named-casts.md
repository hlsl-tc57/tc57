---
title: "0013 - Named Casts"
params:
  authors:
    - llvm-beanz: Chris Bieneman
  sponsors:
    - llvm-beanz: Chris Bieneman
  status: Refinement
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
`hlsl::elementwise_cast<T>` and `hlsl::bit_cast<T>`.

The `hlsl::static_cast<T>(V)` will behave similar to the C++ `static_cast<T>(V)`
expression, except as changes are required due to other differences between C++
and HLSL. It will convert the expression `V` to the result type `T`. The main
difference from C++ is that HLSL's `static_cast<T>` will always produce an
rvalue since HLSL does not have spellable lvalue reference types, and may not be
used for polymorphic casts for the same reason.

The `hlsl::elementwise_cast<T>(V)` will perform an element-wise conversion
(\ref{Conv.Flat}). The type of the expression `V` and the result type `T` must
be scalar layout compatible (\ref{Basic.Types.Scalarized}).

The `hlsl::bit_cast<T>(V)` cast function template will convert the expression
`V` to type `T` without modifying the precise bit representation. The type of
the expression `V` and the result type `T` must not be intangible types
(\ref{Basic.Types.Intangible}), and must be of the same size.

The HLSL `static_cast`, `bit_cast` and `elementwise_cast` templates are defined
in the `hlsl` namespace aligning with modern C++ conventions to avoid additions
to the global namespace. Additionally the `static_cast` construct will be
exposed via a using declaration into the global namespace allowing compatibility
with the historical C++ definition which remains in modern C++.

## Notes on deviations from C++

In the detailed design below the HLSL `static_cast` cannot produce lvalue
outputs, this is because lvalue references in HLSL are not spellable. This
causes some cascading reductions and simplifications of the spec language and
reduces the scope of `static_cast`.

## Detailed Design

### Addition to [Lex.Keywords]

> The keyword `static_cast` is added to the grammar of keywords. Diff below.

```diff
diff --git a/spec/lex.tex b/spec/lex.tex
index 7fbef9d..d454e2f 100644
--- a/spec/lex.tex
+++ b/spec/lex.tex
@@ -271,7 +271,7 @@ but are not required to emit a diagnostic:
   \terminal{inline inout int interface line lineadj linear namespace nointerpolation}\br
   \terminal{noperspective operator out packoffset payload point precise}\br
   \terminal{primitives reordercoherent return row\_major sampler\_state shared sizeof}\br
-  \terminal{snorm static struct switch tbuffer template this triangle}\br
+  \terminal{snorm static static_cast struct switch tbuffer template this triangle}\br
   \terminal{triangleadj true typedef typename uniform unorm unsigned using vertices}\br
   \terminal{void while}
 \end{grammar}

```

### Static cast [Expr.StaticCast]

The `static_cast<T>(e)` expression converts the expression `e` to a new rvalue
object of type `T`. An lvalue-to-rvalue (\ref{Conv.LVal}) is applied to the
operand if the expression is an lvalue.

The expression is ill-formed if the conversion cannot be
performed by one of the conversions described in this sub-clause.

Any expression may be converted to type `void`; discarding the result.

An expression _E_ can be converted to type `T` if there exists an implicit
conversion sequence from _E_ to `T`.

> Editor's comment: This will need to be updated if
> 0018-user-defined-conversions is accepted.

An expression _E_ can be converted to type `T` if there exists a standard
conversion sequence from the type of `T` to the type of _E_, this conversion
applied in reverse is an _inverted_ standard conversion sequence.

An expression _E_ can be converted to type `bool` if there exists a valid
boolean conversion conversion for the expression (\ref{Conv.Bool}).

An expression _E_ of scoped enumeration type (\ref{Decl.Enum}), can be
explicitly converted to boolean, integral, or floating-point type `T`; the
conversion behaves as if _E_ were first converted to the enumeration's
underlying type then to `T`.

An expression _E_ of integral or enumeration type can be explicitly converted to
a value of enumeration type `T`. The value is unchanged if it is within the
range of the enumeration values of `T`; otherwise the resulting value is
unspecified.

An expression _E_ of floating-point type can be explicitly converted to a value
of enumeration type `T`. The conversion behaves as if _E_ were first converted
to the enumeration's underlying type then to `T`.

### Additions to the Conversion Functions Library Clause

The following definitions should be added to the [Conversion
Functions](https://github.com/hlsl-tc57/tc57/issues/162) library clause.

#### Function Template `elementwise_cast`

```
template<typename DestTy, typename SrcTy>
constexpr DestTy elementwise_cast(const SrcTy Src);
```

_Requires:_ `DestTy` and `SrcTy` are scalar layout compatible types
(\ref{Basic.Types.Scalarized})
_Returns:_ An object of type `DestTy`. Each subobject in the scalarized
representation of the returned object is initialized as-if by copy
initialization of the corresponding subojbect in the scalarized representation
of `Src` (\ref{Basic.Types.Scalarized}).

#### Function Template `bit_cast`

```
template<typename DestTy, typename SrcTy>
constexpr DestTy bit_cast(const SrcTy Src);
```

_Requires:_ `sizeof(DestTy) == sizeof(SrcTy)` is `true`;
_Returns:_ An object of type `DestTy`. Each bit in the the object representation
of the `Src` argument is replicated into the cooresponding bit in the value
representation of the newly created `DestTy` object. Padding bits in the result
are unspecified. If an object or subobject of the returned value has a bit
pattern that does not map to a value of that type, the behavior is undefined.
