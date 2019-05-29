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

R"name(string)name":实际作用等于string，只是在string很长时括起来加个名字   

常引用：const 类型标识符 &引用名=目标变量名; 例如 const int &ra=a;  
用这种方式声明的引用，不能通过引用对目标变量的值进行修改,从而使引用的目标成为const

mutable 关键字：被mutable修饰的变量，将永远处于可变的状态，即使在一个const函数中。  

## 智能指针
对普通的指针进行封装，使得智能指针实质上是一个对象，行为表现得却像一个指针  
作用：防止忘记调用delete释放内存和程序异常的进入catch块忘记释放内存，可以解决指针释放时机的问题；把值语义转换成引用语义 

头文件 memory 中, 有shared_ptr, unique_ptr, weak_ptr
### shared_ptr    
shared_ptr多个指针指向相同的对象。shared_ptr使用引用计数，每一个shared_ptr的拷贝都指向相同的内存。每使用他一次，内部的引用计数加1，每析构一次，内部的引用计数减1，减为0时，自动删除所指向的堆内存。shared_ptr内部的引用计数是线程安全的，但是对象的读取需要加锁。   
智能指针类将一个计数器与类指向的对象相关联，引用计数跟踪该类有多少个对象共享同一指针。  
use_count()：检查shared_ptr对象的引用计数；这个值是shared_ptr指向的对象的引用次数，即如果两个shared_ptr指向同一对象，这两个shared_ptr.use_count()输出的值相等   


### Something About C Compile
.a:静态库 .so:动态库 .o:目标文件 .out:可执行文件 

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

Internal::IntrusivePrt<Internal::ModuleContents> contents;  

### IntrusivePtr.h
侵入式指针，智能指针。似乎有点东西...

### 初始化函数：Module::Module(name,target):
new了一个contents，contents->name = name; contents->target = target;    




### void append(const Internal::LoweredFunc &function)
contents->functions.push_back(funtion); 
contents->functions是contents指的一个vector，类型为LoweredFunc。这里在这个向量后push进新的function  
 

### ModuleContents
结构体，记录了ref_count, name, auto_shcedule, buffers, functions, submodules, external_code, metadata_name_map  





### LoweredFunc
(string name, std::vector<LoweredArgument> args, Stmt body, LinkageType linkage)

## CodeGen_C -> IRPrinter -> IRVisitor 
Initialize a C code generator pointing at a particular output stream (e.g. a file, or std::cout)    

### CodeGen_C::compile(Module &input)
