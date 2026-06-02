---
title: "0003 - Simplified Overload Resolution"
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
| C++-aligned best match | Not Planned | Complete |
| C++-aligned candidate selection | Not Planned | Complete |

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

## Detailed Design

### Overloading `[Overload]`

When a single name is declared with two or more different declarations in the
same scope, the name is _overloaded_. A declaration that declares an
overloaded name is called an _overloaded declaration_. The set of
overloaded declarations that declare the same overloaded name are that name's
_overload set_.

Only function and template declarations can be overloaded; variable and type
declarations cannot be overloaded.

#### Overloadable Declarations `[Overload.Decl]`

This section specifies the cases in which a function declaration cannot be
overloaded. Any program that contains an invalid overload set is ill-formed.

An overload set is invalid if:
  * One or more declaration in the overload set only differ by return type.

```hlsl
int Yeet();
uint Yeet(); // ill-formed: decls differ only by return type
```
  * An overload set contains more than one member function declarations with
  the same _parameter-type-list_, and one of those declarations is a
  `static` member function declaration (\ref{Classes.Static}).
```hlsl
class Doggo {
  static void pet();
  void pet();              // ill-formed: static pet has the same parameter-type-list
  void pet() const;        // ill-formed: static pet has the same parameter-type-list

  void wagTail();          // valid: no conflicting static declaration.
  void wagTail() const;    // valid: no conflicting static declaration.

  static void bark(Doggo D);
  void bark();             // valid: static bark parameter-type-list is different
  void bark() const;       // valid: static bark parameter-type-list is different
};
```

  * An overload set contains more than one entry function declaration (\ref{Decl.Attr.Entry}).
```hlsl
[shader("vertex")]
void VS();
void VS(int);              // valid: only one entry point.

[shader("vertex")]
void Entry();

[shader("compute")]
void Entry(int);           // ill-formed: an overload set cannot have more than one entry function
```

  * An overload set contains more than one function declaration which only
  differ in parameter declarations of equivalent types.
```hlsl
void F(int4 I);
void F(vector<int, 4> I);  // ill-formed: int4 is a type alias of vector<int, 4>
```

  * An overload set contains more than one function declaration which only
  differ in `const` specifiers.
```hlsl
void G(int);
void G(const int);         // ill-formed: redeclaration of G(int)
void G(int) {}
void G(const int) {}       // ill-formed: redefinition of G(int)
```

  * An overload set contains more than one function declaration which only
  differ in parameters mismatching `out` and `inout`.
```hlsl
void H(int);
void H(in int);            // valid: redeclaration of H(int)
void H(inout int);         // valid: overloading between in and inout is allowed

void I(in int);
void I(out int);           // valid: overloading between in and out is allowed

void J(out int);
void J(inout int);         // ill-formed: Cannot overload based on out/inout mismatch
```

#### Declaration Matching `[Overload.Match]`

Two function declarations with the same name and same parameter lists refer to
the same function if they are in the same scope (\ref{Basic.Scope}). A function
declaration in a containing scope is not the same as a function of the same
name and parameter list in a contained scope.

#### Overload Resolution `[Overload.Res]`

_Overload resolution_ is process by which a function call is mapped to
a the best overloaded function declaration. Overload resolution uses set of
functions called the _candidate set_, and a list of expressions that
comprise the argument list for the call.

Overload resolution selects the function to call in the following
contexts:

  * invocation of a function named in a function call expression;
  * invocation of a function call operator on a class object named in
  function call syntax;
  * invocation of the operator referenced in an expression;
  * invocation of a user-defined conversion for copy-initialization of a
  class object;
  * invocation of a conversion function for initialization of an object of a
  nonclass type from an expression of class type.

In each of these contexts a unique method is used to construct the overload
candidate set and argument expression list.

##### Candidate Functions and Argument Lists `[Overload.Res.Sets]`

At each point where an overload must be resolved an implementation will generate
a _candidate set_, containing all possible candidate functions, and the argument
list for the overloaded call. The subclauses under \ref(Overload.Res.Sets)
define the process by which the candidate set and argument lists are constructed
in each context where overload resolution occurs.

A candidate set may include both member and non-member functions to be resolved
against the same argument set. Member functions have an extra _implicit object
parameter_, representing the object the function is called on. For the purposes
of overload resolution a static member function is considered to have an
implicit object parameter.

When appropriate the context shall construct an _implied object argument_
referring to the object operated on.

The implicit object parameter and implied object argument if present are always
the first parameter or argument.

The type of the implicit object parameter is: lvalue reference `cv T`; where `T`
is the class containing the declaration of the function, and `cv` is the
_cv-qualification_ on the function declaration.

Implied object arguments behave the same as any explicit argument, no temporary
object shall be created to hold the argument for the implicit object parameter
except when the implicit object parameter is a member of a
_cbuffer-declaration_.

