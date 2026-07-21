---
title: 0015 - const-qualified Non-static Member Functions
params:
  authors:
  - llvm-beanz: Chris Bieneman
  sponsors:
  - llvm-beanz: Chris Bieneman
  status: Under Consideration
---

## Implementation Status

|   | DXC     | Clang    |
|---|---------|----------|
| `const` member functions | [Prototype implementation](https://github.com/llvm-beanz/DirectXShaderCompiler/commit/aa44718f81c58d6aca7d53d0705c897bd2c7eae4) | Complete |

## Introduction

HLSL does not currently support `const` non-`static` member functions for user-defined data
types. This proposal seeks to add support for `const` non-`static` member functions, and to
adopt const-correct behaviors across the HLSL library objects.

## Motivation

The absence of `const` non-`static` member functions causes some challenges since HLSL
injected ASTs do have `const` and non-`const` non-`static` member functions.
Further, since variables can be `const`-qualified, without the ability to
specify `const` there are some cases that cannot be worked around without
breaking `const`-correctness.

DXC has received a number of issues relating to this. Two recent issues are
listed below:

* https://github.com/microsoft/DirectXShaderCompiler/issues/4340
* https://github.com/microsoft/DirectXShaderCompiler/issues/4706

In the first issue, a user defined data type's functions are basically unusable
if the data type is placed in a `ConstantBuffer`. This results from the
`ConstantBuffer` access returning `const &` objects.

The second issue describes a similar problem, where overloaded operators on
instances of `const`-qualified user-defined types are unusable.

## Proposed solution

Following C++, HLSL will enable support for `const` non-`static` member functions and
instance operator overloads (henceforth collectively referred to as constant
member functions) to allow execution of member functions on `const` objects and
preserve `const` qualifiers.

Updates to HLSL's built-in data types to observe best practices in
const-correctness will follow the introduction of language support. Functions
which return mutable lvalue references will become non-constant member
functions, and functions which return constant lvalue references or object values
will become constant member functions.

### Syntactic Changes

C++'s existing syntax for declaring constant instance functions is compatible
with HLSL. Adoption of this syntax does not introduce any syntactic ambiguities
with existing HLSL constructs. Adding the `const` keyword to the end of the
function declarator before the optional function body will denote a const
member function function. The `const` keyword applies to the implicit object
argument so it can only be applied to non-`static` member functions. See the
examples below defining both a constant function and a constant overload of the
call `()` operator:

```c++
struct Pupper {
  void Wag() const { /* body omitted */ }
  void operator() const { /* body omitted */ }
};
```

This proposal also introduces the `mutable` keyword as a storage class for
non-static member variables. Variables declared as `mutable` may be modified
within `const` instances both inside and outside `const` instance methods.

### Semantic Changes

In a const member function, the implicit object parameter (`this`) becomes a
constant lvalue reference (`const &`). Code modifying any field of the `this`
object is ill-formed and will produce a diagnostic. Calls to non-constant member
functions are also ill-formed and will produce a diagnostic.

This change requires modifications to HLSL's overload resolution rules to
account for the const-ness of object parameters. When performing lookup of
possible overload candidates, overloaded functions with non-constant implicit
object parameters are invalid candidates when the implicit object is constant.

Standard HLSL argument promotion rules will apply for the object parameter, but
they cannot remove the `const` qualifier and shall not convert from a constant
lvalue to a non-constant rvalue by copying the implicit argument as is valid for
other arguments.

### HLSL Data Type Changes

Introducing constant member functions provides an opportunity to revisit the
const-correctness patterns of existing HLSL data types. With this change we will
perform an audit of existing data types to provide constant and non-constant
member functions as appropriate for the data type.

When applied to HLSL intangible types, the `const` qualifier will apply as if to
the handle, not the data the handle grants access to. For example, a `const
RWBuffer<T>` will still allow writes to the underlying resource, however the
resource variable itself cannot be re-assigned.

### Impact on Existing Code

Supporting constant member function overload resolution will break existing code
that calls member functions on `cbuffer`, `tbuffer` or global constant variables.
Consider the following valid HLSL:

```c++
struct Hat {
  int getFeathers() {
    return Feathers;
  }
  int Feathers;
};

cbuffer CB {
  Hat H;
};

export int GetFeatherCount() {
  return H.getFeathers();
}
```

This code is valid under HLSL 2021 because HLSL ignores the const-ness of the
implicit object parameter, however any writes to the constant data are dropped.
On introducing constant member functions, this code is ill-formed because these
declarations inside a `cbuffer` are implicitly constant and will produce a
diagnostic.

### Const-correct Resources

Implementing const-correct member functions on built-in HLSL data types should
have no disruption to users.

Consider the following code:

```c++
void setValue(RWBuffer<int> R, int Val, int Index) {
  R[Index] = Val;
}
void setValueConst(const RWBuffer<int> R, int Val, int Index) {
  setValue(R, Val, Index);
}
```

In `setValueConst`, the `const` qualifier applies to the _instance_ of the
`RWBuffer` parameter. A new `RWBuffer<T>` variable can be created from a `const
RWBuffer<T>` via copy-initialization (standard copy construction), allowing
`setValueConst` to call `setValue`. This does not violate const-correctness
since the handle is treated as const while the data it references is not.

> NOTE: DXC already generates methods on built-in objects as `const` in the
> hardcoded AST generation code.

## Detailed Design

### Additions to [Lex.Keywords]

Add `mutable` keyword to the grammar for keywords.

### Additions to Lvalues and rvalues [Basic.lval]

The value referred to by a `const`-qualified expression shall not be modified
except if the value is of class type and contains a `mutable` member, the
mutable member may be modified.

### Storage Class Specifiers [Decl.Specifiers.Storage]

```latex
\define{storage-class-specifier}\br
  \terminal{static}\br
  \terminal{mutable}
```

A _decl-specifier-seq_ shall contain at most one _storage-class-specifier_. Any
_decl-specifier-seq_ that contains a _storage-class-specifier_ shall not contain
a `typedef` _decl-specifier_, and it shall contain an _init-declarator-list_
that contains at least one _declarator_. The specified _storage-class-specifier_
applies to the names declared by each _declarator_ in the
_init-declarator-list_. An explicit specialization of a template declaration may
not have a _storage-class-specifier_.

The `static` specifier may be applied to names of variables at global,
namespace, class and function scope and to names of functions at global,
namespace, and class scope. A variable declared with the `static` storage class
has static storage duration (\ref{{Basic.Storage}}).

The `mutable` specifier may be applied to names of class data members and cannot
be applied to names declared `const`.


### Function Definitions [Decl.Functions]

Function definitions have the form

```latex
\define{function-definition}\br
   \opt{attribute-specifier-seq} \opt{decl-specifier-seq} declarator function-body

\define{function-body}\br
  compound-statement
```

If present, the _attribute-specifier-seq_ applies to the function.

The declarator shall be of the form

  _identifier_ `(` _parameter-declaration-clause_ `)` `const`<sub>opt</sub> _attribute-specifier-seq_<sub>opt</sub>

The `const` qualifier shall only be allowed on non-static member functions.

### Partial Text for: Nonstatic member functions [Class.MemberFunctions.NonStatic]

A non-static member function may be declared `const`, such a function is called
a _const member function_. The `const` qualifier of a const member function
applies to the `this` reference, and affects the type of the member function.
