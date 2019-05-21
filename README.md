# Running CodeGen_C
在Halide/test下有internal.cpp文件，包含各种测试函数的调用。通过
```
g++ internal.cpp -std=c++11 -I ../src -L ../bin -lHalide -lpthread -ldl -o internal
./internal
```
跑了一遍代码，当然自己只显示xxx test passed

# some knowledge for C++
头文件加入 #ifndef/#define/#endif 防止重复编译出错的问题。  
格式： 
``` 
#ifndef <标识>    
#define <标识>  
......  
#endif  
```
每个头文件的<标示>应该是唯一的，命名规则一般是头文件名全大写，并把文件名中的"."也变成下划线 
```
namespace ns1{
    namespace ns2{

    }
}
```
嵌套的命名空间  

class Rectangle: public Shape   
类的继承    

枚举类型：enum <类型名> {<枚举常量表>}; 

虚函数：    
在基类用virtual声明成员函数为虚函数。在类外定义虚函数时，不必再加virtual    
在派生类中重新定义此函数，要求函数名、函数类型、函数参数个数和类型全部与基类的虚函数相同，并根据派生类的需要重新定义函数体。  
C++11 中的 override 关键字，可以显式的在派生类中声明，哪些成员函数需要被重写，如果没被重写，则编译器会报错。

explicit关键字：防止类构造函数的隐式自动转换

# CodeGen_C::test()
## Argument -> LoweredArgument
LoweredArgument(name,kind,type,dimensions,ArgumentEstimates)

### Kind: {InputScalar,InputBuffer|OutputBuffer}

enum Halide::Argument::Kind
An argument is either a primitive type (for parameters), or a
buffer pointer.

If kind == InputScalar, then type fully encodes the expected type
of the scalar argument.

If kind == InputBuffer|OutputBuffer, then type.bytes() should be used to determine* elem_size of the buffer; additionally, type.code *should* reflect the expected interpretation of the buffer data (e.g. float vs int), but there is no runtime enforcement of this at present.

Argument到底是啥，起什么作用

## Var
implicit:隐式创建时名字前加下划线：'_0','_1'...

## Param
A scalar parameter to a halide pipeline. If you're jitting, this should be bound to an actual value of type T using the set method before you realize the function uses this. If you're statically compiling, this param should appear in the argument list.    

## Expr -> Internal::IRHandle -> IntrusivePtr
A fragment of Halide syntax. It's implemented as reference-counted handle to a concrete expression node, but it's immutable, so you can treat it as a value type.   
似乎都是通过make来赋值  
IRHandle(const IRNode *p)

### IR.h: Add/Cast/Sub ... -> ExprNode -> BaseExprNode -> IRNode
reference count是啥

#### Expr Add::make(Expr a, Expr b)
函数返回值为一个Expr：其实就是一个指向结构体Add的指针，并给结构体Add的成员赋值：a和b为相加的两项（两个Expr),type与a.type相同（也与b.type相同），即int,float...等  

#### Expr Select::make(Expr condition, Expr true_value, Expr false_value)    

不同Expr的具体实现在哪里呢？Add在哪里Add了？Select在哪里Select了？

mutate？    

### Store -> StmtNode -> BaseStmtNode -> IRNode
#### Stmt Store::make()

### Stmt LetStmt::make(name, Expr value, Stmt body)

......

### Variable -> ExprNode
make(type, name, Buffer<>(), Parameter(), ReductionDomain())

## Module
A halide module. This represents IR containing lowered function definitions and buffers. 

Module(const std::string &name, const Target &target);  
Target:目标架构：OS, Arch, 

### LoweredFunc
(string name, std::vector<LoweredArgument> args, Stmt body, LinkageType linkage)

## CodeGen_C -> IRPrinter -> IRVisitor 
Initialize a C code generator pointing at a particular output stream (e.g. a file, or std::cout)    

### CodeGen_C::compile(Module &input)