If a candidate is a function template, candidate specializations are generated
through template argument deduction (\ref{Template.Deduction}), candidates are
then handled as any other candidate. A name may refer to more than one function
template, in which case candidate functions shall be generated for each function
template to form the full candidate set.

> TODO: @llvm-beanz to continue fleshing this out...

##### Viable Functions `[Overload.Res.Viable]`

Given the candidate set and argument expressions as determined by the
relevant context (\ref{Overload.Res.Sets}), a subset of viable functions can be
selected from the candidate set.

A function candidate $F(P_0 ... P_m)$ is not a viable function for a call
with argument list $A_0 ... A_n$ if:

* The function has fewer parameters than there are
  arguments in the argument list ($m < n$).
* The function has more parameters than there are arguments to the
  argument list ($m > n$), and function parameters $ P_{n+1} ... P_m $ do not
  all have default arguments.
* There is not an implicit conversion sequence that converts each argument
  $A_i$ to the type of the corresponding parameter $P_i$.

##### Best Viable Function `[Overload.Res.Best]`

For an overloaded call with arguments $A_0 ... A_n$, each viable function
$F(P_0 ... P_m)$, has a set of implicit conversion sequences $ICS_0(F) ... ICS_m(F)$
defining the conversion sequences for each argument $A_i$ to the
type of parameter $P_i$.

A viable function $F$ is defined to be a better function than another
viable function $f\`$ if for all arguments $ICS_i(F)$ is not a worse
conversion sequence than $ICS_i(f\`)$, and:

* for some argument $j$, $ICS_j(F)$ is a better conversion than
  $ICS_j(f\`)$ or,
* in the context of an initialization by user-defined conversion, the
  conversion sequence from the return type of $F$ to the destination type is a
  better conversion sequence than the return type of $f\`$ to the destination
  type or,
* $F$ is a non-template function and $f\`$ is a function template
  specialization, or
* $F$ and $f\`$ are both function template specializations and $F$ is
  more specialized than $f\`$ according to function template partial ordering
  rules (\ref{Template.Func.Order}).

If there is one viable function that is a better function than all the other
viable functions, it is the selected function; otherwise the call is ill-formed.

If the resolved overload is a function with multiple declarations, and if at
least two of these declarations specify a default argument that made the
function viable, the program is ill-formed.

```hlsl
void F(int X = 1);
void F(float Y = 2.0f);

void Fn() {
  F(1);     // Okay.
  F(3.0f);  // Okay.
  F();      // Ill-formed.
}
```

##### Implicit Conversion Sequences `[Overload.ICS]`

An _implicit conversion sequence_ is a sequence of conversions which
converts a source value to a prvalue of destination type. In overload resolution
the source value is the argument expression in a function call, and the
destination type is the type of the corresponding parameter of the function
being called.

When a parameter is a cxvalue an _inverted implicit conversion sequence_ is
required to convert the parameter type back to the argument type
for writing back to the argument expression lvalue. An inverted implicit
conversion sequence must be a well-formed implicit conversion sequence where the
source value is the implicit cxvalue of the parameter type, and the destination
type is the argument expression's lvalue type.

A well-formed implicit conversion sequence is either a _standard conversion
sequence_, or a _user-defined conversion sequence_.

In the following contexts an implicit conversion sequence can only be a
standard conversion sequence:

  * Argument conversion for a user-defined conversion function.
  * Copying a temporary for class copy-initialization.
  * When passing an initializer-list as a single argument.
  * Copy-initialization of a class by user-defined conversion.

An implicit conversion sequence models a copy-initialization unless it is an
inverted implicit conversion sequence when it models an assignment. Any
difference in top-level cv-qualification is handled by the copy-initialization
or assignment, and does not constitute a conversion.

> Note: "Top-level" cv-qualification refers to the qualification of the value.
> This means an parameter of type `T` can be initialized by a argument of type
> `const T`. This does not mean that a parameter of type `inout T` can be
> initialized with a argument of type `const T` because there is no valid
> inverted conversion system to assign back to a value of type `const T`.

When the source value type and the destination type are the same, the
implicit conversion sequence is an _identity conversion_, which signifies
no conversion.

Only standard conversion sequences that do not create temporary objects are
valid for implicit object parameters or left operand to assignment operators.

If no sequence of conversions can be found to convert a source value to the
destination type, an implicit conversion sequence cannot be formed.

If several different sequences of conversions exist that convert the source
value to the destination type, the implicit conversion sequence is defined to be
the unique conversion sequence designated the _ambiguous conversion sequence_.
For the purpose of ranking implicit conversion sequences, the
ambiguous conversion sequence is treated as a user-defined sequence that is
indistinguishable from any other user-defined conversion sequence. If overload
resolution selects a function using the ambiguous conversion sequence as the
best match for a call, the call is ill-formed.

**Standard Conversion Sequences `[Overload.ICS.SCS]`**

The conversions that comprise a standard conversion sequence and the
composition of the sequence are defined in Chapter \ref{Conv}.

Each standard conversion is given a category and rank as defined in the table
below:

| Conversion | Category | Rank | Reference |
|------------|----------|------|-----------|
| No conversion | Identity | Exact Match | |
| Lvalue-to-rvalue | Lvalue Transformation | Exact Match | \ref{Conv.lval} |
| Array-to-pointer | Lvalue Transformation | Exact Match | \ref{Conv.array} |
| Qualification | Qualification Adjustment | Exact Match | \ref{Conv.qual} |
| Vector Scalar splat conversion | Scalar Extension Conversion | Conversion Extension | \ref{Conv.vsplat} |
| Matrix Scalar splat conversion | Scalar Extension Conversion | Conversion Extension | \ref{Conv.msplat} |
| Integral promotion | Promotion | Promotion | \ref{Conv.iconv} & \ref{Conv.rank.int} |
| Floating point promotion | Promotion | Promotion | \ref{Conv.fconv} & \ref{Conv.rank.float} |
| Component-wise promotion | Promotion | Promotion | \ref{Conv.cwise} |
| Scalar splat promotion | Scalar Extension Promotion | Promotion Extension | \ref{Conv.vsplat} |
| Integral conversion | Conversion | Conversion | \ref{Conv.iconv} |
| Floating point conversion | Convesrion | Conversion | \ref{Conv.fconv} |
| Floating-integral conversion | Conversion | Conversion | \ref{Conv.fpint} |
| Boolean conversion | Convesrion | Conversion | \ref{Conv.bool} |
| Component-wise conversion | Conversion | Conversion | \ref{Conv.cwise} |
| Scalar splat conversion | Scalar Extension Conversion | Conversion Extension | \ref{Conv.vsplat} |
| Vector truncation (without conversion) | Dimensionality Reduction | Truncation | \ref{Conv.vtrunc} |
| Vector truncation promotion | Dimensionality Reduction Promotion | Promotion Truncation | \ref{Conv.vtrunc} |
| Vector truncation conversion | Dimensionality Reduction Conversion | Conversion Truncation | \ref{Conv.vtrunc} |
| Matrix truncation (without conversion) | Dimensionality Reduction | Truncation | \ref{Conv.vtrunc} |
| Matrix truncation promotion | Dimensionality Reduction Promotion | Promotion Truncation | \ref{Conv.vtrunc} |
| Matrix truncation conversion | Dimensionality Reduction Conversion | Conversion Truncation | \ref{Conv.vtrunc} |

If a scalar splat conversion occurs in a conversion sequence where all other
conversions are **Exact Match** rank, the conversion is ranked as
**Extension**. If a scalar splat occurs in a conversion
sequence with a **Promotion** conversion, the conversion is ranked as
**Promotion Extension**. If a scalar splat occurs in a conversion
sequence with a **Conversion** conversion, the conversion is ranked as
**Conversion Extension**.

If a vector truncation conversion occurs in a conversion sequence where all
other conversions are **Exact Match** rank, the conversion is ranked as
**Truncation**. If a vector truncation occurs in a conversion
sequence with a **Promotion** conversion, the conversion is ranked as
**Promotion Truncation**. If a vector truncation occurs in a conversion
sequence with a **Conversion** conversion, the conversion is ranked as
**Conversion Truncation**.

Otherwise, the rank of a conversion sequence is determined by considering the
rank of each conversion.

 Conversion sequence ranks are ordered from better to worse as:

  * **Exact Match**
  * **Extension**
  * **Promotion**
  * **Promotion Extension**
  * **Conversion**
  * **Conversion Extension**
  * **Truncation**
  * **Promotion Truncation**
  * **Conversion Truncation**

**Comparing Implicit Conversion Sequences `[Overload.ICS.Comparing]`**

A partial ordering of implicit conversion sequences exists based on defining
relationships for _better conversion sequence_, and _better conversion_. If an
implicit conversion sequence $ICS(f)$ is a better conversion sequence than
$ICS(f\`)$, then the inverse is also true: $ICS(f\`)$ is a _worse conversion
sequence_ than $ICS(f)$. If $ICS(f)$ is neither better nor worse than
$ICS(f\`)$, the conversion sequences are _indistinguishable conversion
sequences_.

A standard conversion sequence is always better than a user-defined conversion
sequence.

Standard conversion sequences are ordered by their ranks. Two conversion
sequences with the same rank are indistinguishable unless one of the following
rules applies:

  * If class `B` is derived directly or indirectly from class
  `A` and class `C` is derived directly or indirectly from class
  `B`,
    * binding of a expression of type `C` to a cxvalue of type
    `B` is better than binding an expression of type `C` to a
    cxvalue of type `A`,
    * conversion of `C` to `B` is better than conversion or
    `C` to `A`,
    * binding of a expression of type `B` to a cxvalue of type
    `A` is better than binding an expression of type `C` to a
    cxvalue of type `A`,
    * conversion of `B` to `A` is better than conversion of
    `C` to `A`.
